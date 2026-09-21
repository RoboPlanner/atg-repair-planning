"""Independent read-only verification and report construction from saved results.

No import from frozen_evaluator; originals and evaluation outputs are preserved.
"""
from collections import Counter
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import statistics

ROOT = Path(__file__).resolve().parent
RESULTS = ROOT / 'results_v1'
REPORTS = ROOT / 'reports_v1'
DOMAINS = {'assembly':'装配', 'packaging':'包装', 'inspection':'检测',
           'warehouse':'仓储', 'sorting':'分拣', 'workcell_preparation':'工位准备'}


def read(p):
    return json.loads(p.read_text(encoding='utf-8-sig'))


def keys(graph):
    return {(e['source'], e['target'], e['type'], e.get('state'), e.get('resource')) for e in graph['edges']}


def audit_graph(graph, spec):
    nodes = {n['id']: n for n in graph['nodes']}
    edges = graph['edges']
    issues, successors = [], {n:set() for n in nodes}
    supports, sync = set(), set()
    for e in edges:
        u, v = e['source'], e['target']
        if u not in nodes or v not in nodes or u == v:
            issues.append('invalid endpoint')
            continue
        successors[u].add(v)
        if e['type'] in ('state_support', 'synchronization'):
            state = e.get('state')
            if state not in nodes[u]['post_state'] or state not in nodes[v]['pre_state']:
                issues.append('invalid state label')
            (supports if e['type']=='state_support' else sync).add((u,v,state))
        if e['type']=='resource_mutex':
            if e.get('resource') not in set(nodes[u]['resource']) & set(nodes[v]['resource']):
                issues.append('invalid resource label')
    expected = {(u,v,s) for u,v,s in supports if nodes[v]['mode']=='cooperative'}
    if sync != expected:
        issues.append('sync is not exact matching support set')
    reach = {u:set(vs) for u,vs in successors.items()}
    for middle in nodes:
        for start in nodes:
            if middle in reach[start]:
                reach[start].update(reach[middle])
    if any(n in reach[n] for n in nodes):
        issues.append('cycle')
    for u,v in itertools.combinations(nodes, 2):
        if set(nodes[u]['resource']) & set(nodes[v]['resource']) and v not in reach[u] and u not in reach[v]:
            issues.append(f'unordered resource pair {u}/{v}')
    remaining, order = set(nodes), []
    while remaining:
        ready = sorted(n for n in remaining if not any(n in successors[u] for u in remaining))
        if not ready:
            issues.append('topological sorting failed')
            break
        order.extend(ready)
        remaining.difference_update(ready)
    available, completed = set(spec['S0']), set()
    for nid in order:
        node = nodes[nid]
        for state in node['pre_state']:
            if state not in available:
                issues.append(f'{nid}: state not available {state}')
            if state not in spec['S0'] and not any(v==nid and s==state and u in completed for u,v,s in supports):
                issues.append(f'{nid}: state support not executable {state}')
        available.update(node['post_state'])
        completed.add(nid)
    if not set(spec['Sg']) <= available:
        issues.append('goal missing')
    return {'valid': not issues, 'issues': issues, 'topological_order': order}


def audit_schedule(graph, schedule, spec):
    nodes = {n['id']:n for n in graph['nodes']}
    steps = schedule['items']
    issues, stepmap = [], {s['node_id']:s for s in steps}
    if len(stepmap)!=len(steps) or set(stepmap)!=set(nodes):
        issues.append('node coverage')
    for s in steps:
        node = nodes[s['node_id']]
        if not math.isclose(s['finish']-s['start'],node['duration'],abs_tol=1e-9) or s['finish']<=s['start'] or s['start']<0:
            issues.append('duration/interval')
        if node['mode']=='cooperative':
            valid = len(s['executors'])==2 and set(s['executors'])=={'left','right'}
        else:
            valid = len(s['executors'])==1 and s['executors'][0] in node['candidate_arm']
        if not valid:
            issues.append('executor allocation')
        if set(s['resources'])!=set(node['resource']):
            issues.append('resource coverage')
        available = set(spec['S0'])
        for previous in steps:
            if previous['finish']<=s['start']:
                available.update(nodes[previous['node_id']]['post_state'])
        if not set(node['pre_state'])<=available:
            issues.append(f'{s["node_id"]}: precondition false at start')
    for a,b in itertools.combinations(steps,2):
        if min(a['finish'],b['finish'])>max(a['start'],b['start']):
            if set(a['executors'])&set(b['executors']):
                issues.append('executor overlap')
            if set(a['resources'])&set(b['resources']):
                issues.append('resource overlap')
    for edge in graph['edges']:
        if stepmap[edge['source']]['finish']>stepmap[edge['target']]['start']:
            issues.append('edge precedence')
    if schedule['estimated_makespan'] != max(s['finish'] for s in steps):
        issues.append('makespan')
    return {'valid':not issues, 'issues':issues}


