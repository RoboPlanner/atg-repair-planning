"""Adversarial record checks; never modify the archived input files."""
from pathlib import Path
from copy import deepcopy
import argparse,json
import numpy as np,mujoco
from verify_expanded import verify_trial
from expanded_tasks import LEGACY

def main():
    p=argparse.ArgumentParser();p.add_argument('pilot');a=p.parse_args();root=Path(a.pilot);rows=[]
    coop=root/'T05_-11_nominal_full';single=root/'T01_-11_nominal_full';shared=root/'T02_-11_nominal_full'
    def load(trial):
        with np.load(trial/'trajectory.npz') as z:t={k:z[k].copy() for k in z.files}
        e=json.loads((trial/'events.json').read_text());s=json.loads((trial/'input.json').read_text());g=json.loads((trial/'planning.json').read_text())
        assets=LEGACY/'assets/franka_local';m=mujoco.MjModel.from_xml_string((trial/'scene.xml').read_text(),{p.name:p.read_bytes() for p in assets.glob('*.stl')})
        return t,e,s,g,m
    def check(name,trial,overrides=None,expect=True,required=None):
        r=verify_trial(trial,overrides);assert r['execution_success']==expect,(name,r)
        if required:assert any(required in v for v in r['physical_failure_reasons']+r['integrity_issues']),(name,r)
        rows.append({'test':name,'passed':True,'observed_execution_verdict':r['execution_success'],'issues':r['physical_failure_reasons']+r['integrity_issues']})
    check('Nominal original record',coop)
    t,e,s,g,m=load(coop);idx=next(x['snapshot'] for x in e if x['event']=='finish' and x['node']=='retreat_L')
    for j in range(1,8):t['qpos'][idx,m.jnt_qposadr[m.joint('L_panda_joint'+str(j)).id]]=t['qpos'][0,m.jnt_qposadr[m.joint('L_panda_joint'+str(j)).id]]
    check('Fake passed retreat with arm away from target',coop,{'trajectory':t},False,'retreat_L:grip_target')
    t,e,s,g,m=load(single);idx=next(x['snapshot'] for x in e if x['event']=='finish' and x['node']=='pick_L');adr=m.jnt_qposadr[m.joint('A_free').id];t['qpos'][idx,adr+2]=.465;t['object_positions'][idx,s['objects'].index('A'),2]=.465
    check('Fake passed pick with object remaining low',single,{'trajectory':t},False,'pick_L:lift_height')
    t,e,s,g,m=load(single);idx=next(x['snapshot'] for x in e if x['event']=='finish' and x['node']=='place_L');adr=m.jnt_qposadr[m.joint('A_free').id];t['qpos'][idx,adr]+=.10;t['object_positions'][idx,s['objects'].index('A'),0]+=.10
    check('Fake passed place off target',single,{'trajectory':t},False,'place_L:target_position')
    t,e,s,g,m=load(shared);lo=next(x['time'] for x in e if x['event']=='start' and x['node']=='service1_L');hi=next(x['time'] for x in e if x['event']=='finish' and x['node']=='service1_L');adr=m.jnt_qposadr[m.joint('A_free').id]
    ids=np.flatnonzero((t['t']>=lo)&(t['t']<=hi));t['qpos'][ids,adr]=.1;t['object_positions'][ids,s['objects'].index('A'),0]=.1
    check('Fake service dwell',shared,{'trajectory':t},False,'service1_L:service_dwell')
    t,e,s,g,m=load(coop);s['skills']['retreat_L']['kind']='unrecognized'
    check('Unsupported primitive is not accepted',coop,{'input':s},False,'unsupported_primitive')
    t,e,s,g,m=load(coop);next(x for x in g['schedule']['items'] if x['node_id']=='transfer1')['executors']=['left']
    check('B allocated only one execution unit',coop,{'planning':g},False,'invalid_planned_schedule')
    t,e,s,g,m=load(coop);next(x for x in e if x['event']=='finish')['snapshot']=0
    check('Forged event-state alignment',coop,{'events':e},False,'event_snapshot_time')
    t,e,s,g,m=load(single);adr=m.jnt_dofadr[m.joint('A_free').id];t['qvel'][-1,adr]=.2
    check('Moving object at final goal',single,{'trajectory':t},False,'final_speed')
    dest=root/'verifier_regressions.json';assert not dest.exists();dest.write_text(json.dumps({'passed':len(rows),'total':len(rows),'tests':rows},indent=2),encoding='utf-8');print(json.dumps({'passed':len(rows),'total':len(rows)}))

if __name__=='__main__':main()
