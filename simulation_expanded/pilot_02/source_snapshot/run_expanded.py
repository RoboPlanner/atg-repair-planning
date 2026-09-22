"""Run actual physics and preserve exact event snapshots, including failures."""
from pathlib import Path
from copy import deepcopy
import argparse,hashlib,json,time,platform,concurrent.futures
import xml.etree.ElementTree as ET
import numpy as np,mujoco
from expanded_tasks import W,REPO,LEGACY,base,core,make_spec,make_scene,waypoints,TITLES,CONDITIONS,ALLOWED

DT=.002;SAMPLE=20
base.TITLES.update(TITLES)

def contacts(m,d,objects):
    touches={o:{a:set() for a in ['L','R']} for o in objects};cross=0
    for c in d.contact:
        a=m.body(int(m.geom_bodyid[c.geom1])).name;b=m.body(int(m.geom_bodyid[c.geom2])).name
        if a.startswith('L_') and b.startswith('R_') or a.startswith('R_') and b.startswith('L_'):
            cross+=int(c.dist<-.001)
        for obj,finger in [(a,b),(b,a)]:
            if obj in touches and finger.startswith(('L_','R_')) and finger.endswith(('leftfinger','rightfinger')) and c.dist<=.001:
                touches[obj][finger[0]].add('left' if finger.endswith('leftfinger') else 'right')
    return touches,cross

def condition(m,d,skill,dwell):
    """Online physical predicates; no permissive fallthrough."""
    k=skill['kind'];o=skill['object'];xyz=d.body(o).xpos.copy();speed=float(np.linalg.norm(d.joint(o+'_free').qvel[:3]));arms=skill['arms']
    touch,_=contacts(m,d,[o]);detail={'position':xyz.tolist(),'speed':speed}
    if k=='pick':
        a=arms[0];detail.update(height=float(xyz[2]),grip_distance=float(np.linalg.norm(xyz-d.site(a+'_grip').xpos)),bilateral_fingers=len(touch[o][a])==2)
        ok=xyz[2]>.62 and detail['grip_distance']<.06 and detail['bilateral_fingers']
    elif k in ['place','cooperative_transfer']:
        detail['target_error']=float(np.linalg.norm(xyz-skill['target']));detail['open']=all(d.joint(a+'_panda_finger_joint1').qpos[0]>.03 and d.joint(a+'_panda_finger_joint2').qpos[0]>.03 for a in arms)
        ok=detail['target_error']<.03 and speed<.04 and detail['open']
    elif k=='inspect':detail['dwell']=dwell;ok=dwell>=.5
    elif k in ['approach','retreat']:
        a=arms[0];detail['grip_error']=float(np.linalg.norm(d.site(a+'_grip').xpos-skill['target']));detail['open']=all(d.joint(a+'_panda_finger_joint'+str(i)).qpos[0]>.03 for i in [1,2])
        detail['object_clearance']=float(np.linalg.norm(d.site(a+'_grip').xpos-xyz))
        ok=detail['grip_error']<.02 and detail['open'] and (k!='retreat' or detail['object_clearance']>.10)
    else:raise ValueError('Unsupported action '+k)
    return bool(ok),detail

