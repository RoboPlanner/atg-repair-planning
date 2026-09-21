"""Frozen public-reference projections, separate from model-generated evidence."""
from pathlib import Path
from collections import Counter, defaultdict
from itertools import combinations
from statistics import mean
from datetime import datetime, timezone
import ast, importlib.util, sys, json, hashlib, re, csv, math

W=Path(__file__).resolve().parent
sys.path.insert(0,str(W/'implementation_v7_70'))
from atomic_task.schema import AtomicTaskGraph
from repair_comparators import evaluate

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')

def recipe_case(source,group):
    ops=source['operations']
    if any(o['kappa']>2 for o in ops):raise ValueError('minimum coalition size exceeds two')
    if any(o.get('predecessor_any') for o in ops):raise ValueError('unresolved exclusive route outside fixed-node interface')
    nodes=[];edges=[]
    for op in ops:
        pre=['material:'+t for t in op['inputs']]+['completed:'+p for p in op.get('predecessors',[])]
        # Inclusive producer alternatives are already encoded by their common
        # material output. Other OR forms need an explicit translation and fail.
        for group_ids in op.get('predecessor_any_inclusive',[]):
            members=[x for x in ops if x['id'] in group_ids]
            if len(members)!=len(group_ids) or len({x['output'] for x in members})!=1 or members[0]['output'] not in op['inputs']:
                raise ValueError('inclusive alternative not represented by a common required material')
        nodes.append({'id':op['id'],'action':op['kind'],'object':op['output'],'pre_state':pre,
                      'post_state':['material:'+op['output'],'completed:'+op['id']],
                      'duration':op['duration'],'resource':op.get('resources',[]),
                      'candidate_arm':['both'] if op['kappa']==2 else ['left','right'],
                      'mode':'cooperative' if op['kappa']==2 else 'single'})
        for pred in op.get('predecessors',[]):
            edges.append({'source':pred,'target':op['id'],'type':'state_support','state':'completed:'+pred})
    return {'id':source['id'],'group':group,'source_reference':source,
            'graph':{'nodes':nodes,'edges':edges},
            'S0':['material:'+t for t in source['raw_tokens']],
            'Sg':['material:'+source['final_token']]}

def public_cases():
    root=W/'sources/AssemblyGrid_v1';cases=[];excluded=[]
    for path in sorted((root/'Experiments/recipes').glob('*.json')):
        ref=json.loads(path.read_text(encoding='utf-8'))
        try:case=recipe_case(ref,'public_recipe')
        except ValueError as exc:
            excluded.append({'id':ref['id'],'source':str(path.relative_to(W)),'reason':str(exc)});continue
        case['source_file']=str(path.relative_to(W));cases.append(case)
    # Execute only the public recipe-construction function, not simulator/tests.
    recipe_path=root/'Experiments/env/recipe.py'
    spec=importlib.util.spec_from_file_location('public_recipe_spec',recipe_path)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    test_path=root/'Experiments/env/tests/test_alternative_routes.py'
    tree=ast.parse(test_path.read_text(encoding='utf-8'))
    fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_branch_recipe')
    env={k:getattr(module,k) for k in ['OperationSpec','RecipeSpec','RecipeLibrary']}
    exec(compile(ast.Module(body=[fn],type_ignores=[]),str(test_path),'exec'),env)
    ref=module.recipe_to_dict(env['_branch_recipe'](False).get('t'));ref['id']='public_inclusive_or'
    case=recipe_case(ref,'public_normative_or');case['source_file']=str(test_path.relative_to(W));cases.append(case)
    xor=module.recipe_to_dict(env['_branch_recipe'](True).get('t'));xor['id']='public_exclusive_xor'
    try:recipe_case(xor,'public_normative_xor')
    except ValueError as exc:excluded.append({'id':xor['id'],'source':str(test_path.relative_to(W)),'reason':str(exc)})
    else:raise AssertionError('XOR must not be silently weakened')
    txt=(W/'sources/jobshop1.txt').read_text(encoding='utf-8')
    for name in ['ft06','la01','la02','la03','la04','la05']:
        part=re.search(r'\binstance '+name+r'\s*\n(.*?)(?=\n\s*instance |\Z)',txt,re.S).group(1)
        lines=part.splitlines();idx=next(i for i,line in enumerate(lines) if re.fullmatch(r'\s*\d+\s+\d+\s*',line))
        nj,nm=map(int,lines[idx].split());jobs=[];nodes=[];edges=[]
        for j,line in enumerate(lines[idx+1:idx+1+nj]):
            vals=list(map(int,line.split()));assert len(vals)==2*nm
            job=list(zip(vals[::2],vals[1::2]));jobs.append(job)
            for k,(machine,duration) in enumerate(job):
                nid=f'j{j:02d}_o{k:02d}';pre=f'j{j:02d}_done{k-1:02d}' if k else f'j{j:02d}_ready'
                nodes.append({'id':nid,'action':'process','object':f'job{j}','pre_state':[pre],
                    'post_state':[f'j{j:02d}_done{k:02d}'],'duration':duration,
                    'resource':[f'machine{machine}'],'candidate_arm':['left','right'],'mode':'single'})
                if k:edges.append({'source':f'j{j:02d}_o{k-1:02d}','target':nid,'type':'state_support','state':pre})
        cases.append({'id':name,'group':'public_jobshop_projection','source_file':'sources/jobshop1.txt',
                      'source_reference':{'id':name,'jobs':jobs,'machines':nm},
                      'graph':{'nodes':nodes,'edges':edges},
                      'S0':[f'j{j:02d}_ready' for j in range(nj)],
                      'Sg':[f'j{j:02d}_done{nm-1:02d}' for j in range(nj)]})
    return cases,excluded

