"""Same-input planning controls on eight explicitly constructed task specifications."""
from pathlib import Path
from copy import deepcopy
import argparse,csv,hashlib,json,time
from expanded_tasks import make_spec,TITLES
from atomic_task.schema import AtomicTaskGraph
from repair_comparators import evaluate
from independent_audit import audit_graph,audit_schedule

METHODS=['audit_only','field_match_compressed','full']
PROFILES=['fields_only','wrong_labels','conservative_order','missing_producer']

def causal_edges(spec):
    edges=[];initial=set(spec['initial_states'])
    for v in spec['graph']['nodes']:
        for state in v['pre_state']:
            if state in initial:continue
            producers=[u for u in spec['graph']['nodes'] if state in u['post_state'] and u['id']!=v['id']]
            assert len(producers)==1,(v,state,producers)
            u=producers[0]
            edges.append({'source':u['id'],'target':v['id'],'type':'state_support','state':state})
            if v['mode']=='cooperative':edges.append({'source':u['id'],'target':v['id'],'type':'synchronization','state':state})
    return edges

def can_reach(nodes,initial,goals):
    state=set(initial);remaining=deepcopy(nodes)
    while True:
        ready=[n for n in remaining if set(n['pre_state'])<=state]
        if not ready:break
        for n in ready:state.update(n['post_state']);remaining.remove(n)
    return set(goals)<=state

def cases():
    output=[]
    for task in TITLES:
        spec=make_spec(task,100);edges=causal_edges(spec)
        # Node construction order is a valid topological witness for these templates.
        ids=[n['id'] for n in spec['graph']['nodes']];ranks={n:i for i,n in enumerate(ids)}
        assert all(ranks[e['source']]<ranks[e['target']] for e in edges)
        for profile in PROFILES:
            g=deepcopy(spec['graph'])
            if profile=='wrong_labels':g['edges']=[dict(e,state='incorrect_'+e['state']) for e in edges]
            elif profile=='conservative_order':g['edges']=deepcopy(edges)+[{'source':a,'target':b,'type':'order'} for a,b in zip(ids,ids[1:])]
            elif profile=='missing_producer':
                victim=next(n for n in g['nodes'] if any(s in spec['goal_states'] for s in n['post_state']))
                g['nodes']=[n for n in g['nodes'] if n['id']!=victim['id']];g['edges']=[e for e in edges if victim['id'] not in (e['source'],e['target'])]
            feasible=can_reach(g['nodes'],spec['initial_states'],spec['goal_states'])
            output.append({'id':task+'_'+profile,'task':task,'profile':profile,'graph':g,'initial_states':spec['initial_states'],'goal_states':spec['goal_states'],'causal_reference':edges,'expected_discrete_goal_reachable':feasible,'construction':'Author-defined state fields and primitive semantics; no external or natural-language reference claimed.'})
    return output

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);a=p.parse_args();out=Path(a.output);out.mkdir(parents=True,exist_ok=False);inputs=cases()
    inp=out/'inputs';inp.mkdir()
    for c in inputs:(inp/(c['id']+'.json')).write_text(json.dumps(c,indent=2),encoding='utf-8')
    protocol={'created_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'input_count':len(inputs),'setting_count':len(inputs)*len(METHODS),'methods':METHODS,'input_files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in inp.glob('*.json')},'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/'protocol_frozen_before_evaluation.json').write_text(json.dumps(protocol,indent=2),encoding='utf-8')
    rows=[];records=[]
    for c in inputs:
        for method in METHODS:
            graph,schedule,reasons=evaluate(AtomicTaskGraph.from_dict(c['graph']),set(c['initial_states']),set(c['goal_states']),method)
            gd=graph.to_dict();sd=schedule.to_dict() if schedule else None;context={'S0':c['initial_states'],'Sg':c['goal_states']}
            qa=audit_graph(gd,context);qs=audit_schedule(gd,sd,context) if sd else None
            accepted=schedule is not None
            if accepted:
                assert qa['valid'] and qs['valid'],(c['id'],method,qa,qs)
                assert c['expected_discrete_goal_reachable']
                # Directly check the original declared causal obligations on this input.
                times={i['node_id']:i for i in sd['items']}
                assert all(times[e['source']]['finish']<=times[e['target']]['start']+1e-9 for e in c['causal_reference'])
            row={'task':c['task'],'profile':c['profile'],'method':method,'accepted':accepted,'expected_goal_reachable':c['expected_discrete_goal_reachable'],'independent_acceptance_valid':bool(accepted and qa['valid'] and qs['valid']),'makespan_s':sd['estimated_makespan'] if sd else None,'state_edges':sum(e['type']=='state_support' for e in gd['edges']),'sync_edges':sum(e['type']=='synchronization' for e in gd['edges']),'resource_edges':sum(e['type']=='resource_mutex' for e in gd['edges']),'order_edges':sum(e['type']=='order' for e in gd['edges'])}
            rows.append(row);records.append({'input_id':c['id'],**row,'graph':gd,'schedule':sd,'diagnostics':reasons,'independent_graph':qa,'independent_schedule':qs})
    (out/'records.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    with (out/'records.csv').open('w',encoding='utf-8',newline='') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    summary={method:{'accepted':sum(r['accepted'] for r in rows if r['method']==method),'total':32,'feasible_accepted':sum(r['accepted'] and r['expected_goal_reachable'] for r in rows if r['method']==method),'infeasible_accepted':sum(r['accepted'] and not r['expected_goal_reachable'] for r in rows if r['method']==method)} for method in METHODS}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary))

if __name__=='__main__':main()
