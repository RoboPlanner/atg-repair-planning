"""Actual MuJoCo executions of accepted ATG schedules with fixed contact-grasp skills.

Object poses are never reset after initialization. No weld or attachment constraints
are used. A prescribed operational-space path is tracked by position actuators.
"""
from pathlib import Path
from copy import deepcopy
import argparse, csv, hashlib, json, math, os, platform, shutil, subprocess, sys, time
import xml.etree.ElementTree as ET
import numpy as np
import mujoco
from PIL import Image, ImageDraw, ImageFont
from sim_core import W, scene, setup, ik

PROJECT = W.parents[1]
REPO = W.parent if (W.parent/'reproduction').is_dir() else PROJECT/'analysis_outputs/manuscript_revision_v7_70_20260920/github_publication_v1/atg-repair-planning'
REP = REPO/'reproduction'
sys.path.insert(0, str(REP/'implementation_v7_70'))
sys.path.insert(0, str(REP))
from atomic_task.pipeline import run_verified_atg
from independent_audit import audit_graph, audit_schedule

DT = .002
FPS = 25
CONTROL_STEPS = 10
COLORS = {'L':'#477eb6','R':'#359982','B':'#9669b7'}
TITLES = {'parallel':'Parallel sorting','shared':'Shared inspection station','cooperative':'Cooperative tray transfer'}

def node(nid, action, obj, pre, post, duration, arms, resources):
    return dict(id=nid,action=action,object=obj,pre_state=pre,post_state=post,duration=duration,
                resource=resources,candidate_arm=arms,mode='cooperative' if arms==['both'] else 'single')

def specification(case, seed):
    rng=np.random.default_rng(seed if seed>=0 else 1900-seed)
    initial={'A':[.45+float(rng.uniform(-.01,.01)),-.48+float(rng.uniform(-.01,.01)),.47],
             'B':[.45+float(rng.uniform(-.01,.01)),.48+float(rng.uniform(-.01,.01)),.47],
             'tray':[.40+float(rng.uniform(-.01,.01)),float(rng.uniform(-.01,.01)),.457]}
    targets={'A':[.65,-.35,.465],'B':[.65,.35,.465],'tray':[.62,0,.457]}
    n=[]
    if case=='cooperative':
        for arm in ['L','R']:
            n.append(node('approach_'+arm,'approach','tray',['tray_available'],[arm+'_ready'],3,[{'L':'left','R':'right'}[arm]],[]))
        n.append(node('transfer','cooperative_transfer','tray',['L_ready','R_ready'],['tray_placed'],12,['both'],['tray']))
        for arm in ['L','R']:
            n.append(node('retreat_'+arm,'retreat','tray',['tray_placed'],[arm+'_clear'],2,[{'L':'left','R':'right'}[arm]],[]))
        s0=['tray_available'];sg=['tray_placed','L_clear','R_clear']
    else:
        for arm,obj in [('L','A'),('R','B')]:
            a=[{'L':'left','R':'right'}[arm]]
            n.append(node('pick_'+arm,'pick',obj,[obj+'_available'],[obj+'_held'],6,a,[obj]))
            if case=='shared':
                n.append(node('inspect_'+arm,'inspect',obj,[obj+'_held'],[obj+'_inspected'],8,a,[obj,'station']))
            n.append(node('place_'+arm,'place',obj,[obj+'_inspected' if case=='shared' else obj+'_held'],[obj+'_placed'],6,a,[obj]))
        s0=['A_available','B_available'];sg=['A_placed','B_placed']
    return dict(case=case,seed=seed,initial_states=s0,goal_states=sg,graph={'nodes':n,'edges':[]},initial_positions=initial,target_positions=targets)

def make_scene(spec):
    root=scene();world=root.find('worldbody')
    for b in list(world.findall('body')):
        if b.attrib['name'] in ['A','B']:
            if spec['case']=='cooperative':world.remove(b)
            else:b.set('pos',' '.join(map(str,spec['initial_positions'][b.attrib['name']])))
    if spec['case']=='cooperative':
        b=ET.SubElement(world,'body',name='tray',pos=' '.join(map(str,spec['initial_positions']['tray'])))
        ET.SubElement(b,'freejoint',name='tray_free')
        ET.SubElement(b,'geom',name='tray_board',type='box',size='.085 .27 .016',mass='.12',rgba='.68 .46 .24 1')
        for side,y in [('L',-.23),('R',.23)]:
            ET.SubElement(b,'geom',name='handle_'+side,type='box',pos=f'0 {y} .045',size='.025 .018 .03',mass='.02',rgba='.83 .66 .34 1')
        ET.SubElement(world,'geom',type='box',pos='.62 0 .441',size='.095 .285 .001',contype='0',conaffinity='0',rgba='.6 .49 .8 .55')
    else:
        for obj,col in [('A','.22 .5 .85 .55'),('B','.18 .67 .52 .55')]:
            x,y,z=spec['target_positions'][obj]
            ET.SubElement(world,'geom',type='box',pos=f'{x} {y} .441',size='.06 .06 .001',contype='0',conaffinity='0',rgba=col)
        if spec['case']=='shared':
            ET.SubElement(world,'geom',name='station',type='box',pos='.52 0 .48',size='.08 .08 .04',rgba='.72 .58 .3 1')
            ET.SubElement(world,'site',name='inspection_center',pos='.52 0 .62',size='.035',type='sphere',rgba='.98 .7 .2 .12')
    return root