def independent_source_audit(case,schedule):
    """Truth comes from public source records, never from repaired node fields."""
    ref=case['source_reference'];items=schedule['items'];issues=[];lookup={s['node_id']:s for s in items}
    if len(lookup)!=len(items):issues.append('duplicate operation')
    if 'jobs' in ref:
        expected={f'j{j:02d}_o{k:02d}':{'duration':d,'kappa':1,'resources':[f'machine{m}']}
                  for j,job in enumerate(ref['jobs']) for k,(m,d) in enumerate(job)}
    else:expected={o['id']:o for o in ref['operations']}
    if set(lookup)!=set(expected):issues.append('source operation coverage');return {'valid':False,'issues':issues}
    for nid,s in lookup.items():
        op=expected[nid];start,end=s['start'],s['finish']
        if not(math.isfinite(start) and math.isfinite(end) and 0<=start<end) or not math.isclose(end-start,op['duration'],rel_tol=1e-9,abs_tol=0):issues.append('source duration/interval')
        if set(s['resources'])!=set(op.get('resources',[])):issues.append('source resource declaration')
        if len(s['executors'])!=op['kappa'] or len(set(s['executors']))!=op['kappa'] or not set(s['executors'])<={'left','right'}:issues.append('source simultaneous arity')
    for a,b in combinations(items,2):
        if min(a['finish'],b['finish'])>max(a['start'],b['start']):
            if set(a['executors'])&set(b['executors']):issues.append('base unit overlap')
            if set(expected[a['node_id']].get('resources',[]))&set(expected[b['node_id']].get('resources',[])):issues.append('source resource overlap')
    if 'jobs' in ref:
        for j,job in enumerate(ref['jobs']):
            for k in range(1,len(job)):
                if lookup[f'j{j:02d}_o{k-1:02d}']['finish']>lookup[f'j{j:02d}_o{k:02d}']['start']:issues.append('source job precedence')
        # Coverage plus all job-chain checks includes each externally specified goal.
    else:
        available=Counter(ref['raw_tokens']);done=set()
        events=sorted([(s['start'],1,s['node_id']) for s in items]+[(s['finish'],0,s['node_id']) for s in items])
        for _,kind,nid in events:
            op=expected[nid]
            if kind==0:available[op['output']]+=1;done.add(nid);continue
            if not set(op.get('predecessors',[]))<=done:issues.append('source explicit predecessor')
            for group in op.get('predecessor_any',[]):
                if len(set(group)&done)!=1:issues.append('source XOR obligation')
            for group in op.get('predecessor_any_inclusive',[]):
                if not set(group)&done:issues.append('source OR obligation')
            for token,number in Counter(op['inputs']).items():
                if available[token]<number:issues.append('source material unavailable')
                available[token]-=number
        if available[ref['final_token']]<1:issues.append('source final token missing')
    if schedule['estimated_makespan']!=max(s['finish'] for s in items):issues.append('makespan')
    return {'valid':not issues,'issues':issues}

def main():
    out=Path(sys.argv[1]) if len(sys.argv)>1 else W/'results/external_discrete_run01'
    out.mkdir(parents=True,exist_ok=False)
    cases,excluded=public_cases();dump(out/'frozen_cases.json',cases);dump(out/'excluded.json',excluded)
    dump(out/'frozen_manifest.json',{'frozen_utc':datetime.now(timezone.utc).isoformat(),
        'cases_sha256':digest(out/'frozen_cases.json'),'protocol_sha256':digest(W/'external_discrete_protocol.md'),
        'source_sha256':{str(p.relative_to(W)):digest(p) for p in (W/'sources').rglob('*') if p.is_file() and '.git' not in p.parts},
        'script_sha256':digest(Path(__file__))})
    rows=[]
    with (out/'details.jsonl').open('x',encoding='utf-8') as f:
        for case in cases:
            for method in ['audit_only','field_match','field_match_compressed','full']:
                graph=AtomicTaskGraph.from_dict(case['graph'])
                repaired,plan,reasons=evaluate(graph,set(case['S0']),set(case['Sg']),method)
                check=independent_source_audit(case,plan.to_dict()) if plan else {'valid':False,'issues':['no accepted schedule']}
                row={'id':case['id'],'group':case['group'],'method':method,'nodes':len(graph.nodes),
                    'B_nodes':sum(n.mode=='cooperative' for n in graph.nodes),'resource_labels':len({r for n in graph.nodes for r in n.resource}),
                    'accepted':plan is not None,'source_semantics_valid':check['valid'],
                    'makespan':plan.makespan if plan else None,
                    'speedup':sum(n.duration for n in graph.nodes)/plan.makespan if plan else None}
                rows.append(row)
                f.write(json.dumps({'metrics':row,'graph':repaired.to_dict(),'schedule':plan.to_dict() if plan else None,
                    'diagnostics':reasons,'independent_source_audit':check},ensure_ascii=False)+'\n');f.flush()
                print(case['id'],method,'accepted',plan is not None,'source',check['valid'],flush=True)
    groups=defaultdict(list)
    for r in rows:groups[(r['group'],r['method'])].append(r)
    summary=[]
    for (group,method),rs in groups.items():
        summary.append({'group':group,'method':method,'n':len(rs),'accepted':sum(r['accepted'] for r in rs),
            'source_semantics_valid':sum(r['source_semantics_valid'] for r in rs),
            'mean_speedup':mean(r['speedup'] for r in rs if r['accepted']) if any(r['accepted'] for r in rs) else None})
    with (out/'metrics.csv').open('x',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    dump(out/'summary.json',{'results':summary,'exclusions':excluded,'independent_failures':[r for r in rows if r['accepted'] and not r['source_semantics_valid']]})
    assert all(not r['accepted'] or r['source_semantics_valid'] for r in rows)
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
