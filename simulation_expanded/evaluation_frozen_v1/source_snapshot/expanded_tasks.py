"""Eight explicit, constructed planning/physics task specifications."""
from pathlib import Path
import sys,importlib.util
from copy import deepcopy
import numpy as np
import xml.etree.ElementTree as ET

W=Path(__file__).resolve().parent
REPO=W.parent if (W.parent/'reproduction').is_dir() else W.parents[1]/'analysis_outputs/manuscript_revision_v7_70_20260920/github_publication_v1/atg-repair-planning'
LEGACY=REPO/'simulation'
sys.path.insert(0,str(LEGACY))
import sim_core as core
spec=importlib.util.spec_from_file_location('legacy_execution',LEGACY/'run_experiments.py')
base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)

TITLES={'T01':'Parallel sorting','T02':'Shared inspection','T03':'Synchronized kitting','T04':'Two-stage shared service','T05':'Cooperative transfer','T06':'Two-leg cooperative transfer','T07':'Tray loading and transfer','T08':'Transfer and unloading'}
CONDITIONS={'nominal':{'mass':1.,'friction':1.5,'bias':0.,'time_scale':1.},'heavy':{'mass':5.,'friction':1.5,'bias':0.,'time_scale':1.},'low_friction':{'mass':1.,'friction':.15,'bias':0.,'time_scale':1.},'pose_bias':{'mass':1.,'friction':1.5,'bias':.02,'time_scale':1.},'fast':{'mass':1.,'friction':1.5,'bias':0.,'time_scale':.5}}
ARMS={'L':'left','R':'right'}
ALLOWED={'pick','place','inspect','approach','cooperative_transfer','retreat'}

def make_spec(task,seed,condition='nominal'):
    rng=np.random.default_rng(seed if seed>=0 else 8000-seed)
    cfg=deepcopy(CONDITIONS[condition]);initial={'A':np.array([.45,-.48,.465]),'B':np.array([.45,.48,.465]),'tray':np.array([.40,0,.457])}
    for obj in initial:initial[obj][:2]+=rng.uniform(-.01,.01,2)
    true_initial={k:v.copy() for k,v in initial.items()}
    if task=='T08':
        for obj,sy in [('A',-1),('B',1)]:true_initial[obj]=true_initial['tray']+np.array([0,sy*.115,.041])
    known={k:v.copy() for k,v in true_initial.items()}
    for obj in known:known[obj][:2]+=rng.uniform(-cfg['bias'],cfg['bias'],2)
    goals={};nodes=[];skills={};s0=[];sg=[]
    objects=['tray'] if task in ['T05','T06'] else ['A','B','tray'] if task in ['T07','T08'] else ['A','B']
    def add(nid,action,obj,pre,post,d,arms,res,**skill):
        if action not in ALLOWED:raise ValueError(action)
        nodes.append(base.node(nid,action,obj,pre,post,d*cfg['time_scale'],['both'] if len(arms)==2 else [ARMS[arms[0]]],res))
        skills[nid]={'kind':action,'object':obj,'arms':arms,'duration':d*cfg['time_scale'],**skill}
    if task in ['T01','T02','T03','T04','T07']:
        s0=['A_available','B_available']
        for a,o in [('L','A'),('R','B')]:
            add('pick_'+a,'pick',o,[o+'_available'],[o+'_held'],6,[a],[o],pickup=known[o].tolist())
        for a,o in [('L','A'),('R','B')]:
            pre=[o+'_held']
            if task in ['T02','T04']:
                for j in range(2 if task=='T04' else 1):
                    state=o+'_service'+str(j+1);zone=[.52+(.06 if j else 0),0,.63]
                    add('service'+str(j+1)+'_'+a,'inspect',o,pre,[state],8,[a],[o,'station'],zone=zone,return_point=[known[o][0],known[o][1],.70]);pre=[state]
            if task=='T03':pre=['A_held','B_held']
            target=(initial['tray']+np.array([0,-.115 if a=='L' else .115,.041])).tolist() if task=='T07' else [.65,-.35 if a=='L' else .35,.465]
            res=[o,'slot_'+a] if task=='T07' else [o]
            add('place_'+a,'place',o,pre,[o+'_placed'],6,[a],res,target=target)
            goals[o]=target;sg.append(o+'_placed')
    if task in ['T05','T06','T07','T08']:
        if task!='T07':s0=['tray_available'];barrier=['tray_available']
        else:barrier=['A_placed','B_placed']
        for a in ['L','R']:
            sy=-1 if a=='L' else 1
            add('approach_'+a,'approach','tray',barrier,[a+'_ready'],3,[a],[],target=[known['tray'][0],known['tray'][1]+sy*.23,.65])
        targets=[[.51,0,.457],[.62,0,.457]] if task=='T06' else [[.62,0,.457]]
        pickup=known['tray'].tolist();pre=['L_ready','R_ready']
        for i,target in enumerate(targets):
            nid='transfer'+str(i+1);state='tray_stage'+str(i+1)
            payload=['A','B'] if task in ['T07','T08'] else []
            add(nid,'cooperative_transfer','tray',pre,[state],12,['L','R'],['tray']+(['slot_L','slot_R'] if payload else []),pickup=pickup,target=target,payload=payload)
            pickup=target;pre=[state]
        for a in ['L','R']:
            add('retreat_'+a,'retreat','tray',pre,[a+'_clear'],2,[a],[],target=[.4,-.48 if a=='L' else .48,.85])
        sg.extend(pre+['L_clear','R_clear']);goals['tray']=targets[-1]
        if task in ['T07','T08']:
            for a,o in [('L','A'),('R','B')]:goals[o]=[targets[-1][0],-.115 if a=='L' else .115,.498]
        if task=='T08':
            for a,o in [('L','A'),('R','B')]:
                add('unload_pick_'+a,'pick',o,['L_clear','R_clear'],[o+'_held'],6,[a],[o,'slot_'+a],pickup=goals[o])
                target=[.65,-.35 if a=='L' else .35,.465]
                add('unload_place_'+a,'place',o,[o+'_held'],[o+'_placed'],6,[a],[o],target=target)
                goals[o]=target;sg.append(o+'_placed')
    return {'task':task,'title':TITLES[task],'case':task,'seed':seed,'condition':condition,'parameters':cfg,'graph':{'nodes':nodes,'edges':[]},'initial_states':s0,'goal_states':sg,'objects':objects,'initial_positions':{k:v.tolist() for k,v in true_initial.items() if k in objects},'controller_positions':{k:v.tolist() for k,v in known.items() if k in objects},'target_positions':goals,'skills':skills}

