from pathlib import Path
from copy import deepcopy
from collections import Counter,defaultdict
from datetime import datetime,timezone
import csv,hashlib,importlib.util,io,json,math,platform,statistics,sys,time,unittest
import numpy,scipy
WORK=Path(__file__).resolve().parent;ROOT=WORK.parents[1]
sys.path.insert(0,str(WORK/'implementation_v7_63'))
from atomic_task.schema import AtomicTaskGraph
from atomic_task.pipeline import run_verified_atg
from atomic_task.verification import joint_graph_audit
from atomic_task.optimization import replay_accepted_events
from milp_baseline import solve
spec=importlib.util.spec_from_file_location('independent_reference_checks',ROOT/'analysis_outputs/gpt6_current_session_planning_20260917_v1/verify_and_report.py')
independent=importlib.util.module_from_spec(spec);spec.loader.exec_module(independent)
FLAGS={'full':{},'no_state':{'use_state_dependency':False},'no_sync':{'use_synchronization_repair':False},
       'no_resource':{'use_resource_constraint':False},'no_compression':{'use_critical_path':False},
       'no_executor':{'use_executor_assignment':False}}
GATES=['schema_valid','closed','goal_reachable','acyclic','synchronization_complete','resource_ordered']

def readl(name):return [json.loads(s) for s in (WORK/'inputs'/name).read_text(encoding='utf-8').splitlines() if s.strip()]
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def stat(xs):
    xs=[x for x in xs if x is not None]
    return {'n':len(xs),'mean':statistics.mean(xs) if xs else None,'sd':statistics.stdev(xs) if len(xs)>1 else None,
            'median':statistics.median(xs) if xs else None,'min':min(xs) if xs else None,'max':max(xs) if xs else None}
def csvout(p,rows):
    fields=list(dict.fromkeys(k for row in rows for k in row))
    with p.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

def evaluate(c,method):
    g=AtomicTaskGraph.from_dict(c['graph']);s0=set(c['spec']['S0']);sg=set(c['spec']['Sg'])
    before=joint_graph_audit(g,s0,sg).to_dict()
    result=run_verified_atg(g,s0,sg,**FLAGS[method]);encoded=result.to_dict()
    row={k:c[k] for k in ['id','base_id','view','fraction','seed','realized_fraction','jitter','width','depth','resource_pattern','join_mode'] if k in c}
    row.update(method=method,nodes=len(g.nodes),cooperative_nodes=sum(n.mode=='cooperative' for n in g.nodes),
               before_joint=before['valid'],after_joint=result.audit.valid if result.audit else False,
               accepted=result.accepted,accepted_events=0,rejected_events=0,net_added=0,net_removed=0,
               replay_valid=None,export_valid=None,independent_graph_valid=None,makespan=None,speedup=None,utilization=None)
    for gate in GATES:row['before_'+gate]=before['checks'][gate]
    if result.audit and result.graph:
        for gate in GATES:row['after_'+gate]=result.audit.joint_after['checks'][gate]
        events=result.audit.events;row['accepted_events']=sum(e.accepted for e in events);row['rejected_events']=sum(not e.accepted for e in events)
        row['net_added']=len(result.graph.edge_keys()-g.edge_keys());row['net_removed']=len(g.edge_keys()-result.graph.edge_keys())
        replay=replay_accepted_events(g,events)
        row['replay_valid']=replay.edge_keys()==result.graph.edge_keys() and [n.to_dict() for n in replay.nodes]==[n.to_dict() for n in result.graph.nodes]
        assert row['replay_valid'],(c['id'],method,'replay')
        for stage in ['state_closure','synchronization','resource_mutex','compression']:
            row[stage+'_accepted_events']=sum(e.accepted and e.stage==stage for e in events)
    diagnostics={}
    if result.accepted:
        gcheck=independent.audit_graph(encoded['graph'],c['spec'])
        scheck=independent.audit_schedule(encoded['graph'],encoded['schedule'],c['spec'])
        row['independent_graph_valid']=gcheck['valid'];row['export_valid']=scheck['valid']
        assert gcheck['valid'] and scheck['valid'],(c['id'],method,gcheck,scheck)
        row['makespan']=result.schedule.makespan
        serial=sum(n.duration for n in g.nodes);busy=sum(n.duration*(2 if n.mode=='cooperative' else 1) for n in g.nodes)
        row.update(serial_duration=serial,speedup=serial/row['makespan'],duration_reduction=1-row['makespan']/serial,utilization=busy/(2*row['makespan']))
        diagnostics={'graph':gcheck,'schedule':scheck}
    else:assert result.schedule is None
    return row,{'input_id':c['id'],'method':method,'before_audit':before,'result':encoded,'independent_checks':diagnostics,'metrics':row}