def planning(spec, mode):
    result=run_verified_atg(spec['graph'],set(spec['initial_states']),set(spec['goal_states'])).to_dict()
    assert result['accepted'],result['failure_reasons']
    context={'S0':spec['initial_states'],'Sg':spec['goal_states']}
    result['independent_graph']=audit_graph(result['graph'],context)
    if mode=='serial':
        items={s['node_id']:s for s in result['schedule']['items']};serial=[];t=0.
        for nid in result['independent_graph']['topological_order']:
            item=deepcopy(items[nid]);duration=item['finish']-item['start'];item.update(start=t,finish=t+duration);t+=duration;serial.append(item)
        result['schedule']['items']=serial;result['schedule']['estimated_makespan']=t
    result['independent_schedule']=audit_schedule(result['graph'],result['schedule'],context)
    assert result['independent_graph']['valid'] and result['independent_schedule']['valid']
    return result

def waypoints(spec, item, starts):
    """Fixed-duration, fixed-waypoint primitives; planning only sets start times."""
    kind=item['action'];obj=item['object'];arms=['L','R'] if len(item['executors'])==2 else [('L' if item['executors']==['left'] else 'R')]
    result={}
    for arm in arms:
        sy=-1 if arm=='L' else 1
        initial=np.array(spec['initial_positions'][obj]);target=np.array(spec['target_positions'][obj]);origin=starts[arm]
        if kind=='pick':
            xyz=[initial[0],initial[1],.477]
            result[arm]=[(0,origin,.04),(1.2,[*xyz[:2],.65],.04),(2.5,xyz,.04),(3.4,xyz,.012),(5.3,[*xyz[:2],.70],.012),(6,[*xyz[:2],.70],.012)]
        elif kind=='place':
            result[arm]=[(0,origin,.012),(1.6,[*target[:2],.70],.012),(3,[*target[:2],.477],.012),(3.5,[*target[:2],.477],.04),(4.4,[*target[:2],.477],.04),(6,[*target[:2],.75],.04)]
        elif kind=='inspect':
            result[arm]=[(0,origin,.012),(1.3,[initial[0],initial[1],.8],.012),(3,[.52,0,.64],.012),(4.4,[.52,0,.64],.012),(5.7,[.52,0,.80],.012),(7.5,[initial[0],initial[1],.70],.012),(8,[initial[0],initial[1],.70],.012)]
        elif kind=='approach':
            result[arm]=[(0,origin,.04),(2.6,[initial[0],initial[1]+sy*.23,.65],.04),(3,[initial[0],initial[1]+sy*.23,.65],.04)]
        elif kind=='cooperative_transfer':
            at=[initial[0],initial[1]+sy*.23,.512]
            end=[target[0],target[1]+sy*.23,.512]
            result[arm]=[(0,origin,.04),(1.5,at,.04),(2.5,at,.012),(4.5,[at[0],at[1],.76],.012),(6.6,[end[0],end[1],.76],.012),(8.6,end,.012),(9.2,end,.04),(10.1,end,.04),(12,[end[0],end[1],.75],.04)]
        elif kind=='retreat':
            result[arm]=[(0,origin,.04),(2,[.4,sy*.48,.85],.04)]
    return result

def interpolate(points,t):
    for (ta,pa,ga),(tb,pb,gb) in zip(points,points[1:]):
        if t<=tb:
            a=np.clip((t-ta)/(tb-ta),0,1);s=a*a*(3-2*a)
            # Finger transitions at the end of a movement occur over their own dwell segment.
            return np.array(pa)+(np.array(pb)-pa)*s,ga+(gb-ga)*s
    return np.array(points[-1][1]),points[-1][2]

