"""Reconstruct body poses from saved generalized coordinates and check event logs."""
from pathlib import Path
import argparse,hashlib,json,itertools
import numpy as np,mujoco

def verify(directory):
    records=[];assets=Path(__file__).parent/'assets/franka_local'
    for trial in sorted(directory.glob('*_*_*')):
        if not trial.is_dir() or not (trial/'summary.json').exists():continue
        spec=json.loads((trial/'input.json').read_text());summary=json.loads((trial/'summary.json').read_text())
        plan=json.loads((trial/'planning.json').read_text());events=json.loads((trial/'events.json').read_text())
        trace=np.load(trial/'trajectory.npz');samples=[json.loads(s) for s in (trial/'states.jsonl').read_text().splitlines()]
        m=mujoco.MjModel.from_xml_string((trial/'scene.xml').read_text(),{p.name:p.read_bytes() for p in assets.glob('*.stl')});d=mujoco.MjData(m)
        observed_errors={};max_reconstruction=0.;station_steps=0;carried=0;both=0;dwell={'A':0.,'B':0.}
        items={s['node_id']:s for s in plan['schedule']['items']}
        for q,t,sample in zip(trace['qpos'],trace['t'],samples):
            d.qpos[:]=q;mujoco.mj_forward(m,d)
            for name,position in sample['objects'].items():max_reconstruction=max(max_reconstruction,float(np.linalg.norm(d.body(name).xpos-position)))
            if spec['case']=='shared':
                count=0
                for obj in ['A','B']:
                    xyz=d.body(obj).xpos
                    if np.linalg.norm(xyz[:2]-[.52,0])<.035 and .58<xyz[2]<.66:count+=1;dwell[obj]+=.04
                station_steps+=int(count>1)
            if spec['case']=='cooperative' and items['transfer']['start']+2.5<=t<items['transfer']['start']+8.6:
                carried+=1;arms=set()
                for c in d.contact:
                    a=m.body(int(m.geom_bodyid[c.geom1])).name;b=m.body(int(m.geom_bodyid[c.geom2])).name
                    if a=='tray' and b.startswith(('L_','R_')):arms.add(b[0])
                    if b=='tray' and a.startswith(('L_','R_')):arms.add(a[0])
                both+=int(arms=={'L','R'})
        for name,target in spec['target_positions'].items():
            if (spec['case']=='cooperative')!=(name=='tray'):continue
            observed_errors[name]=float(np.linalg.norm(d.body(name).xpos-target))
        starts={e['node']:e for e in events if e['event']=='start'};ends={e['node']:e for e in events if e['event']=='finish'}
        issues=[]
        if set(starts)!=set(items) or set(ends)!=set(items):issues.append('Incomplete execution')
        for nid,s in items.items():
            if nid not in starts or nid not in ends:continue
            if abs(starts[nid]['time']-s['start'])>1e-8 or abs(ends[nid]['time']-s['finish'])>1e-8:issues.append('Dispatch interval mismatch '+nid)
            if ends[nid]['time']<=starts[nid]['time'] or not ends[nid]['passed']:issues.append('Task completion failed '+nid)
        for a,b in itertools.combinations(starts,2):
            overlap=max(starts[a]['time'],starts[b]['time'])<min(ends[a]['time'],ends[b]['time'])-1e-8
            if overlap and (set(starts[a]['units'])&set(starts[b]['units']) or set(starts[a]['resources'])&set(starts[b]['resources'])):issues.append('Capacity conflict')
        for edge in plan['graph']['edges']:
            if ends[edge['source']]['time']>starts[edge['target']]['time']+1e-8:issues.append('Relation precedence violation')
        if max_reconstruction>1e-4:issues.append('Pose log inconsistent with generalized coordinates')
        if any(e>=.03 for e in observed_errors.values()):issues.append('Final object goal failed')
        if any(abs(observed_errors[k]-v)>1e-5 for k,v in summary['goal_errors_m'].items()):issues.append('Reported goal error mismatch')
        if station_steps:issues.append('Observed station overlap')
        if spec['case']=='shared' and min(dwell.values())<.5:issues.append('Insufficient station dwell')
        if carried and both/carried<=.9:issues.append('Insufficient dual contact in saved trajectory')
        records.append({'trial':trial.name,'valid':not issues,'issues':issues,'reconstructed_goal_errors_m':observed_errors,'maximum_pose_reconstruction_difference_m':max_reconstruction,'sampled_station_overlap':station_steps,'sampled_station_dwell_s':dwell,'sampled_dual_contact_fraction':both/carried if carried else None})
    assert len(records)==30,len(records)
    output={'records':records,'passed':sum(r['valid'] for r in records),'total':len(records),'sampling_interval_s':.04,'scope':'Independent event/capacity checks and forward-kinematics reconstruction of stored physical states; contact/dwell recheck is sampled, not continuous collision certification.'}
    (directory/'independent_verification.json').write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps({'passed':output['passed'],'total':len(records),'issues':[(r['trial'],r['issues']) for r in records if not r['valid']]}))
    return output

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('directory');args=ap.parse_args();verify(Path(args.directory))
