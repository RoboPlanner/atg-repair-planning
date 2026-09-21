from pathlib import Path
from collections import Counter,defaultdict
from statistics import mean,stdev
from datetime import datetime,timezone
import json,hashlib,csv,sys,importlib.util
W=Path(__file__).resolve().parent;ROOT=W.parents[1]
sys.dont_write_bytecode=True;sys.path.insert(0,str(W/'implementation_v7_70'))
from atomic_task.generation import read_jsonl
from atomic_task.experiments import _method_graph
from atomic_task.schema import AtomicTaskGraph
from atomic_task.pipeline import run_verified_atg
from repair_comparators import evaluate
from external_adapter import adapt,raw_sets,graph_sets,f1
OLD=ROOT/'analysis_outputs/experiment_expansion_v7_63_20260917'
R=W/'external/GNN4TaskPlan';OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else W/'results/reproduced';OUT.mkdir(parents=True,exist_ok=False)
METHODS=['audit_only','field_match','field_match_compressed','full']
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def loadl(p):return [json.loads(s) for s in p.read_text(encoding='utf-8-sig').splitlines() if s.strip()]
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
def csvout(p,rows):
    with p.open('x',encoding='utf-8-sig',newline='') as f:
        wr=csv.DictWriter(f,fieldnames=list(dict.fromkeys(k for r in rows for k in r)));wr.writeheader();wr.writerows(rows)
def stats(v):return {'n':len(v),'mean':mean(v) if v else None,'sd':stdev(v) if len(v)>1 else 0}
checkspec=importlib.util.spec_from_file_location('independent',W/'independent_audit.py')
independent=importlib.util.module_from_spec(checkspec);checkspec.loader.exec_module(independent)
history=W/'inputs/frozen_comparison_inputs.jsonl'
cases=loadl(history)
inputfile=OUT/'frozen_comparison_inputs.jsonl'
inputfile.write_text(''.join(json.dumps(c,ensure_ascii=False)+'\n' for c in cases),encoding='utf-8')
dump(OUT/'run_manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),'protocol_sha256':sha(W/'experiment_protocol.md'),
    'inputs_sha256':sha(inputfile),'source_tasks_sha256':sha(history),
    'script_sha256':{p.name:sha(p) for p in [Path(__file__),W/'external_adapter.py',W/'repair_comparators.py']},
    'implementation_sha256':{str(p.relative_to(W/'implementation_v7_70')):sha(p) for p in (W/'implementation_v7_70').rglob('*.py')}})
rows=[]
with (OUT/'comparison_details.jsonl').open('x',encoding='utf-8') as f:
    for c in cases:
        g=AtomicTaskGraph.from_dict(c['graph']);s0=set(c['spec']['S0']);sg=set(c['spec']['Sg'])
        ref=AtomicTaskGraph.from_dict(c['reference']) if 'reference' in c else None
        refedges={e.key() for e in ref.edges if e.type!='order'} if ref else None
        for method in METHODS:
            out,plan,reasons=evaluate(g,s0,sg,method)
            if plan:
                assert independent.audit_graph(out.to_dict(),c['spec'])['valid'],c['id']
                assert independent.audit_schedule(out.to_dict(),plan.to_dict(),c['spec'])['valid'],c['id']
            edges={e.key() for e in out.edges if e.type!='order'}
            row={'id':c['id'],'group':c['group'],'method':method,'accepted':plan is not None,
                 'edge_f1':f1(edges,refedges) if ref else None,'makespan':plan.makespan if plan else None,
                 'speedup':sum(n.duration for n in g.nodes)/plan.makespan if plan else None,
                 'net_added':len(out.edge_keys()-g.edge_keys()),'net_removed':len(g.edge_keys()-out.edge_keys())}
            rows.append(row);f.write(json.dumps({'metrics':row,'output_graph':out.to_dict(),'schedule':plan.to_dict() if plan else None,'reasons':reasons},ensure_ascii=False)+'\n')
csvout(OUT/'comparison_metrics.csv',rows)
groups=defaultdict(list)
for r in rows:groups[(r['group'],r['method'])].append(r)
summary={'comparison':[],'external':[]}
for (group,method),rs in groups.items():
    summary['comparison'].append({'group':group,'method':method,'n':len(rs),'accepted':sum(r['accepted'] for r in rs),
        'edge_f1':stats([r['edge_f1'] for r in rs if r['edge_f1'] is not None]),
        'speedup':stats([r['speedup'] for r in rs if r['accepted']])})