def execute(task,seed,mode,condition_name,out,record=False):
    out=Path(out);out.mkdir(parents=True,exist_ok=False);spec=make_spec(task,seed,condition_name);plan=base.planning(spec,mode);root=make_scene(spec)
    (out/'input.json').write_text(json.dumps(spec,indent=2),encoding='utf-8');(out/'planning.json').write_text(json.dumps(plan,indent=2),encoding='utf-8');(out/'scene.xml').write_bytes(ET.tostring(root,encoding='utf-8'))
    m,d=core.setup(root)
    for _ in range(200):mujoco.mj_step(m,d)
    d.time=0.;mujoco.mj_forward(m,d)
    nodes={n['id']:n for n in plan['graph']['nodes']};items=plan['schedule']['items'];horizon=plan['schedule']['estimated_makespan']
    active={};finished=set();states=set(spec['initial_states']);events=[];fail=[];abort=None;dwells={n:0. for n,s in spec['skills'].items() if s['kind']=='inspect'}
    carries={n:{'steps':0,'bilateral_steps':0} for n,s in spec['skills'].items() if s['kind']=='cooperative_transfer'}
    cross_steps=station_steps=0;max_ik=0.;snapshot=[];qt=[];vt=[];ct=[];tt=[];poses=[];finger_flags=[]
    holds={a:d.site(a+'_grip').xpos.copy() for a in ['L','R']};opening={'L':.04,'R':.04};control_trace=[]
    recorder=base.Recorder(m,out/'execution.mp4',spec,mode,plan) if record else None
    def capture(t):
        if tt and abs(tt[-1]-t)<1e-9:return len(tt)-1
        touch,_=contacts(m,d,spec['objects']);qt.append(d.qpos.copy());vt.append(d.qvel.copy());ct.append(d.ctrl.copy());tt.append(t)
        poses.append([d.body(o).xpos.copy() for o in spec['objects']]);finger_flags.append([[int(len(touch[o][a])==2) for a in ['L','R']] for o in spec['objects']]);return len(tt)-1
    capture(0.)
    for step in range(round((horizon+.5)/DT)+1):
        t=round(step*DT,8)
        if abort is not None and t>abort+.5:break
        for nid,rt in list(active.items()):
            item=rt['item'];skill=spec['skills'][nid]
            if t+1e-8>=item['finish']:
                ok,detail=condition(m,d,skill,dwells.get(nid,0.));idx=capture(t)
                if nid in carries:
                    c=carries[nid];ratio=c['bilateral_steps']/max(1,c['steps']);detail['bilateral_carry_fraction']=ratio
                    if ratio<=.9:ok=False;detail['carry_contact_failed']=True
                events.append({'event':'finish','node':nid,'time':t,'snapshot':idx,'passed':ok,'physical_observation':detail})
                if ok:states.update(nodes[nid]['post_state'])
                else:fail.append(nid+': physical postcondition');abort=t if abort is None else abort
                for a in rt['points']:holds[a]=np.array(rt['points'][a][-1][1]);opening[a]=rt['points'][a][-1][2]
                finished.add(nid);del active[nid]
        for item in items:
            nid=item['node_id']
            if abort is None and nid not in active and nid not in finished and abs(t-item['start'])<DT/2:
                missing=set(nodes[nid]['pre_state'])-states
                if missing:fail.append(nid+': observed prerequisites missing');abort=t;continue
                points=waypoints(spec['skills'][nid],{a:d.site(a+'_grip').xpos.copy() for a in ['L','R']})
                active[nid]={'item':item,'points':points}
                events.append({'event':'start','node':nid,'time':t,'snapshot':capture(t),'units':item['executors'],'resources':item['resources']})
        if abort is not None and active:
            for nid,rt in active.items():events.append({'event':'aborted','node':nid,'time':t,'snapshot':capture(t)})
            active.clear()
            for a in ['L','R']:holds[a]=d.site(a+'_grip').xpos.copy();opening[a]=float(d.joint(a+'_panda_finger_joint1').qpos[0])
        if step%10==0:
            targets={a:(holds[a],opening[a]) for a in ['L','R']}
            for rt in active.values():
                for a,pts in rt['points'].items():targets[a]=base.interpolate(pts,t-rt['item']['start'])
            for a,(xyz,g) in targets.items():
                q,err=core.ik(m,d,a,xyz);max_ik=max(max_ik,err)
                for j,value in enumerate(q,1):d.ctrl[m.actuator(a+'_a'+str(j)).id]=value
                for j in [1,2]:d.ctrl[m.actuator(a+'_finger'+str(j)).id]=g
        if step%SAMPLE==0:capture(t)
        if recorder and step%20==0:recorder.frame(d,t,[rt['item'] for rt in active.values()],'Execution stopped' if abort is not None else '')
        if t>=horizon+.5:break
        mujoco.mj_step(m,d);mujoco.mj_forward(m,d)
        touch,cross=contacts(m,d,spec['objects']);cross_steps+=int(cross>0)
        if spec['task'] in ['T02','T04']:
            count=sum(np.linalg.norm(d.body(o).xpos[:2]-[.55,0])<.075 and .58<d.body(o).xpos[2]<.68 for o in ['A','B']);station_steps+=int(count>1)
        for nid,rt in active.items():
            sk=spec['skills'][nid];x=d.body(sk['object']).xpos
            if sk['kind']=='inspect' and np.linalg.norm(x[:2]-np.array(sk['zone'])[:2])<.035 and abs(x[2]-sk['zone'][2])<.04:dwells[nid]+=DT
            if nid in carries and .30*sk['duration']<=t-rt['item']['start']<.68*sk['duration']:
                carries[nid]['steps']+=1;carries[nid]['bilateral_steps']+=int(all(len(touch['tray'][a])==2 for a in ['L','R']))
    if recorder:recorder.close()
    capture(round(float(d.time),8))
    errors={o:float(np.linalg.norm(d.body(o).xpos-spec['target_positions'][o])) for o in spec['objects']};speeds={o:float(np.linalg.norm(d.joint(o+'_free').qvel[:3])) for o in spec['objects']}
    warnings=sum(int(w.number) for w in d.warning)
    if any(e>=.03 for e in errors.values()):fail.append('final position')
    if any(v>=.02 for v in speeds.values()):fail.append('final speed')
    if cross_steps:fail.append('inter-arm penetration')
    if station_steps:fail.append('station occupancy')
    if warnings:fail.append('physics warnings')
    if len(finished)!=len(nodes):fail.append('incomplete execution')
    if not set(spec['goal_states'])<=states:fail.append('goal state not observed')
    success=not fail
    result={'task':task,'seed':seed,'condition':condition_name,'mode':mode,'nodes':len(nodes),'cooperative_nodes':sum(n['mode']=='cooperative' for n in nodes.values()),'graph_accepted':plan['accepted'],'execution_success':success,'scheduled_window_s':horizon,'completed_schedule_s':horizon if success else None,'simulation_end_s':float(d.time),'abort_s':abort,'failure_reasons':fail,'goal_errors_m':errors,'object_speeds_m_s':speeds,'finished_tasks':sorted(finished),'states':sorted(states),'service_dwell_s':dwells,'carry_contacts':carries,'interarm_penetration_steps':cross_steps,'station_overlap_steps':station_steps,'physics_warnings':warnings,'maximum_ik_residual':max_ik,'recorded':record,'mujoco_version':mujoco.__version__,'python_version':platform.python_version()}
    (out/'summary.json').write_text(json.dumps(result,indent=2),encoding='utf-8');(out/'events.json').write_text(json.dumps(events,indent=2),encoding='utf-8')
    np.savez_compressed(out/'trajectory.npz',qpos=qt,qvel=vt,ctrl=ct,t=tt,object_positions=poses,bilateral_fingers=finger_flags)
    return result

