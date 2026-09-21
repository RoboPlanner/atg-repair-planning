"""Export verified frozen schedules as website replay data and animated SVGs.

No plans are generated, repaired, rescheduled, or added to the experiment count.
"""
from pathlib import Path
from collections import defaultdict
from html import escape
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / 'reproduction'
OUT = ROOT / 'docs/assets'
sys.path.insert(0, str(REP))
from independent_audit import audit_graph, audit_schedule
from external_discrete import independent_source_audit

def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines()]

def source(path, record_id, method=None):
    result = {'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'record_id': record_id}
    if method:
        result['method'] = method
    return result

def make_svg(case, animated=False):
    """Shared geometry for the controllable player and standalone SVG animation."""
    width, height = 1040, 492
    horizon = case['horizon']
    left, right = 68, 992
    scale = (right-left)/horizon
    comparison = len(case['plans']) == 2
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="replay-svg-title replay-svg-desc">',
           f'<title id="replay-svg-title">{escape(case["title"])}</title>',
           '<desc id="replay-svg-desc">Replay of archived accepted schedules. Time is symbolic. Purple joint tasks occupy both L and R. Rectangles show exact stored start and finish times.</desc>',
           '<style>text{font-family:Arial,sans-serif;fill:#26384d}.label{font-size:13px}.tiny{font-size:11px}.clock{stroke:#d76c40;stroke-width:2}.task-progress{pointer-events:none}.node-id{font-weight:700;font-size:14px}.node-action{font-size:11px}.graph-edge{fill:none;stroke:#99aac0;stroke-width:1.4}</style>',
           '<defs><marker id="replay-arrow" markerWidth="7" markerHeight="7" refX="6" refY="3.5" orient="auto"><path d="M0,0 L7,3.5 L0,7" fill="#99aac0"/></marker></defs>',
           '<rect width="1040" height="492" rx="8" fill="white"/>']
    for pi, plan in enumerate(case['plans']):
        y0 = 74 + pi*200 if comparison else 322
        out.append(f'<text x="{left}" y="{y0-23}" font-size="15" font-weight="700">{escape(plan["label"])}</text>')
        out.append(f'<text x="{right}" y="{y0-23}" text-anchor="end" class="label">Makespan {plan["schedule"]["estimated_makespan"]:g}</text>')
        for ri, unit in enumerate(['L','R']):
            y=y0+ri*48
            out += [f'<text x="35" y="{y+28}" font-size="16" font-weight="700">{unit}</text>', f'<rect x="{left}" y="{y}" width="{right-left}" height="42" fill="#f4f7fa" stroke="#dce3eb"/>']
        for tick in range(6):
            t=horizon*tick/5; x=left+t*scale
            out.append(f'<line x1="{x:.5f}" x2="{x:.5f}" y1="{y0}" y2="{y0+90}" stroke="#dce3eb" stroke-dasharray="2 4"/>')
            out.append(f'<text x="{x:.5f}" y="{y0+112}" text-anchor="middle" class="tiny">{t:g}</text>')
        for item in plan['schedule']['items']:
            nid=item['node_id'];both=len(item['executors'])==2
            x=left+item['start']*scale; w=(item['finish']-item['start'])*scale
            y=y0 if both or item['executors']==['left'] else y0+48
            h=90 if both else 42
            color='#8056a9' if both else ('#376eaa' if item['executors']==['left'] else '#388b82')
            tip=f"{nid} · {item['action']} · {item['object']} | [{item['start']:g}, {item['finish']:g}) | units: {', '.join(item['executors'])} | resources: {', '.join(item['resources']) or 'none declared'}"
            out.append(f'<g data-task="{escape(nid)}" data-plan="{pi}"><title>{escape(tip)}</title>')
            out.append(f'<rect x="{x:.5f}" y="{y}" width="{w:.5f}" height="{h}" rx="3" fill="{color}" fill-opacity=".13" stroke="{color}" stroke-width=".8"/>')
            out.append(f'<rect class="task-progress" data-progress="{escape(nid)}" data-plan="{pi}" x="{x:.5f}" y="{y}" width="0" height="{h}" rx="3" fill="{color}" fill-opacity=".72">')
            if animated:
                s=item['start']/horizon*12/14;f=item['finish']/horizon*12/14
                out.append(f'<animate attributeName="width" values="0;0;{w:.5f};{w:.5f}" keyTimes="0;{s:.8f};{f:.8f};1" dur="14s" repeatCount="indefinite"/>')
            out.append('</rect>')
            if w>42:
                label = nid if not comparison else nid.replace('j0','J').replace('_o0','.').replace('_o','.')
                out.append(f'<text x="{x+w/2:.5f}" y="{y+h/2+5}" text-anchor="middle" font-size="{14 if not comparison else 11}" font-weight="600">{escape(label)}{(" · B" if both else "")}</text>')
            out.append('</g>')
        out.append(f'<line class="clock" data-clock="{pi}" x1="{left}" x2="{left}" y1="{y0-5}" y2="{y0+94}">')
        if animated:
            for attr in ['x1','x2']:
                out.append(f'<animate attributeName="{attr}" values="{left};{right};{right}" keyTimes="0;0.85714286;1" dur="14s" repeatCount="indefinite"/>')
        out.append('</line>')
    if not comparison:
        graph=case['plans'][0]['graph']; items={x['node_id']:x for x in case['plans'][0]['schedule']['items']}
        pairs=defaultdict(list)
        for e in graph['edges']:
            if e['type']=='state_support':pairs[(e['source'],e['target'])].append(e['state'])
        levels={n['id']:0 for n in graph['nodes']}
        for _ in graph['nodes']:
            for u,v in pairs:levels[v]=max(levels[v],levels[u]+1)
        groups=defaultdict(list)
        for n in graph['nodes']:groups[levels[n['id']]].append(n)
        depth=max(levels.values()) or 1;pos={}
        for level, nodes in groups.items():
            for ni,node in enumerate(nodes):
                pos[node['id']] = (110+level*820/depth, 117+(ni-(len(nodes)-1)/2)*118)
        out.append('<text x="68" y="26" class="label">Accepted state-support projection</text>')
        out.append('<text x="992" y="26" text-anchor="end" class="tiny">All accepted relation types constrain the schedule.</text>')
        for (u,v), states in pairs.items():
            x1,y1=pos[u];x2,y2=pos[v];r=31
            lift=55 if levels[v]-levels[u]>1 else 0
            path=f'M{x1+r},{y1} C{x1+r+45},{y1+lift} {x2-r-45},{y2+lift} {x2-r-2},{y2}'
            out.append(f'<path class="graph-edge" d="{path}" marker-end="url(#replay-arrow)"><title>{escape(u+" → "+v+" | "+", ".join(states))}</title></path>')
        for node in graph['nodes']:
            nid=node['id'];x,y=pos[nid];item=items[nid];b=node['mode']=='cooperative'
            color='#8056a9' if b else ('#376eaa' if item['executors']==['left'] else '#388b82')
            out.append(f'<g><title>{escape(nid+": "+node["action"]+" "+node["object"])}</title><circle data-node="{escape(nid)}" cx="{x}" cy="{y}" r="31" fill="{color}" fill-opacity=".12" stroke="{color}" stroke-width="1.5">')
            if animated:
                s=item['start']/horizon*12/14;f=item['finish']/horizon*12/14
                out.append(f'<animate attributeName="fill-opacity" values=".12;.75;.4;.4" keyTimes="0;{s:.8f};{f:.8f};1" calcMode="discrete" dur="14s" repeatCount="indefinite"/>')
            out.append('</circle>')
            if len(nid)>8 and '_' in nid:
                a,b=nid.split('_',1)
                out.append(f'<text x="{x}" y="{y-4}" text-anchor="middle" font-size="11" font-weight="600"><tspan x="{x}">{escape(a)}</tspan><tspan x="{x}" dy="14">{escape(b)}</tspan></text>')
            else:
                out.append(f'<text x="{x}" y="{y+4}" text-anchor="middle" class="node-id">{escape(nid)}</text>')
            label=node['action']+' '+node['object']
            out.append(f'<text x="{x}" y="{y+51}" text-anchor="middle" class="node-action">{escape(label[:35])}</text></g>')
    else:
        out.append('<text x="68" y="437" class="label">Same input · same compression · common time axis</text>')
        out.append(f'<text x="992" y="437" text-anchor="end" class="label">{case["reduction_percent"]:.2f}% shorter for the full method on this instance</text>')
    out.append('<text x="68" y="479" class="tiny">Time: symbolic input units · visual playback speed is arbitrary · archived schedules, not hardware footage</text>')
    out.append('</svg>')
    return ''.join(out)

