"""Reconstruct each action predicate from saved physical states, not passed flags."""
from pathlib import Path
from copy import deepcopy
import argparse,json,itertools
import numpy as np,mujoco
from expanded_tasks import LEGACY,base

def verify_trial(trial,overrides=None):
    trial=Path(trial);overrides=overrides or {}
    spec=deepcopy(overrides.get('input',json.loads((trial/'input.json').read_text())))
    plan=deepcopy(overrides.get('planning',json.loads((trial/'planning.json').read_text())))
    events=deepcopy(overrides.get('events',json.loads((trial/'events.json').read_text())))
    summary=json.loads((trial/'summary.json').read_text())
    with np.load(trial/'trajectory.npz') as z:trace={k:z[k].copy() for k in z.files}
    trace.update(overrides.get('trajectory',{}))
    assets=LEGACY/'assets/franka_local';m=mujoco.MjModel.from_xml_string((trial/'scene.xml').read_text(),{p.name:p.read_bytes() for p in assets.glob('*.stl')});d=mujoco.MjData(m)
    frames=[];maxdiff=0.;cross=station=0
    for i,(q,v,c,t) in enumerate(zip(trace['qpos'],trace['qvel'],trace['ctrl'],trace['t'])):
        d.qpos[:]=q;d.qvel[:]=v;d.ctrl[:]=c;mujoco.mj_forward(m,d)
        positions={o:d.body(o).xpos.copy() for o in spec['objects']}
        speeds={o:float(np.linalg.norm(d.joint(o+'_free').qvel[:3])) for o in spec['objects']}
        grip={a:d.site(a+'_grip').xpos.copy() for a in ['L','R']};fingers={a:[float(d.joint(a+'_panda_finger_joint'+str(j)).qpos[0]) for j in [1,2]] for a in ['L','R']}
        touch={o:{a:set() for a in ['L','R']} for o in spec['objects']}
        for cc in d.contact:
            a=m.body(int(m.geom_bodyid[cc.geom1])).name;b=m.body(int(m.geom_bodyid[cc.geom2])).name
            if a.startswith('L_') and b.startswith('R_') or a.startswith('R_') and b.startswith('L_'):cross+=int(cc.dist<-.001)
            for obj,body in [(a,b),(b,a)]:
                if obj in touch and body.startswith(('L_','R_')) and body.endswith(('leftfinger','rightfinger')) and cc.dist<=.001:touch[obj][body[0]].add(body.rsplit('_',1)[-1])
        if spec['task'] in ['T02','T04']:station+=int(sum(np.linalg.norm(positions[o][:2]-[.55,0])<.075 and .58<positions[o][2]<.68 for o in ['A','B'])>1)
        for j,o in enumerate(spec['objects']):maxdiff=max(maxdiff,float(np.linalg.norm(positions[o]-trace['object_positions'][i,j])))
        frames.append({'t':float(t),'positions':positions,'speeds':speeds,'grip':grip,'fingers':fingers,'touch':touch})
    integrity=[];physical=[];outcomes=[];starts={};ends={};states=set(spec['initial_states']);nodes={n['id']:n for n in plan['graph']['nodes']};items={i['node_id']:i for i in plan['schedule']['items']}
    if maxdiff>1e-6:integrity.append('pose_snapshot_mismatch')
    if len(trace['t'])!=len(trace['qpos']) or np.any(np.diff(trace['t'])<=0):integrity.append('invalid_trace_time')
    context={'S0':spec['initial_states'],'Sg':spec['goal_states']}
    audit=base.audit_schedule(plan['graph'],plan['schedule'],context)
    if not audit['valid']:integrity.append('invalid_planned_schedule')
    for e in events:
        nid=e['node'];sk=spec['skills'][nid];item=items[nid];f=frames[e['snapshot']]
        if abs(f['t']-e['time'])>1e-7:integrity.append(nid+':event_snapshot_time')
        if e['event']=='start':
            starts[nid]=e
            if not set(nodes[nid]['pre_state'])<=states:physical.append(nid+':missing_observed_precondition')
            if set(e['units'])!=set(item['executors']) or set(e['resources'])!=set(item['resources']):integrity.append(nid+':dispatch_allocation')
            if abs(e['time']-item['start'])>1e-8:integrity.append(nid+':dispatch_time')
            continue
        if e['event']!='finish':continue
        ends[nid]=e;k=sk['kind'];o=sk['object'];a=sk['arms'][0];xyz=f['positions'][o];reason=[];metrics={}
        if nid not in starts:integrity.append(nid+':finish_without_start');continue
        if abs(e['time']-item['finish'])>1e-8 or e['time']<=starts[nid]['time']:integrity.append(nid+':finish_time')
        if k=='pick':
            if xyz[2]<=.62:reason.append('lift_height')
            if np.linalg.norm(xyz-f['grip'][a])>=.06:reason.append('grip_separation')
            if len(f['touch'][o][a])!=2:reason.append('bilateral_fingers')
        elif k in ['place','cooperative_transfer']:
            if np.linalg.norm(xyz-sk['target'])>=.03:reason.append('target_position')
            if f['speeds'][o]>=.04:reason.append('object_speed')
            if any(min(f['fingers'][aa])<=.03 for aa in sk['arms']):reason.append('release_opening')
        elif k=='inspect':
            dwell=0.
            for j in range(1,len(frames)):
                previous=frames[j-1];current=frames[j]
                if previous['t']<starts[nid]['time']-1e-8 or current['t']>e['time']+1e-8:continue
                p=previous['positions'][o]
                if np.linalg.norm(p[:2]-np.array(sk['zone'])[:2])<.035 and abs(p[2]-sk['zone'][2])<.04:dwell+=current['t']-previous['t']
            metrics['sampled_dwell_s']=dwell
            if dwell<.5:reason.append('service_dwell')
        elif k in ['approach','retreat']:
            metrics['grip_target_error_m']=float(np.linalg.norm(f['grip'][a]-sk['target']))
            if metrics['grip_target_error_m']>=.02:reason.append('grip_target')
            if min(f['fingers'][a])<=.03:reason.append('gripper_not_open')
            if k=='retreat' and np.linalg.norm(f['grip'][a]-xyz)<=.10:reason.append('retreat_clearance')
        else:reason.append('unsupported_primitive')
        if k=='cooperative_transfer':
            subset=[fr for fr in frames if starts[nid]['time']+.30*sk['duration']<=fr['t']<starts[nid]['time']+.68*sk['duration']]
            n=sum(all(len(fr['touch']['tray'][aa])==2 for aa in ['L','R']) for fr in subset)
            ratio=n/len(subset) if subset else 0.;metrics.update(sampled_carry_frames=len(subset),sampled_bilateral_carry_fraction=ratio)
            if ratio<=.9:reason.append('carry_finger_contact')
        passed=not reason
        if passed:states.update(nodes[nid]['post_state'])
        else:physical.extend(nid+':'+s for s in reason)
        if passed!=e['passed']:integrity.append(nid+':reported_pass_flag_disagrees')
        outcomes.append({'node':nid,'reconstructed_pass':passed,'reasons':reason,**metrics})
    for a,b in itertools.combinations(starts,2):
        ea=ends.get(a,{'time':summary['simulation_end_s']})['time'];eb=ends.get(b,{'time':summary['simulation_end_s']})['time']
        if max(starts[a]['time'],starts[b]['time'])<min(ea,eb)-1e-8 and (set(starts[a]['units'])&set(starts[b]['units']) or set(starts[a]['resources'])&set(starts[b]['resources'])):integrity.append('overlapping_dispatch_capacity')
    for edge in plan['graph']['edges']:
        u,v=edge['source'],edge['target']
        if v in starts and (u not in ends or ends[u]['time']>starts[v]['time']+1e-8):physical.append('precedence_violation')
    final=frames[-1];errors={o:float(np.linalg.norm(final['positions'][o]-spec['target_positions'][o])) for o in spec['objects']}
    if any(v>=.03 for v in errors.values()):physical.append('final_position')
    if any(v>=.02 for v in final['speeds'].values()):physical.append('final_speed')
    if set(ends)!=set(nodes):physical.append('incomplete_execution')
    if not set(spec['goal_states'])<=states:physical.append('goal_not_observed')
    if cross or summary['interarm_penetration_steps']:physical.append('interarm_penetration')
    if station or summary['station_overlap_steps']:physical.append('station_occupancy')
    if summary['physics_warnings']:physical.append('physics_warning')
    for o,v in errors.items():
        if abs(v-summary['goal_errors_m'][o])>1e-6:integrity.append('final_error_mismatch')
    success=not physical and not integrity
    return {'trial':trial.name,'task':spec['task'],'seed':spec['seed'],'condition':spec['condition'],'mode':summary['mode'],'execution_success':success,'online_success':summary['execution_success'],'outcome_agreement':success==summary['execution_success'],'integrity_valid':not integrity,'integrity_issues':integrity,'physical_failure_reasons':physical,'reconstructed_goal_errors_m':errors,'sampled_interarm_contacts':cross,'sampled_station_overlap':station,'actions':outcomes,'maximum_pose_reconstruction_difference_m':maxdiff}

def main():
    p=argparse.ArgumentParser();p.add_argument('directory');a=p.parse_args();root=Path(a.directory);results=[]
    for trial in sorted(root.glob('T*_*_*_*')):
        if (trial/'summary.json').exists():results.append(verify_trial(trial))
    report={'total':len(results),'execution_successes':sum(r['execution_success'] for r in results),'integrity_valid':sum(r['integrity_valid'] for r in results),'outcome_agreement':sum(r['outcome_agreement'] for r in results),'scope':'Exact event-state reconstruction of every primitive including retreat; 40ms sampled service/contact checks; online 2ms counters are additionally retained, not independently certified as continuous collision safety.','records':results}
    dest=root/'independent_verification.json';assert not dest.exists(),dest;dest.write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='records'}));print(json.dumps([(r['trial'],r['integrity_issues']) for r in results if not r['integrity_valid']]))

if __name__=='__main__':main()