def worker(args):return execute(*args)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--pilot',action='store_true');p.add_argument('--tasks',default=','.join(TITLES));p.add_argument('--seeds',default='100,101,102,103,104');p.add_argument('--conditions',default=','.join(CONDITIONS));p.add_argument('--workers',type=int,default=4);p.add_argument('--videos',action='store_true');a=p.parse_args()
    out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=False);tasks=a.tasks.split(',');seeds=[int(x) for x in a.seeds.split(',')];conditions=a.conditions.split(',')
    jobs=[]
    for task in tasks:
        for seed in seeds:
            for condition_name in conditions:
                for mode in (['full','serial'] if condition_name=='nominal' else ['full']):
                    name=f'{task}_{seed}_{condition_name}_{mode}'
                    record=a.videos and seed==100 and (condition_name=='nominal' or task=='T08')
                    jobs.append((task,seed,mode,condition_name,str(out/name),record))
    protocol={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'development':a.pilot,'tasks':tasks,'seeds':seeds,'conditions':conditions,'runs':len(jobs),'video_selection':'All nominal methods at seed 100, plus all four T08 stress conditions at seed 100; fixed before evaluation.','parameters':CONDITIONS,'sampling':'40 ms plus every exact action start/finish; online contact/collision counts at 2 ms','source_sha256':{q.name:hashlib.sha256(q.read_bytes()).hexdigest() for q in [Path(__file__),W/'expanded_tasks.py',LEGACY/'sim_core.py',LEGACY/'run_experiments.py']},'jobs':[{'task':j[0],'seed':j[1],'mode':j[2],'condition':j[3],'record':j[5]} for j in jobs]}
    (out/'protocol_frozen_before_runs.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    source=out/'source_snapshot';source.mkdir()
    for q in [Path(__file__),W/'expanded_tasks.py']:(source/q.name).write_bytes(q.read_bytes())
    results=[]
    with concurrent.futures.ProcessPoolExecutor(max_workers=a.workers) as pool:
        futures={pool.submit(worker,j):j for j in jobs}
        for f in concurrent.futures.as_completed(futures):
            j=futures[f]
            try:r=f.result()
            except Exception as e:
                r={'task':j[0],'seed':j[1],'mode':j[2],'condition':j[3],'runtime_error':repr(e),'execution_success':False}
                Path(j[4]).mkdir(exist_ok=True);(Path(j[4])/'runtime_error.json').write_text(json.dumps(r,indent=2))
            results.append(r);results.sort(key=lambda x:(x['task'],x['seed'],x['condition'],x['mode']));(out/'summaries.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
            print(json.dumps({'progress':len(results),'total':len(jobs),'task':j[0],'seed':j[1],'mode':j[2],'condition':j[3],'success':r['execution_success'],'issues':r.get('failure_reasons',r.get('runtime_error'))}),flush=True)

if __name__=='__main__':main()