def main():
    fair_path=REP/'results/fair_comparison/comparison_details.jsonl'
    public_path=REP/'results/external_discrete_run01/details.jsonl'
    public_input_path=REP/'results/external_discrete_run01/frozen_cases.json'
    fair_inputs_path=REP/'results/fair_comparison/frozen_comparison_inputs.jsonl'
    fair=read_lines(fair_path); public=read_lines(public_path)
    fin={d['id']:d for d in read_lines(fair_inputs_path)}
    pin={d['id']:d for d in json.loads(public_input_path.read_text(encoding='utf-8'))}
    cases=[]
    configs=[('controlled-pour','Controlled drink preparation','pour_drink_001',fair,['full'],fair_path,
              'Controlled record pour_drink_001 · 6 nodes · 1 cooperative task',
              'This is the six-node controlled experiment, not the five-node tea illustration. The raw candidate was rejected; the animation shows only the accepted full-method schedule.'),
             ('public-cooperation','Public parallel assembly','parallel_branch_light',public,['full'],public_path,
              'AssemblyGrid parallel_branch_light · 3 operations · source-checked',
              'Two preparation operations run in parallel, then the cooperative join occupies both units. This replays the retained planning projection, not the original geometric simulator.'),
             ('resource-comparison','Resource-ordering comparison','ft06',public,['field_match_compressed','full'],public_path,
              'OR-Library ft06 two-unit projection · 36 operations · 6 resources',
              'The two methods receive the same input and share order compression. Both accepted schedules passed independent source checks. This single instance illustrates a resource-ordering difference, not general superiority or the original job-shop optimum.')]
    validations=[]
    for cid,title,rid,rows,methods,path,subtitle,note in configs:
        case={'id':cid,'title':title,'record_id':rid,'subtitle':subtitle,'note':note,'plans':[], 'sources':[]}
        for method in methods:
            matches=[d for d in rows if d['metrics']['id']==rid and d['metrics']['method']==method]
            assert len(matches)==1
            d=matches[0];assert d['metrics']['accepted']
            graph=d.get('output_graph',d.get('graph'));schedule=d['schedule']
            spec=fin[rid]['spec'] if rows is fair else {'S0':pin[rid]['S0'],'Sg':pin[rid]['Sg']}
            ga=audit_graph(graph,spec);sa=audit_schedule(graph,schedule,spec)
            assert ga['valid'] and sa['valid'],(rid,method,ga,sa)
            source_check=independent_source_audit(pin[rid],schedule) if rows is public else None
            assert source_check is None or source_check['valid']
            case['plans'].append({'method':method,'label':'Full method' if method=='full' else 'Field matching + shared compression','graph':graph,'schedule':schedule,'metrics':d['metrics']})
            case['sources'].append(source(path,rid,method))
            validations.append({'id':rid,'method':method,'graph':ga,'schedule':sa,'public_source':source_check})
        case['sources'].append(source(fair_inputs_path if rows is fair else public_input_path,rid))
        case['horizon']=max(p['schedule']['estimated_makespan'] for p in case['plans'])
        if len(methods)==2:
            a,b=[p['schedule']['estimated_makespan'] for p in case['plans']]
            case['reduction_percent']=100*(a-b)/a
        case['svg']=make_svg(case)
        cases.append(case)
    (OUT/'animations').mkdir(exist_ok=True)
    payload={'version':'v7_70','playback_seconds_per_cycle':14,'cases':cases}
    for case in cases:
        (OUT/'animations'/f'{case["id"]}.svg').write_text(make_svg(case,animated=True)+'\n',encoding='utf-8',newline='\n')
    text=json.dumps(payload,ensure_ascii=False,indent=2)
    (OUT/'data/replays.json').write_text(text+'\n',encoding='utf-8',newline='\n')
    (OUT/'data/replays.js').write_text('window.ATG_REPLAYS = '+text+';\n',encoding='utf-8',newline='\n')
    (ROOT/'documentation/replay_verification.json').write_text(json.dumps({'sources_untouched':True,'cases':validations},indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Exported 3 replay cases, 4 independently checked schedules, and 3 animated SVGs.')

if __name__=='__main__':
    main()
