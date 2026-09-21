"""Additional audit: require the contacting robot bodies to be fingers, not any arm link."""
from pathlib import Path
import argparse,json
import mujoco,numpy as np

def verify(directory):
    assets=Path(__file__).parent/'assets/franka_local'
    records=[]
    for trial in sorted(directory.glob('cooperative_*_*')):
        if not trial.is_dir():continue
        plan=json.loads((trial/'planning.json').read_text())
        transfer=next(i for i in plan['schedule']['items'] if i['node_id']=='transfer')
        m=mujoco.MjModel.from_xml_string((trial/'scene.xml').read_text(),{p.name:p.read_bytes() for p in assets.glob('*.stl')})
        d=mujoco.MjData(m);trace=np.load(trial/'trajectory.npz')
        frames=both=0;contact_bodies=set()
        for q,t in zip(trace['qpos'],trace['t']):
            if not transfer['start']+2.5<=t<transfer['start']+8.6:continue
            frames+=1;d.qpos[:]=q;mujoco.mj_forward(m,d);arms=set()
            for c in d.contact:
                a=m.body(int(m.geom_bodyid[c.geom1])).name;b=m.body(int(m.geom_bodyid[c.geom2])).name
                partner=b if a=='tray' else a if b=='tray' else ''
                if partner:
                    contact_bodies.add(partner)
                    if partner.startswith(('L_','R_')) and partner.endswith(('leftfinger','rightfinger')):arms.add(partner[0])
            both+=int(arms=={'L','R'})
        records.append({'trial':trial.name,'sampled_frames':frames,'both_fingers_frames':both,'fraction':both/frames,'contacting_bodies':sorted(contact_bodies),'passed':both/frames>.9})
    assert len(records)==10,len(records)
    output={'scope':'Additional post-evaluation audit of finger-specific contacts from stored 40 ms samples; original online counts include any robot-link contact. No full-rate finger-contact claim is made.','total':10,'passed':sum(r['passed'] for r in records),'records':records}
    destination=directory/'finger_contact_verification.json'
    assert not destination.exists(),destination
    destination.write_text(json.dumps(output,indent=2),encoding='utf-8')
    print(json.dumps(output,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory');verify(Path(p.parse_args().directory))