class Recorder:
    def __init__(self,m,path,spec,mode,plan):
        self.renderer=mujoco.Renderer(m,height=560,width=1000)
        self.cam=mujoco.MjvCamera();self.cam.lookat[:]=[.33,0,.68];self.cam.distance=2.24;self.cam.azimuth=140;self.cam.elevation=-34
        self.proc=subprocess.Popen([shutil.which('ffmpeg') or 'ffmpeg','-v','error','-n','-f','rawvideo','-pix_fmt','rgb24','-s','1280x720','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','fast','-crf','21','-pix_fmt','yuv420p','-movflags','+faststart',str(path)],stdin=subprocess.PIPE)
        self.title=TITLES[spec['case']];self.mode=mode;self.plan=plan;self.poster=path.with_suffix('.png');self.frames=0
        regular='C:/Windows/Fonts/arial.ttf' if Path('C:/Windows/Fonts/arial.ttf').is_file() else 'DejaVuSans.ttf'
        bold='C:/Windows/Fonts/arialbd.ttf' if Path('C:/Windows/Fonts/arialbd.ttf').is_file() else 'DejaVuSans-Bold.ttf'
        self.font=ImageFont.truetype(regular,17);self.big=ImageFont.truetype(bold,27);self.small=ImageFont.truetype(regular,14)
    def frame(self,d,t,active,status):
        self.renderer.update_scene(d,camera=self.cam);pic=Image.new('RGB',(1280,720),'#f5f7fa');pic.paste(Image.fromarray(self.renderer.render()),(0,80));draw=ImageDraw.Draw(pic)
        draw.rectangle((0,0,1280,80),fill='#182a40');draw.text((24,17),self.title,fill='white',font=self.big)
        draw.text((25,51),'MuJoCo physics execution | two Panda models | contact-based grasping',fill='#cad6e5',font=self.small)
        draw.text((1017,18),'FULL METHOD' if self.mode=='full' else 'SERIAL CONTROL',fill='#a7dccc',font=self.font)
        draw.text((1017,48),f'Sim time {t:5.2f} s',fill='white',font=self.font)
        draw.text((1020,106),'Execution units',fill='#26384d',font=self.font)
        for i,arm in enumerate(['L','R']):
            current=next((s for s in active if ('left' if arm=='L' else 'right') in s['executors']),None)
            both=current and len(current['executors'])==2;col=COLORS['B' if both else arm];y=145+i*145
            draw.rounded_rectangle((1010,y,1260,y+118),radius=8,fill='white',outline=col,width=2)
            draw.text((1024,y+12),arm+(' + partner' if both else ''),font=self.big,fill=col)
            draw.text((1024,y+52),current['node_id'] if current else 'Idle',font=self.font,fill='#26384d')
            if both:draw.text((1024,y+84),'B reserves L + R',font=self.small,fill=col)
        draw.text((1020,460),'Objects move through',font=self.font,fill='#26384d');draw.text((1020,484),'contacts and actuators.',font=self.font,fill='#26384d')
        draw.text((1020,529),'No object teleportation.',font=self.small,fill='#52647a')
        horizon=self.plan['schedule']['estimated_makespan'];left=70;scale=1170/horizon
        for ri,arm in enumerate(['L','R']):
            y=653+ri*24;draw.text((28,y),arm,font=self.font,fill=COLORS[arm]);draw.rectangle((left,y,1240,y+17),fill='#e4e9ef')
        for item in self.plan['schedule']['items']:
            x0=left+item['start']*scale;x1=left+item['finish']*scale;both=len(item['executors'])==2;y=653 if 'left' in item['executors'] else 677
            draw.rectangle((x0,y,x1,y+(41 if both else 17)),outline=COLORS['B' if both else ('L' if y==653 else 'R')])
            if t>item['start']:draw.rectangle((x0,y,min(x1,left+t*scale),y+(41 if both else 17)),fill=COLORS['B' if both else ('L' if y==653 else 'R')])
        draw.line((left+min(t,horizon)*scale,649,left+min(t,horizon)*scale,697),fill='#ce6539',width=2)
        draw.text((25,700),'Actual simulation recording | fixed skills, constructed scenes | not a hardware experiment',font=self.small,fill='#52647a')
        if status:draw.text((25,95),status,font=self.big,fill='#9b3529')
        if self.frames==FPS*4:pic.save(self.poster)
        self.proc.stdin.write(np.asarray(pic).tobytes());self.frames+=1
    def close(self):
        self.renderer.close();self.proc.stdin.close()
        if self.proc.wait()!=0:raise RuntimeError('video encoding failed')