# External reference is kept separate and is read by the scoring stage only.
reference={str(c['id']):c for c in loadl(R/'data/huggingface/data.json')}
tools={n['id']:n for n in json.loads((R/'data/huggingface/tool_desc.json').read_text())['nodes']}
split=json.loads((R/'data/huggingface/split_ids.json').read_text())
testids=set(x for ids in split['test_ids'].values() for x in ids)
extrows=[]
for model in ['CodeLlama-13b','mistral-7b']:
    raw=loadl(R/f'prediction/huggingface/{model}/direct.json')
    assert len({str(c['id']) for c in raw})==len(raw)
    assert all(str(c['id']) in reference for c in raw)
    reasoncount=Counter()
    with (OUT/f'external_{model}_details.jsonl').open('x',encoding='utf-8') as f:
        for c in raw:
            predicted_nodes,predicted_edges=raw_sets(c)
            adapted=None;error=None;signature=None
            try:adapted=adapt(c,tools)
            except (ValueError,KeyError,TypeError) as exc:error=str(exc);reasoncount[error]+=1
            # The adapter's signature does not accept ground-truth records.
            ref_nodes,ref_edges=raw_sets(reference[str(c['id'])])
            for method in METHODS:
                out=plan=None;reasons=[error] if error else []
                if adapted:
                    g,s0,sg,signature=adapted;out,plan,reasons=evaluate(g,s0,sg,method)
                    if plan:
                        spec={'S0':sorted(s0),'Sg':sorted(sg)}
                        assert independent.audit_graph(out.to_dict(),spec)['valid']
                        assert independent.audit_schedule(out.to_dict(),plan.to_dict(),spec)['valid']
                out_nodes,out_edges=graph_sets(out) if out is not None else (predicted_nodes,predicted_edges)
                row={'model':model,'id':str(c['id']),'method':method,'adapted':adapted is not None,'accepted':plan is not None,
                    'signature_consistent':not signature if adapted else False,'node_f1':f1(predicted_nodes,ref_nodes),
                    'raw_edge_f1':f1(predicted_edges,ref_edges),'output_edge_f1':f1(out_edges,ref_edges),
                    'raw_exact':predicted_nodes==ref_nodes and predicted_edges==ref_edges,
                    'output_exact':out_nodes==ref_nodes and out_edges==ref_edges,
                    'relation_changed':out_edges!=predicted_edges,'adaptation_error':error or ''}
                extrows.append(row)
                f.write(json.dumps({'metrics':row,'candidate':c,'reference_id':str(c['id']),
                    'adapted_graph':adapted[0].to_dict() if adapted else None,
                    'signature_error_nodes':signature,'output_graph':out.to_dict() if out else None,
                    'schedule':plan.to_dict() if plan else None,'diagnostics':reasons},ensure_ascii=False)+'\n')
    mr=[r for r in extrows if r['model']==model]
    for method in METHODS:
        rs=[r for r in mr if r['method']==method];aa=[r for r in rs if r['adapted']];ac=[r for r in aa if r['accepted']]
        summary['external'].append({'model':model,'method':method,'archive_n':len(raw),'official_test_n':len(testids),
            'test_overlap':len(testids&{str(c['id']) for c in raw}),'missing_archived_test_outputs':len(testids-{str(c['id']) for c in raw}),
            'adapted':len(aa),'accepted':len(ac),'accepted_exact':sum(r['output_exact'] for r in ac),
            'accepted_signature_consistent':sum(r['signature_consistent'] for r in ac),
            'adapted_edge_f1_before':stats([r['raw_edge_f1'] for r in aa]),
            'adapted_edge_f1_after':stats([r['output_edge_f1'] for r in aa]),
            'changed':sum(r['relation_changed'] for r in aa),
            'improved':sum(r['output_edge_f1']>r['raw_edge_f1']+1e-12 for r in aa),
            'worsened':sum(r['output_edge_f1']<r['raw_edge_f1']-1e-12 for r in aa),
            'adaptation_failures':dict(reasoncount)})
csvout(OUT/'external_metrics.csv',extrows)
dump(OUT/'summary.json',summary)
print('COMPLETE',len(rows),len(extrows),'independently checked all accepted outputs')