def aggregate(rows,groupkeys):
    groups=defaultdict(list)
    for r in rows:groups[tuple(r.get(k) for k in groupkeys)].append(r)
    output=[]
    for key,group in groups.items():
        entry=dict(zip(groupkeys,key));entry.update(n=len(group),before_joint=sum(r['before_joint'] for r in group),
            after_joint=sum(r['after_joint'] for r in group),accepted=sum(r['accepted'] for r in group),
            replay_checked=sum(r['replay_valid'] is not None for r in group),replay_passed=sum(bool(r['replay_valid']) for r in group),
            exported_checked=sum(r['export_valid'] is not None for r in group),exported_passed=sum(bool(r['export_valid']) for r in group),
            net_added=sum(r['net_added'] for r in group),net_removed=sum(r['net_removed'] for r in group))
        for name in ['makespan','speedup','duration_reduction','utilization','timing_median_ms']:
            entry[name]=stat([r.get(name) for r in group])
        for gate in GATES:
            entry['before_'+gate]=sum(r.get('before_'+gate,False) for r in group)
            entry['after_'+gate]=sum(r.get('after_'+gate,False) for r in group)
        output.append(entry)
    return output

def main():
    out=WORK/'results';out.mkdir(exist_ok=False)
    protocol=json.loads((WORK/'experiment_protocol_frozen.json').read_text(encoding='utf-8'))
    assert all(sha(WORK/p)==digest for p,digest in protocol['files'].items())
    # Archive the full preflight, including the MILP-versus-exhaustive checks.
    suite=unittest.defaultTestLoader.discover(str(WORK/'implementation_v7_63/tests'))
    local=unittest.defaultTestLoader.loadTestsFromName('test_new_contract_and_milp')
    suite.addTests(local);stream=io.StringIO();tests=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    (out/'preflight_tests.txt').write_text(stream.getvalue(),encoding='utf-8');assert tests.wasSuccessful()
    dump(out/'run_environment.json',{'started_utc':datetime.now(timezone.utc).isoformat(),'python':sys.version,'python_executable':sys.executable,
        'platform':platform.platform(),'processor':platform.processor(),'numpy':numpy.__version__,'scipy':scipy.__version__,
        'tests':{'methods':tests.testsRun,'failures':len(tests.failures),'errors':len(tests.errors)},
        'scripts_sha256':{p.name:sha(p) for p in [Path(__file__),WORK/'milp_baseline.py',WORK/'test_new_contract_and_milp.py']},
        'milp_numeric_reconstruction':'exact earliest starts from rounded integer arm and pair decisions, retain raw solution; verify final schedule',
        'milp_optimality_tolerance':1e-6})
    summaries={};allrows=[]
    plans=[('information','information_views96.jsonl',['view','method'],list(FLAGS)),
           ('deletion','relation_deletion216.jsonl',['fraction'],['full']),
           ('duration','duration_variants168.jsonl',['jitter'],['full']),
           ('shape','branch_resource_cooperation24.jsonl',['width'],['full'])]
    for name,file,groupkeys,methods in plans:
        rows=[]
        with (out/(name+'_details.jsonl')).open('x',encoding='utf-8') as handle:
            cases=readl(file)
            for c in cases:
                for method in methods:
                    row,detail=evaluate(c,method)
                    if name=='shape':
                        g=AtomicTaskGraph.from_dict(c['graph']);s0=set(c['spec']['S0']);sg=set(c['spec']['Sg'])
                        for _ in range(3):run_verified_atg(g,s0,sg)
                        times=[]
                        for _ in range(10):
                            start=time.perf_counter();trial=run_verified_atg(g,s0,sg);times.append((time.perf_counter()-start)*1000)
                            assert trial.accepted==row['accepted']
                        row['timing_median_ms']=statistics.median(times);detail['timing_ms_samples']=times
                    handle.write(json.dumps(detail,ensure_ascii=False,allow_nan=False)+'\n')
                    rows.append(row)
        csvout(out/(name+'_metrics.csv'),rows);allrows+=rows
        summaries[name]=aggregate(rows,groupkeys)
        if name=='shape':
            summaries['shape_by_resource']=aggregate(rows,['resource_pattern'])
            summaries['shape_by_cooperation']=aggregate(rows,['join_mode'])
            summaries['shape_by_nodes']=aggregate(rows,['nodes'])
        print(f'{name}: {len(rows)} evaluations, accepted={sum(r["accepted"] for r in rows)}, replay failures=0',flush=True)
    miprows=[]
    with (out/'milp_details.jsonl').open('x',encoding='utf-8') as handle:
        for c in readl('gpt6_base24.jsonl'):
            row,detail=evaluate(c,'full');g=AtomicTaskGraph.from_dict(detail['result']['graph'])
            mip=solve(g,time_limit=10)
            validated=False
            if mip['schedule'] is not None:
                check=independent.audit_schedule(g.to_dict(),mip['schedule'],c['spec'])
                validated=check['valid'];mip['independent_schedule_check']=check
            r={'id':c['id'],'nodes':len(g.nodes),'list_makespan':row['makespan'],'milp_status':mip['status'],
               'milp_schedule_valid':validated,'milp_optimal':mip.get('optimal_within_tolerance',False) and validated,
               'milp_makespan':mip['schedule']['estimated_makespan'] if validated else None,
               'dual_bound':mip['dual_bound'],'solver_gap':mip['mip_gap'],
               'build_solve_seconds':mip['elapsed_seconds_build_and_solve'],'list_gap_to_optimum':None}
            if r['milp_optimal']:
                assert r['list_makespan']+1e-8>=r['milp_makespan']
                r['list_gap_to_optimum']=r['list_makespan']/r['milp_makespan']-1
            if mip['schedule'] is not None:assert validated,(c['id'],mip)
            miprows.append(r);handle.write(json.dumps({'case':c,'list_result':detail,'milp':mip,'metrics':r},ensure_ascii=False)+'\n')
            print(f'MILP {c["id"]}: status={mip["status"]}, list={row["makespan"]}, optimized={r["milp_makespan"]}',flush=True)
    csvout(out/'milp_metrics.csv',miprows)
    summaries['milp']={'n':len(miprows),'valid':sum(r['milp_schedule_valid'] for r in miprows),'optimal':sum(r['milp_optimal'] for r in miprows),
        'status_counts':dict(Counter(r['milp_status'] for r in miprows)),
        'list_makespan':stat([r['list_makespan'] for r in miprows]),'milp_makespan':stat([r['milp_makespan'] for r in miprows]),
        'list_gap_to_optimum':stat([r['list_gap_to_optimum'] for r in miprows]),
        'list_matches_optimum':sum(r['milp_optimal'] and abs(r['list_gap_to_optimum'])<1e-8 for r in miprows),
        'worst':max((r for r in miprows if r['milp_optimal']),key=lambda r:r['list_gap_to_optimum'],default=None)}
    summaries['total']={'pipeline_evaluations':len(allrows),'accepted':sum(r['accepted'] for r in allrows),
        'replay_checked':sum(r['replay_valid'] is not None for r in allrows),'replay_passed':sum(bool(r['replay_valid']) for r in allrows),
        'exported_checked':sum(r['export_valid'] is not None for r in allrows),'exported_passed':sum(bool(r['export_valid']) for r in allrows),
        'frozen_files_unchanged':all(sha(WORK/p)==digest for p,digest in protocol['files'].items())}
    assert summaries['total']['frozen_files_unchanged']
    dump(out/'summary.json',summaries)
    print(json.dumps({'total':summaries['total'],'milp':summaries['milp']},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