def make_scene(spec):
    root=core.scene();world=root.find('worldbody');cfg=spec['parameters']
    root.find('default/geom').set('friction',f"{cfg['friction']} .02 .001")
    for b in list(world.findall('body')):
        if b.attrib['name'] in ['A','B']:
            o=b.attrib['name']
            if o not in spec['objects']:world.remove(b)
            else:
                b.set('pos',' '.join(map(str,spec['initial_positions'][o])))
                b.find('geom').set('mass',str(.08*cfg['mass']))
    if 'tray' in spec['objects']:
        b=ET.SubElement(world,'body',name='tray',pos=' '.join(map(str,spec['initial_positions']['tray'])))
        ET.SubElement(b,'freejoint',name='tray_free');ET.SubElement(b,'geom',name='tray_board',type='box',size='.085 .27 .016',mass=str(.12*cfg['mass']),rgba='.68 .46 .24 1')
        for a,y in [('L',-.23),('R',.23)]:ET.SubElement(b,'geom',name='handle_'+a,type='box',pos=f'0 {y} .045',size='.025 .018 .03',mass=str(.02*cfg['mass']),rgba='.83 .66 .34 1')
    if spec['task'] in ['T02','T04']:
        ET.SubElement(world,'geom',name='station',type='box',pos='.55 0 .48',size='.10 .08 .04',rgba='.72 .58 .3 1')
        for i,x in enumerate([.52,.58] if spec['task']=='T04' else [.52]):ET.SubElement(world,'site',name='service'+str(i),pos=f'{x} 0 .63',size='.035',type='sphere',rgba='.98 .7 .2 .12')
    for o,p in spec['target_positions'].items():
        size='.095 .285 .001' if o=='tray' else '.05 .05 .001'
        ET.SubElement(world,'geom',type='box',pos=f'{p[0]} {p[1]} .441',size=size,contype='0',conaffinity='0',rgba='.5 .6 .85 .3')
    return root

def waypoints(skill,starts):
    kind=skill['kind'];out={};scale=skill['duration']/({'pick':6,'place':6,'inspect':8,'approach':3,'cooperative_transfer':12,'retreat':2}[kind])
    for a in skill['arms']:
        origin=starts[a];sy=-1 if a=='L' else 1
        if kind=='pick':
            p=np.array(skill['pickup']);p[2]+=.012
            pts=[(0,origin,.04),(1.2,[p[0],p[1],.70],.04),(2.5,p,.04),(3.4,p,.012),(5.3,[p[0],p[1],.75],.012),(6,[p[0],p[1],.75],.012)]
        elif kind=='place':
            p=np.array(skill['target']);p[2]+=.012
            pts=[(0,origin,.012),(1.6,[p[0],p[1],.75],.012),(3,p,.012),(3.5,p,.04),(4.4,p,.04),(6,[p[0],p[1],.80],.04)]
        elif kind=='inspect':
            p=np.array(skill['zone']);p[2]+=.01;q=skill['return_point']
            pts=[(0,origin,.012),(1.3,[origin[0],origin[1],.82],.012),(3,p,.012),(4.4,p,.012),(5.7,[p[0],p[1],.82],.012),(7.5,q,.012),(8,q,.012)]
        elif kind=='approach':pts=[(0,origin,.04),(2.6,skill['target'],.04),(3,skill['target'],.04)]
        elif kind=='retreat':pts=[(0,origin,.04),(2,skill['target'],.04)]
        elif kind=='cooperative_transfer':
            p=np.array(skill['pickup'])+[0,sy*.23,.055];q=np.array(skill['target'])+[0,sy*.23,.055]
            pts=[(0,origin,.04),(1.5,p,.04),(2.5,p,.012),(4.5,[p[0],p[1],.76],.012),(6.6,[q[0],q[1],.76],.012),(8.6,q,.012),(9.2,q,.04),(10.1,q,.04),(12,[q[0],q[1],.80],.04)]
        else:raise ValueError('Unknown primitive '+kind)
        out[a]=[(round(t*scale,8),np.asarray(x,dtype=float).tolist(),g) for t,x,g in pts]
    return out
