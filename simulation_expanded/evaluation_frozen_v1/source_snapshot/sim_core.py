from pathlib import Path
from copy import deepcopy
import xml.etree.ElementTree as ET
import numpy as np,mujoco
from PIL import Image
W=Path(__file__).resolve().parent
HOME=np.array([0,-.35,0,-2.05,0,1.7,.7854])
def scene():
    source=ET.parse(W/'assets/franka_local/panda.xml').getroot()
    root=ET.Element('mujoco',model='ATG_dual_panda')
    ET.SubElement(root,'compiler',angle='radian',autolimits='true')
    ET.SubElement(root,'option',timestep='.002',integrator='implicitfast',iterations='100',cone='elliptic',impratio='10',noslip_iterations='5',gravity='0 0 -9.81')
    visual=ET.SubElement(root,'visual');ET.SubElement(visual,'global',offwidth='1280',offheight='720');ET.SubElement(visual,'headlight',ambient='.35 .35 .35',diffuse='.65 .65 .65',specular='.2 .2 .2')
    default=ET.SubElement(root,'default');ET.SubElement(default,'joint',damping='2',armature='.1');ET.SubElement(default,'geom',friction='1.5 .02 .001',solref='.01 1',solimp='.95 .99 .001')
    assets=deepcopy(source.find('asset'));ET.SubElement(assets,'texture',name='sky',type='skybox',builtin='gradient',rgb1='.83 .87 .93',rgb2='.96 .97 .99',width='512',height='512');root.append(assets)
    world=ET.SubElement(root,'worldbody');ET.SubElement(world,'light',pos='0 -1 3',dir='0 .5 -1',directional='true',castshadow='true')
    ET.SubElement(world,'geom',name='floor',type='plane',size='3 3 .1',rgba='.9 .92 .95 1')
    ET.SubElement(world,'geom',name='table',type='box',pos='.3 0 .4',size='.65 .85 .04',rgba='.24 .31 .4 1')
    actuators=ET.SubElement(root,'actuator');contacts=ET.SubElement(root,'contact');eq=ET.SubElement(root,'equality')
    for prefix,y,col in [('L',-.48,'.82 .87 .95 1'),('R',.48,'.77 .9 .85 1')]:
        body=deepcopy(source.find('worldbody/body'));body.set('pos',f'0 {y} .44')
        for gi,e in enumerate(body.iter()):
            if 'name' in e.attrib:e.set('name',prefix+'_'+e.attrib['name'])
            if e.tag=='body':e.set('gravcomp','1')
            if e.tag=='geom':
                e.set('name',prefix+'_geom'+str(gi));e.set('rgba',col if e.attrib['mesh'] not in ('finger','hand','link5') else '.16 .19 .23 1')
        hand=next(b for b in body.iter('body') if b.attrib['name']==prefix+'_panda_hand')
        ET.SubElement(hand,'site',name=prefix+'_grip',pos='0 0 .1034',size='.004',rgba='1 .2 .1 1')
        world.append(body)
        for i in range(1,8):
            joint=prefix+'_panda_joint'+str(i)
            ET.SubElement(actuators,'position',name=prefix+'_a'+str(i),joint=joint,kp='1200' if i<5 else '600',kv='70' if i<5 else '35')
        for i in (1,2):ET.SubElement(actuators,'position',name=prefix+'_finger'+str(i),joint=prefix+'_panda_finger_joint'+str(i),kp='300',kv='10',ctrlrange='0 .04',forcerange='-20 20')
        ET.SubElement(contacts,'exclude',body1=prefix+'_panda_link0',body2=prefix+'_panda_link1')
    for name,pos,col in [('A',[.45,-.48,.47],'.2 .5 .85 1'),('B',[.45,.48,.47],'.1 .68 .52 1')]:
        b=ET.SubElement(world,'body',name=name,pos=' '.join(map(str,pos)));ET.SubElement(b,'freejoint',name=name+'_free');ET.SubElement(b,'geom',name=name+'_geom',type='box',size='.025 .025 .025',mass='.08',rgba=col)
    return root

def setup(root):
    model=mujoco.MjModel.from_xml_string(ET.tostring(root,encoding='unicode'),{p.name:p.read_bytes() for p in (W/'assets/franka_local').glob('*.stl')})
    d=mujoco.MjData(model)
    for prefix in ['L','R']:
        for i,val in enumerate(HOME,1):d.joint(prefix+'_panda_joint'+str(i)).qpos[:]=val;d.ctrl[model.actuator(prefix+'_a'+str(i)).id]=val
        for i in (1,2):d.joint(prefix+'_panda_finger_joint'+str(i)).qpos[:]=.04;d.ctrl[model.actuator(prefix+'_finger'+str(i)).id]=.04
    mujoco.mj_forward(model,d)
    return model,d

def ik(m,d,prefix,target,quat=np.array([0.,1.,0.,0.])):
    tmp=mujoco.MjData(m);tmp.qpos[:]=d.qpos
    ids=[m.joint(prefix+'_panda_joint'+str(i)).id for i in range(1,8)]
    qidx=np.array([m.jnt_qposadr[i] for i in ids]);vidx=np.array([m.jnt_dofadr[i] for i in ids]);site=m.site(prefix+'_grip').id
    jp=np.zeros((3,m.nv));jr=jp.copy();curq=np.zeros(4);neg=np.zeros(4);dif=np.zeros(4);ori=np.zeros(3)
    for _ in range(80):
        mujoco.mj_forward(m,tmp);mujoco.mju_mat2Quat(curq,tmp.site_xmat[site]);mujoco.mju_negQuat(neg,curq);mujoco.mju_mulQuat(dif,quat,neg);mujoco.mju_quat2Vel(ori,dif,1)
        err=np.r_[np.asarray(target)-tmp.site_xpos[site],ori*.5]
        if np.linalg.norm(err)<1e-5:break
        mujoco.mj_jacSite(m,tmp,jp,jr,site);j=np.vstack([jp[:,vidx],jr[:,vidx]*.5]);delta=j.T@np.linalg.solve(j@j.T+np.eye(6)*.0001,err)
        tmp.qpos[qidx]=np.clip(tmp.qpos[qidx]+np.clip(delta,-.1,.1),m.jnt_range[ids,0]+.002,m.jnt_range[ids,1]-.002)
    return tmp.qpos[qidx].copy(),float(np.linalg.norm(err))

if __name__=='__main__':
    m,d=setup(scene());print('home',[d.site(p+'_grip').xpos.tolist() for p in ['L','R']])
    for p,y in [('L',-.48),('R',.48)]:
        q,e=ik(m,d,p,[.45,y,.50]);print(p,e,q)
        for i,x in enumerate(q,1):d.ctrl[m.actuator(p+'_a'+str(i)).id]=x
    for _ in range(1500):mujoco.mj_step(m,d)
    print('actual',[d.site(p+'_grip').xpos.tolist() for p in ['L','R']])
    r=mujoco.Renderer(m,height=720,width=1280);cam=mujoco.MjvCamera();cam.lookat[:]=[.25,0,.65];cam.distance=2.4;cam.azimuth=145;cam.elevation=-30;r.update_scene(d,camera=cam);Image.fromarray(r.render()).save(W/'pilot_scene.png');r.close()
