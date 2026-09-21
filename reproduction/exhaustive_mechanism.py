"""Complete predeclared 3-node symbolic family; NOT independent industrial data."""
from pathlib import Path
from itertools import product, permutations
from collections import defaultdict
import sys,json,hashlib,csv
W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'implementation_v7_70'))
from atomic_task.schema import AtomicTaskGraph
from repair_comparators import evaluate

def oracle(nodes):
    # A serial order is sufficient for capacity-one resources and both units;
    # material-free monotone facts are checked without using the ATG algorithm.
    for order in permutations(nodes):
        states={'ready'}
        for n in order:
            if not set(n['pre_state'])<=states:break
            states.update(n['post_state'])
        else:return [n['id'] for n in order]
    return None

def main():
    out=Path(sys.argv[1]) if len(sys.argv)>1 else W/'results/exhaustive_run01'
    out.mkdir(parents=True,exist_ok=False)
    cases=[]
    for pre,post,durations,coop,shared in product(product(['ready','x','y'],repeat=3),product(['x','y'],repeat=3),[(1,1,1),(1,2,4)],[False,True],[False,True]):
        nodes=[{'id':f't{i+1}','action':'transform','object':'token','pre_state':[pre[i]],'post_state':[post[i]],
                'duration':durations[i],'resource':['r'] if shared else [],
                'candidate_arm':['both'] if coop and i==2 else ['left','right'],
                'mode':'cooperative' if coop and i==2 else 'single'} for i in range(3)]
        cases.append({'id':f'm{len(cases):04d}','graph':{'nodes':nodes,'edges':[]},'S0':['ready'],'Sg':sorted(set(post))})
    frozen=json.dumps(cases,sort_keys=True,ensure_ascii=False)
    (out/'frozen_cases.json').write_text(frozen,encoding='utf-8')
    (out/'manifest.json').write_text(json.dumps({'family':'all 3^3 pre x 2^3 post x 2 duration x 2 B x 2 resource','n':len(cases),
        'sha256':hashlib.sha256(frozen.encode()).hexdigest(),'scope':'author-constructed exhaustive mechanism diagnostic, not public task evidence'},indent=2),encoding='utf-8')
    rows=[];details=[]
    for c in cases:
        witness=oracle(c['graph']['nodes'])
        for method in ['audit_only','field_match','field_match_compressed','field_match_acyclic_compressed','full']:
            _,plan,reasons=evaluate(AtomicTaskGraph.from_dict(c['graph']),set(c['S0']),set(c['Sg']),method)
            row={'id':c['id'],'method':method,'oracle_feasible':witness is not None,'accepted':plan is not None}
            rows.append(row)
            if bool(plan)!=bool(witness):details.append({**row,'witness':witness,'diagnostics':reasons})
            assert not plan or witness,('false acceptance',c['id'],method)
    summary={}
    for method in sorted({r['method'] for r in rows}):
        rs=[r for r in rows if r['method']==method]
        summary[method]={'n':len(rs),'feasible':sum(r['oracle_feasible'] for r in rs),
            'accepted':sum(r['accepted'] for r in rs),'false_accept':sum(r['accepted'] and not r['oracle_feasible'] for r in rs),
            'feasible_rejected':sum(not r['accepted'] and r['oracle_feasible'] for r in rs)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    (out/'mismatches.json').write_text(json.dumps(details,ensure_ascii=False,indent=2),encoding='utf-8')
    with (out/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