def simulate(spec,mode,out,record=False):
    out.mkdir(parents=True,exist_ok=False);plan=planning(spec,mode);root=make_scene(spec)
    (out/'input.json').write_text(json.dumps(spec,indent=2),encoding='utf-8');(out/'planning.json').write_text(json.dumps(plan,indent=2),encoding='utf-8')
    (out/'scene.xml').write_bytes(ET.tostring(root,encoding='utf-8'))
    m,d=setup(root)
    for _ in range(200):mujoco.mj_step(m,d)
    d.time=0
    nodes={n['id']:n for n in plan['graph']['nodes']};items=plan['schedule']['items'];horizon=plan['schedule']['estimated_makespan']
    active={};finished=set();states=set(spec['initial_states']);events=[];samples=[];failure=[];inspected={'A':0.,'B':0.};cross_contacts=0;peak_cross_pen=0.;max_ik_error=0.
    station_conflicts=0;dual_contact_steps=0;dual_carry_steps=0
    objnames=['tray'] if spec['case']=='cooperative' else ['A','B']
    robot_label={i:(m.body(int(m.geom_bodyid[i])).name or '').split('_')[0] for i in range(m.ngeom)}
    holds={arm:d.site(arm+'_grip').xpos.copy() for arm in ['L','R']};heldgrip={'L':.04,'R':.04}
    recorder=Recorder(m,out/'execution.mp4',spec,mode,plan) if record else None
    trace_q=[];trace_t=[]
    for k in range(round((horizon+.5)/DT)+1):
        t=round(k*DT,8)
        # End events are processed before starts at the same timestamp.
        for nid,rt in list(active.items()):
            item=rt['item'];n=nodes[nid]
            if t+1e-8>=item['finish']:
                obj=n['object'];xyz=d.body(obj).xpos.copy();kind=n['action'];target=np.array(spec['target_positions'][obj])
                if kind=='pick':ok=xyz[2]>.62 and np.linalg.norm(xyz-d.site(('L' if item['executors']==['left'] else 'R')+'_grip').xpos)<.05
                elif kind in ['place','cooperative_transfer']:ok=np.linalg.norm(xyz-target)<.03
                elif kind=='inspect':ok=inspected[obj]>=.5
                elif kind=='approach':ok=max(np.linalg.norm(d.site(a+'_grip').xpos-rt['points'][a][-1][1]) for a in rt['points'])<.02
                else:ok=True
                events.append({'event':'finish','node':nid,'time':t,'passed':bool(ok),'object_position':xyz.tolist()})
                if ok:states.update(n['post_state'])
                else:failure.append(f'{nid}: postcondition failed')
                for a in rt['points']:holds[a]=np.array(rt['points'][a][-1][1]);heldgrip[a]=rt['points'][a][-1][2]
                finished.add(nid);del active[nid]
        for item in items:
            nid=item['node_id'];n=nodes[nid]
            if nid not in active and nid not in finished and abs(t-item['start'])<DT/2:
                missing=set(n['pre_state'])-states
                if missing:failure.append(f'{nid}: observed preconditions missing {sorted(missing)}')
                if failure:finished.add(nid);continue
                points=waypoints(spec,item,{a:d.site(a+'_grip').xpos.copy() for a in ['L','R']})
                active[nid]={'item':item,'points':points};events.append({'event':'start','node':nid,'time':t,'units':item['executors'],'resources':item['resources']})
        if k%CONTROL_STEPS==0:
            targets={a:(holds[a],heldgrip[a]) for a in ['L','R']}
            for rt in active.values():
                for a,pts in rt['points'].items():targets[a]=interpolate(pts,t-rt['item']['start'])
            for a,(xyz,g) in targets.items():
                q,error=ik(m,d,a,xyz);max_ik_error=max(max_ik_error,error)
                for i,value in enumerate(q,1):d.ctrl[m.actuator(a+'_a'+str(i)).id]=value
                for i in (1,2):d.ctrl[m.actuator(a+'_finger'+str(i)).id]=g
        mujoco.mj_step(m,d)
        # Synchronize derived body/contact coordinates with the integrated qpos.
        mujoco.mj_forward(m,d)
        contact_arms=set()
        for c in d.contact:
            for g1,g2 in [(c.geom1,c.geom2),(c.geom2,c.geom1)]:
                if robot_label[g1] in ['L','R'] and m.body(int(m.geom_bodyid[g2])).name=='tray':contact_arms.add(robot_label[g1])
            if {robot_label[c.geom1],robot_label[c.geom2]}=={'L','R'} and c.dist<-.001:
                cross_contacts+=1;peak_cross_pen=max(peak_cross_pen,-float(c.dist))
        if spec['case']=='cooperative' and 'transfer' in active and 2.5 <= t-active['transfer']['item']['start'] < 8.6:
            dual_carry_steps+=1;dual_contact_steps+=int(contact_arms=={'L','R'})
        if spec['case']=='shared':
            zone_count=0
            for obj in ['A','B']:
                xyz=d.body(obj).xpos
                if np.linalg.norm(xyz[:2]-[.52,0])<.035 and .58<xyz[2]<.66:inspected[obj]+=DT;zone_count+=1
            station_conflicts+=int(zone_count>1)
        if k%20==0:
            samples.append({'t':round(t+DT,8),'active':list(active),'objects':{o:d.body(o).xpos.tolist() for o in objnames},'grippers':{a:d.site(a+'_grip').xpos.tolist() for a in ['L','R']}})
            trace_q.append(d.qpos.copy());trace_t.append(round(t+DT,8))
        if recorder and k%20==0:recorder.frame(d,round(t+DT,8),[v['item'] for v in active.values()],'; '.join(failure[:1]))
    if recorder:recorder.close()
    errors={o:float(np.linalg.norm(d.body(o).xpos-np.array(spec['target_positions'][o]))) for o in objnames}
    velocities={o:float(np.linalg.norm(d.joint(o+'_free').qvel[:3])) for o in objnames}
    warning_count=sum(int(w.number) for w in d.warning)
    success=not failure and all(v<.03 for v in errors.values()) and all(v<.02 for v in velocities.values()) and cross_contacts==0 and warning_count==0 and station_conflicts==0 and (not dual_carry_steps or dual_contact_steps/dual_carry_steps>.9) and set(spec['goal_states'])<=states
    summary={'case':spec['case'],'seed':spec['seed'],'mode':mode,'accepted':plan['accepted'],'execution_success':bool(success),'planned_makespan_s':horizon,'simulation_end_s':float(d.time),'goal_errors_m':errors,'object_speeds_m_s':velocities,'failure_reasons':failure,'states':sorted(states),'station_dwell_s':inspected,'station_conflict_steps':station_conflicts,'cooperative_carry_steps':dual_carry_steps,'both_grippers_contact_steps':dual_contact_steps,'both_grippers_contact_fraction':dual_contact_steps/dual_carry_steps if dual_carry_steps else None,'cross_arm_penetration_contacts':cross_contacts,'peak_cross_arm_penetration_m':peak_cross_pen,'max_ik_residual':max_ik_error,'physics_warnings':warning_count,'mujoco_version':mujoco.__version__,'python_version':platform.python_version(),'physics_dt_s':DT,'control_dt_s':DT*CONTROL_STEPS,'video_fps':FPS if record else None}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');(out/'events.json').write_text(json.dumps(events,indent=2),encoding='utf-8')
    (out/'states.jsonl').write_text('\n'.join(json.dumps(s) for s in samples)+'\n',encoding='utf-8');np.savez_compressed(out/'trajectory.npz',qpos=trace_q,t=trace_t)
    return summary

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',required=True);ap.add_argument('--seeds',default='0,1,2,3,4');ap.add_argument('--cases',default='parallel,shared,cooperative');ap.add_argument('--modes',default='full,serial');ap.add_argument('--record-seed',type=int,default=0)
    args=ap.parse_args();out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=False)
    protocol={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'seeds':[int(x) for x in args.seeds.split(',')],'cases':args.cases.split(','),'modes':args.modes.split(','),'record_seed':args.record_seed,'success':'All observed task postconditions and goals; final object Euclidean error < 0.03 m; speed < 0.02 m/s; no inter-arm contact deeper than 1 mm; no physics warnings; no shared-zone conflict; both grippers contact the tray in >90% of the designated carry interval.','control':'Same fixed primitives, durations, assignment and accepted graph; serial control executes a topological serialization.','grasp':'Physical finger contacts; no attachments, welds or object-pose resets after initialization.','perturbation':'Initial XY positions uniform +/- 0.01 m; fixed task templates; not independent industrial tasks.','logging':'Body poses and qpos synchronized after mj_step by mj_forward; state snapshots use actual post-step simulation time.', 'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),W/'sim_core.py']}}
    (out/'protocol_frozen_before_runs.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    summaries=[]
    for case in protocol['cases']:
        for seed in protocol['seeds']:
            spec=specification(case,seed)
            for mode in protocol['modes']:
                s=simulate(spec,mode,out/f'{case}_{seed}_{mode}',seed==args.record_seed);summaries.append(s)
                (out/'summaries.json').write_text(json.dumps(summaries,indent=2),encoding='utf-8')
                print(json.dumps(s),flush=True)

if __name__=='__main__':main()