def main():
    if REPORTS.exists():
        raise FileExistsError('Reports already exist; preserve this version.')
    REPORTS.mkdir()
    cases = [read(p) for p in sorted((RESULTS/'cases').glob('*.json'))]
    summary = read(RESULTS/'summary.json')
    rows = [c['metrics'] for c in cases]
    checks, net_rows, serial_plans = {}, [], []
    all_events = []
    for c in cases:
        tid = c['task_id']
        before, after = c['normalized_input'], c['full']['graph']
        before_keys, after_keys = keys(before), keys(after)
        nets = {'task_id':tid, 'removed_full_keys':sorted(before_keys-after_keys,key=repr),
                'added_full_keys':sorted(after_keys-before_keys,key=repr)}
        net_rows.append(nets)
        before_check, after_check = audit_graph(before,c['spec']), audit_graph(after,c['spec'])
        replay = set(before_keys)
        for e in c['full']['audit']['events']:
            all_events.append(e)
            if not e['accepted']:
                continue
            k = (e['source'],e['target'],e['edge_type'],e['state'],e['resource'])
            if e['action'].startswith('remove_'):
                replay.discard(k)
            elif e['action'].startswith('add_'):
                replay.add(k)
        node_map = {n['id']:n for n in after['nodes']}
        assignment = {s['node_id']:s['executors'] for s in c['full']['schedule']['items']}
        elapsed, items = 0, []
        for nid in after_check['topological_order']:
            n = node_map[nid]
            items.append({'node_id':nid,'start':elapsed,'finish':elapsed+n['duration'],
                          'executors':assignment[nid], 'resources':n['resource']})
            elapsed += n['duration']
        serial = {'estimated_makespan':elapsed, 'items':items}
        serial_plans.append({'task_id':tid,'baseline':'same tasks and final allocation, all nodes sequential', 'schedule':serial})
        checks[tid] = {'before_graph':before_check, 'after_graph':after_check,
                       'before_schedule':audit_schedule(before,c['before_schedule'],c['spec']),
                       'full_schedule':audit_schedule(after,c['full']['schedule'],c['spec']),
                       'no_compression_schedule':audit_schedule(c['no_compression']['graph'],c['no_compression']['schedule'],c['spec']),
                       'serial_schedule':audit_schedule(after,serial,c['spec']),
                       'independent_replay_equal':replay==after_keys,
                       'full_and_raw_schedule_intervals_equal':c['before_schedule']['items']==c['full']['schedule']['items']}
    numerical_checks = {
        'node_sum':sum(len(c['raw_candidate']['nodes']) for c in cases)==summary['statistics']['nodes']['sum'],
        'makespan_mean':math.isclose(statistics.mean(c['full']['schedule']['estimated_makespan'] for c in cases),summary['statistics']['full_makespan']['mean']),
        'speedup_mean':math.isclose(statistics.mean(sum(n['d'] for n in c['raw_candidate']['nodes'])/c['full']['schedule']['estimated_makespan'] for c in cases), summary['statistics']['speedup_vs_same_nodes_serial']['mean']),
        'events_sum':len(all_events)==summary['statistics']['accepted_events']['sum']+summary['statistics']['rejected_events']['sum']}
    for value in checks.values():
        assert all(v['valid'] if isinstance(v,dict) else v for v in value.values())
    assert all(numerical_checks.values())
    verified = {'cases':checks, 'numerical_checks':numerical_checks,
                'net_changes':net_rows, 'event_actions':dict(Counter(e['action'] for e in all_events)),
                'net_added_edges':sum(len(n['added_full_keys']) for n in net_rows),
                'net_removed_edges':sum(len(n['removed_full_keys']) for n in net_rows),
                'cases_with_cooperative_nodes':sum(r['cooperative_nodes']>0 for r in rows),
                'cooperative_node_count_histogram':dict(Counter(r['cooperative_nodes'] for r in rows))}
    (REPORTS/'independent_verification.json').write_text(json.dumps(verified,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    (REPORTS/'verified_serial_baselines.jsonl').write_text(''.join(json.dumps(s,ensure_ascii=False)+'\n' for s in serial_plans),encoding='utf-8')
    # A short spreadsheet-friendly summary; no unmeasured accuracy or timing values.
    domain_rows = []
    for domain, label in DOMAINS.items():
        d = summary['domains'][domain]
        domain_rows.append({'任务域':label,'任务数':d['records'],'节点总数':d['nodes']['sum'],
                           '修复前严格接受':d['before_accepted'],'修复后严格接受':d['full_accepted'],
                           '符号时长均值':d['full_makespan']['mean'],
                           '相同节点串行基线加速比均值':d['speedup_vs_same_nodes_serial']['mean'],
                           '双单元利用率均值':d['executor_utilization']['mean']})
    with (REPORTS/'分任务域统计.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w = csv.DictWriter(f,fieldnames=list(domain_rows[0])); w.writeheader(); w.writerows(domain_rows)
    # Human-readable catalogue keeps all original nine fields and relation labels.
    catalogue = ['# 当前会话 GPT-6 任务规划全集（24份冻结候选）','',
                 '候选直接由本次 GPT-6 助手编写。下表转写冻结 JSON，不改变节点、状态、资源、候选单元或边。d 的单位为符号输入时间。每任务附严格调度供逐项核查；形式接受不等于实际操作已验证。','']
    for c in cases:
        spec, raw = c['spec'], c['raw_candidate']
        catalogue += [f'## {c["task_id"]} {spec["title"]}', '', spec['instruction'], '',
                      '**S₀**：'+', '.join(spec['S0']), '', '**Sg**：'+', '.join(spec['Sg']), '',
                      '**容量1资源**：'+', '.join(spec['resources']), '',
                      '| id | action | object | Pre | Post | d | Res | Cand | mode |',
                      '|---|---|---|---|---|---:|---|---|---|']
        for n in raw['nodes']:
            fmt = lambda v: '{'+', '.join(v)+'}' if isinstance(v,list) else str(v)
            catalogue.append('| '+' | '.join(fmt(n[k]).replace('|','\\|') for k in ['id','action','object','Pre','Post','d','Res','Cand','mode'])+' |')
        catalogue += ['', '**原始类型关系**', '']
        for kind, edges in raw['relations'].items():
            catalogue += [f'- {kind}：' + ('；'.join('('+', '.join(e)+')' for e in edges) if edges else '∅')]
        catalogue += ['', '**严格调度输出**（区间为左闭右开）', '', '| 节点 | 占用 | 开始 | 完成 |','|---|---|---:|---:|']
        for s in c['full']['schedule']['items']:
            occ = 'L+R' if len(s['executors'])==2 else ('L' if s['executors']==['left'] else 'R')
            catalogue.append(f'| {s["node_id"]} | {occ} | {s["start"]:g} | {s["finish"]:g} |')
        catalogue += ['', f'符号完工时间 {c["metrics"]["full_makespan"]:g}；相同节点完全串行时间 {c["metrics"]["serial_duration"]:g}；相应加速比 {c["metrics"]["speedup_vs_same_nodes_serial"]:.4f}。原始与后处理的完整标签关系集合相同。', '']
    (REPORTS/'任务规划全集_24份.md').write_text('\n'.join(catalogue)+'\n',encoding='utf-8')
    s = summary['statistics']
    report = ['# 当前会话 GPT-6 任务规划与统计分析（第一批）', '',
        '**已完成24个任务、254个节点的直接生成与实际代码评估。原始候选与后处理结果均24/24通过形式审计和严格调度。本批观察到并行调度相对完全串行基线的收益，但没有观察到关系修复带来的额外收益。**', '',
        '本批为2026-09-17当前GPT-6助手的方法知情、单会话候选接口试验。任务规格与候选均由同一助手编写，用户已明确授权使用这些生成规划作为实验输入。任务规格于09:41:14 UTC冻结，六个原始候选文件于09:59:55 UTC全部冻结，随后才运行评估。每任务一份候选；未使用随机删边，不回改、不筛除。模型身份来自本会话，未保存独立提供商API请求ID或采样参数，不能包装为可核验API benchmark。', '',
        '## 生成了哪些规划', '',
        '六类任务各4份，节点数7–16，均值10.5833、样本标准差2.4302。共254个节点，其中24个cooperative节点分布于17个任务；另外7个任务不含cooperative节点。共266条状态边、41条同步边、54条资源顺序边，E_order为空。具体内容涵盖支架装配、密封壳体、包装齐套、电气检测、托盘固定、分拣、夹具换装及工装交接等。全部原始节点严格保留九个字段。', '',
        '| 任务域 | 任务数 | 节点总数 | 严格接受：前→后 | 符号完工时间均值 | 串行基线加速比均值 | 单元利用率均值 |',
        '|---|---:|---:|---|---:|---:|---:|']
    for d in domain_rows:
        report.append(f'| {d["任务域"]} | {d["任务数"]} | {d["节点总数"]} | {d["修复前严格接受"]}/4 → {d["修复后严格接受"]}/4 | {d["符号时长均值"]:.2f} | {d["相同节点串行基线加速比均值"]:.4f} | {100*d["双单元利用率均值"]:.2f}% |')
    report += ['', '## 实际审计与重放结果', '',
        '| 指标 | 原始候选 | 完整后处理 |', '|---|---:|---:|',
        '| 九字段格式、类型与资源声明 | 24/24 | 使用同一批节点 |']
    for gate, vals in summary['gates'].items():
        report.append(f'| {gate} | {vals["before"]}/24 | {vals["after"]}/24 |')
    report += [
        '| 六项联合通过 | 24/24 | 24/24 |', '| 实际调用strict=True接受 | 24/24 | 24/24 |',
        '| 导出区间、前置状态、边时序、资源和L/R占用的独立复核 | 24/24 | 24/24 |', '',
        '最终关系集合按(source, target, type, state, resource)完整边键比较：净新增0条、净删除0条；24份输出计划的节点区间和执行单元分配也与原始图严格调度相同。日志重放24/24一致，另用不导入原验证器的脚本独立重放及核查图、时间线，仍全部通过。24个B节点均实际占用L+R，未发现B与L/R任务重叠或容量1资源重叠。', '',
        '**82条接受事件的解释必须保留**：现有同步阶段先删除41条既有同步边，再按合法状态支撑加回同样的41条边。因此82是日志操作次数，不是82处错误，也不是82条净修复关系。状态阶段、资源阶段、压缩阶段接受事件均为0；拒绝事件为0。此实现的同步集合重建有真实日志操作，但本批没有语义关系净变化。', '',
        '## 调度统计及计算口径', '',
        '所有d均为模型指定的正整数符号时间，绝非设备耗时或算法运行毫秒。串行基线使用相同节点、同一最终单元分配、合法拓扑顺序，将所有节点依次执行；共24份串行计划已单独保存并通过独立审计。记串行时间Tserial=Σd，严格调度完工时间T；加速比=Tserial/T；时长降低比例=1−T/Tserial。B的持续时间在Tserial中计一次，在L/R总忙碌占用中计两次。利用率=(L忙碌时间+R忙碌时间)/(2T)。', '',
        '| 指标 | 逐任务均值 ± 样本标准差 | 中位数 | 范围 |', '|---|---:|---:|---:|']
    for key,label,percent in [('serial_duration','完全串行时间',False),('full_makespan','严格调度完工时间',False),('speedup_vs_same_nodes_serial','相对串行的加速比',False),('relative_duration_reduction_vs_serial','相对串行的时长降低',True),('executor_utilization','双单元利用率',True)]:
        v=s[key]; scale=100 if percent else 1; suffix='%' if percent else ''
        report.append(f'| {label} | {v["mean"]*scale:.4f} ± {v["sample_sd"]*scale:.4f}{suffix} | {v["median"]*scale:.4f}{suffix} | {v["min"]*scale:.4f}–{v["max"]*scale:.4f}{suffix} |')
    report += ['',
        '逐任务平均加速比为1.2411，平均符号完工时间降低18.4861%，平均双单元利用率70.6264%。这些收益来自同一关系图上的并行执行能力，不能归因于关系修复。24任务串行时间求和为507，调度时间求和为414，两总和之比为1.2246；这与逐任务比值平均1.2411是不同统计口径。忙碌占用按总时长池化的利用率为70.4106%，也不同于逐任务平均70.6264%。各任务平均值和样本标准差仅描述本批差异，不是独立多次采样的不确定性。', '',
        '修复前后静态可并行节点对均共225对；严格计划中实际时间重叠的节点对共67对。两种计数回答不同问题：前者是图与候选单元允许的潜在配对，后者是此次调度实现的配对；不能用67/225冒充召回率。没有独立参考规划图，故不报告边F1、并行F1、precision、recall或语义正确率。', '',
        '预定对照“完整方法vs关闭顺序压缩”在24/24共同接受任务上关系集合、完工时间均一致。原始E_order全部为空，压缩阶段未被有效激发，本批不能证明压缩贡献。相对原始图严格调度的完工时间改善也为0。', '',
        '## 两份便于核查的实例', '',
        '**A01 支架与底座装配**：定位底座[L,0–2]与准备支架[R,0–2]并行；对齐支架[B,2–5]同时占用L+R；随后第一处紧固[L,5–7]、第二处紧固[R,7–9]、检查[L,9–11]、贴签[L,11–12]依次执行。d总和14，严格完工12，加速比1.1667。这个例子验证了B独占与共享扭矩工具的串行占用。', '',
        '**W02 两货位补货**：两个货位检查可并行；扫码器按A→B顺序使用；放置A与扫描B、放置B之间存在合法重叠，登记终端串行使用。d总和17，严格完工11，加速比1.5455。这是本批相对串行基线加速比最大任务，仅为观察到的最大值，不是最优性证据。', '',
        '## 对论文能补充什么，以及尚未补足什么', '',
        '可补充一组可逐项检查的当前会话GPT-6直接规划输入，展示九字段接口、同步精确配对、已表示资源约束与严格调度输出能够共同工作，且同一输入在固定代码下有可复核结果。已有受控修复实验应保留，两组回答不同问题。本批不与旧160条记录混池，也不与历史其他模型名称下的输出直接作公平横向比较。', '',
        '全部形式接受不代表24份规划具有已证实的现实语义正确性。具体例子是I02：检测节点只产生continuity_test_recorded和insulation_test_recorded，归档后直接进入合格区，未表示“检测通过”的条件或拆线步骤。S02的A合格/B返修则由任务规格直接给定，也不能算真实分类准确率。T02的“label and stow”等节点包含组合动作，操作粒度仍需独立工艺人员判断。这些原始内容已保留，没有为了通过结果而回写修正；本次定性检查也不作为独立金标准。', '',
        '因此，本批仍不能支撑通用GPT-6规划准确率100%、修复成功率提升、对其他模型的优越性、显著性、真实机器人安全性或硬件性能。模型知道方法和验证规则、规格与规划出自同一会话、每任务只有一份候选，存在明显选择和方法知情条件。需要失败输入的修复证据时，应另设预先固定协议的新实验，不把本批已接受样本改坏后当成自然LLM错误。', '',
        '可用的论文措辞为：“补充开展方法知情的当前会话GPT-6候选接口试验，覆盖六类任务的24份直接生成规划，共254个节点。全部候选在后处理前后均通过六项形式审计和严格调度，日志重放及导出占用检查均一致；相对于相同节点的完全串行基线，逐任务平均符号完工时间降低18.49%。由于候选关系集合未发生净变化，本批证据支持接口可接受性与规划层调度演示，不用于量化关系修复增益或通用语义准确率。”', '',
        '## 文件与复现', '',
        '- 原始候选：上一级raw_candidates_*.json（六个文件，原始字节与冻结哈希一致）。',
        '- 任务输入：上一级task_specs.json、common_prompt.txt、generation_protocol.md。',
        '- 逐任务候选/适配输入/审计/接受与拒绝日志/计划/G1–G4重放图：../results_v1/cases/。',
        '- 逐任务完整数值：../results_v1/per_task_metrics.csv；日志操作：../results_v1/edit_events.csv。',
        '- 人工可读规划全集：任务规划全集_24份.md；分任务域统计：分任务域统计.csv。',
        '- 不导入原验证器的独立复核：independent_verification.json；串行计划：verified_serial_baselines.jsonl。',
        '- 复现实验：在批次目录运行python -B evaluate_batch.py --output results_reproduction；需使用未存在的新目录。',
        '- 核心代码副本位于../frozen_evaluator/，数据与代码SHA-256在两份freeze.json中。本轮未改论文、原实验代码或历史数据。', '',
        '格式适配只重命名Pre/Post/d/Res/Cand并映射L/R/B，不推断或生成边。代码输出的workspace=shared为既有内部序列化附加项，不会写回原始九字段节点。']
    assert verified['cases_with_cooperative_nodes']==17
    (REPORTS/'统计分析报告_24任务.md').write_text('\n'.join(report)+'\n',encoding='utf-8')
    print(json.dumps({'independently_checked_cases':len(checks),'net_added_edges':verified['net_added_edges'],
                      'net_removed_edges':verified['net_removed_edges'],'event_actions':verified['event_actions'],
                      'cooperative_histogram':verified['cooperative_node_count_histogram'],
                      'report':str(REPORTS/'统计分析报告_24任务.md')},ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
