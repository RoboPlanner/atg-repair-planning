"""Evaluate frozen, directly authored GPT-6 candidates; never generate/repair raw data.

Usage: python -B evaluate_batch.py --output results_v1
Use a new output directory for a reproducibility rerun. Python standard library only.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import platform
import statistics
import sys

from frozen_evaluator.schema import AtomicTaskGraph
from frozen_evaluator.pipeline import run_verified_atg
from frozen_evaluator.planning import plan_graph, critical_path_length
from frozen_evaluator.optimization import replay_accepted_events
from frozen_evaluator.verification import joint_graph_audit

ROOT = Path(__file__).resolve().parent
NODE_FIELDS = {'id', 'action', 'object', 'Pre', 'Post', 'd', 'Res', 'Cand', 'mode'}
EDGE_TYPES = {'E_state': 'state_support', 'E_sync': 'synchronization',
              'E_mutex': 'resource_mutex', 'E_order': 'order'}
ARM = {'L': 'left', 'R': 'right', 'B': 'both'}
STAGES = ['state_closure', 'synchronization', 'resource_mutex', 'compression']
GATES = ['schema_valid', 'closed', 'goal_reachable', 'acyclic',
         'synchronization_complete', 'resource_ordered']


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def dump(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify_frozen():
    pre, raw = read(ROOT / 'pre_generation_freeze.json'), read(ROOT / 'candidate_freeze.json')
    checks = {}
    for name, expected in pre['input_files'].items():
        checks[name] = sha(ROOT / name) == expected
    for name, expected in pre['code_files'].items():
        checks['frozen_evaluator/' + name] = sha(ROOT / 'frozen_evaluator' / name) == expected
    for item in raw['files']:
        checks[item['file']] = sha(ROOT / item['file']) == item['sha256']
    if not all(checks.values()):
        raise ValueError(f'Frozen file changed: {[k for k,v in checks.items() if not v]}')
    return checks


def raw_issues(candidate, spec):
    issues = []
    if set(candidate) != {'task_id', 'nodes', 'relations'}:
        issues.append('candidate top-level fields differ from protocol')
    if set(candidate['relations']) != set(EDGE_TYPES):
        issues.append('relation type keys differ from protocol')
    ids = []
    for i, node in enumerate(candidate['nodes']):
        prefix = f'node[{i}]'
        if set(node) != NODE_FIELDS:
            issues.append(f'{prefix}: not exactly nine fields')
            continue
        ids.append(node['id'])
        for field in ('id', 'action', 'object', 'mode'):
            if not isinstance(node[field], str) or not node[field].strip():
                issues.append(f'{prefix}: invalid {field}')
        for field in ('Pre', 'Post', 'Res', 'Cand'):
            value = node[field]
            if not isinstance(value, list) or any(not isinstance(x, str) or not x for x in value):
                issues.append(f'{prefix}: invalid {field}')
        d = node['d']
        if isinstance(d, bool) or not isinstance(d, (int, float)) or not math.isfinite(d) or d <= 0:
            issues.append(f'{prefix}: invalid d')
        if node['mode'] == 'cooperative':
            if node['Cand'] != ['B']:
                issues.append(f'{prefix}: cooperative Cand must be B')
        elif node['mode'] == 'single':
            if not node['Cand'] or not set(node['Cand']) <= {'L', 'R'}:
                issues.append(f'{prefix}: invalid single Cand')
        else:
            issues.append(f'{prefix}: invalid mode')
        if not set(node['Res']) <= set(spec['resources']):
            issues.append(f'{prefix}: undeclared resources {sorted(set(node["Res"]) - set(spec["resources"]))}')
    if len(set(ids)) != len(ids):
        issues.append('duplicate node IDs')
    for kind, edges in candidate['relations'].items():
        for edge in edges:
            if not isinstance(edge, list) or len(edge) != (2 if kind == 'E_order' else 3):
                issues.append(f'{kind}: malformed edge')
            elif any(not isinstance(x, str) or not x for x in edge):
                issues.append(f'{kind}: non-string edge member')
    return issues


def adapt(candidate):
    # Exact syntactic mapping: no inferred facts, extra edges, or candidate correction.
    nodes = []
    for n in candidate['nodes']:
        nodes.append({'id': n['id'], 'action': n['action'], 'object': n['object'],
                      'pre_state': n['Pre'], 'post_state': n['Post'], 'duration': n['d'],
                      'resource': n['Res'], 'candidate_arm': [ARM[x] for x in n['Cand']],
                      'mode': n['mode']})
    edges = []
    for kind, triples in candidate['relations'].items():
        for values in triples:
            e = {'source': values[0], 'target': values[1], 'type': EDGE_TYPES[kind]}
            if kind in ('E_state', 'E_sync'):
                e['state'] = values[2]
            elif kind == 'E_mutex':
                e['resource'] = values[2]
            edges.append(e)
    return {'nodes': nodes, 'edges': edges}


def exported_schedule_check(graph, schedule):
    """Check serialized output independently, including both B lanes and resources."""
    issues = []
    steps, nodes = schedule['items'], {n.id: n for n in graph.nodes}
    ids = [s['node_id'] for s in steps]
    if len(ids) != len(set(ids)) or set(ids) != set(nodes):
        issues.append('scheduled node coverage is not exact')
    by_id = {s['node_id']: s for s in steps}
    for s in steps:
        n = nodes[s['node_id']]
        start, end = s['start'], s['finish']
        if not all(math.isfinite(t) for t in (start, end)) or start < 0 or end <= start:
            issues.append(f'{n.id}: non-positive/non-finite interval')
        if not math.isclose(end - start, n.duration, abs_tol=1e-9):
            issues.append(f'{n.id}: exported duration changed')
        occ = s['executors']
        if n.mode == 'cooperative':
            if len(occ) != 2 or set(occ) != {'left', 'right'}:
                issues.append(f'{n.id}: B does not occupy L+R')
        elif len(occ) != 1 or occ[0] not in n.candidate_arm:
            issues.append(f'{n.id}: allocation not in Cand')
        if set(s['resources']) != set(n.resource):
            issues.append(f'{n.id}: declared resources changed')
    overlaps = []
    for a, b in itertools.combinations(steps, 2):
        duration = min(a['finish'], b['finish']) - max(a['start'], b['start'])
        if duration > 1e-9:
            overlaps.append([a['node_id'], b['node_id'], duration])
            if set(a['executors']) & set(b['executors']):
                issues.append(f'{a["node_id"]}/{b["node_id"]}: executor overlap')
            if set(a['resources']) & set(b['resources']):
                issues.append(f'{a["node_id"]}/{b["node_id"]}: resource overlap')
    for e in graph.edges:
        if by_id[e.source]['finish'] > by_id[e.target]['start'] + 1e-9:
            issues.append(f'{e.source}->{e.target}: precedence violated')
    end = max((s['finish'] for s in steps), default=0)
    if not math.isclose(end, schedule['estimated_makespan'], abs_tol=1e-9):
        issues.append('exported makespan mismatch')
    busy = {arm: sum(s['finish']-s['start'] for s in steps if arm in s['executors'])
            for arm in ('left', 'right')}
    return {'valid': not issues, 'issues': issues, 'overlapping_node_pairs': overlaps,
            'executor_busy_time': busy, 'utilization_unrounded': sum(busy.values())/(2*end) if end else None}


def stats(values):
    values = [x for x in values if x is not None]
    return {'n': len(values), 'mean': statistics.mean(values) if values else None,
            'sample_sd': statistics.stdev(values) if len(values) > 1 else None,
            'median': statistics.median(values) if values else None,
            'min': min(values) if values else None, 'max': max(values) if values else None,
            'sum': sum(values) if values else 0}


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for row in rows for k in row))
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', default='results_v1')
    args = parser.parse_args()
    output = ROOT / args.output
    if output.exists():
        raise FileExistsError('Use a new output directory; existing results are preserved.')
    before_hashes = verify_frozen()
    specs = read(ROOT / 'task_specs.json')
    by_spec = {s['task_id']: s for s in specs}
    candidates, file_sources = [], {}
    for entry in read(ROOT / 'candidate_freeze.json')['files']:
        for c in read(ROOT / entry['file']):
            candidates.append(c)
            file_sources[c['task_id']] = entry['file']
    ids = [c['task_id'] for c in candidates]
    assert len(ids) == 24 and len(set(ids)) == 24 and set(ids) == set(by_spec)
    candidates.sort(key=lambda c: c['task_id'])
    output.mkdir()
    (output / 'cases').mkdir()
    (output / 'raw_candidates.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in candidates), encoding='utf-8')
    rows, details, event_rows = [], [], []
    for candidate in candidates:
        task_id = candidate['task_id']
        spec = by_spec[task_id]
        detail = {'task_id': task_id, 'spec': spec, 'raw_source': file_sources[task_id],
                  'raw_candidate': candidate, 'raw_protocol_issues': raw_issues(candidate, spec)}
        row = {'task_id': task_id, 'domain': spec['domain'], 'title': spec['title'],
               'nodes': len(candidate['nodes']), 'cooperative_nodes': sum(n['mode']=='cooperative' for n in candidate['nodes']),
               'flexible_single_nodes': sum(n['mode']=='single' and len(n['Cand'])==2 for n in candidate['nodes']),
               'raw_protocol_valid': not detail['raw_protocol_issues'], 'parsed': False,
               'before_joint_valid': False, 'before_strict_accepted': False, 'full_accepted': False,
               'no_compression_accepted': False}
        for kind in EDGE_TYPES:
            row['raw_' + kind] = len(candidate['relations'][kind])
        try:
            normalized = adapt(candidate)
            graph = AtomicTaskGraph.from_dict(normalized)
            detail['normalized_input'] = normalized
            row['parsed'] = True
            initial, goals = set(spec['S0']), set(spec['Sg'])
            before = joint_graph_audit(graph, initial, goals)
            detail['before_audit'] = before.to_dict()
            row['before_joint_valid'] = before.valid
            row['before_closure_rate'] = before.state_audit.closure_rate
            row['before_parallel_pairs'] = len(graph.parallel_pairs()) if before.acyclic else None
            row['before_resource_conflict_pairs'] = len(before.resource_conflicts)
            row['serial_duration'] = sum(n.duration for n in graph.nodes)
            row['cooperative_duration'] = sum(n.duration for n in graph.nodes if n.mode=='cooperative')
            if before.valid:
                try:
                    raw_schedule = plan_graph(graph, initial_states=initial, goal_states=goals, strict=True)
                    row['before_strict_accepted'] = raw_schedule.valid
                    detail['before_schedule'] = raw_schedule.to_dict()
                    detail['before_export_check'] = exported_schedule_check(graph, raw_schedule.to_dict())
                    row['before_makespan'] = raw_schedule.makespan
                except (ValueError, KeyError, TypeError) as exc:
                    detail['before_schedule_error'] = f'{type(exc).__name__}: {exc}'
            full = run_verified_atg(graph.copy(), initial, goals)
            no_comp = run_verified_atg(graph.copy(), initial, goals, use_critical_path=False)
            detail['full'], detail['no_compression'] = full.to_dict(), no_comp.to_dict()
            row['full_accepted'], row['no_compression_accepted'] = full.accepted, no_comp.accepted
            for variant, result in [('full', full), ('no_compression', no_comp)]:
                if result.graph is not None and result.audit is not None:
                    replayed = replay_accepted_events(graph, result.audit.events)
                    identical = replayed.edge_keys() == result.graph.edge_keys() and [n.to_dict() for n in replayed.nodes] == [n.to_dict() for n in result.graph.nodes]
                    row[variant + '_replay_valid'] = identical
                    detail[variant + '_replay_graph'] = replayed.to_dict()
                    detail[variant + '_replay_valid'] = identical
                if result.schedule is not None:
                    checked = exported_schedule_check(result.graph, result.schedule.to_dict())
                    detail[variant + '_export_check'] = checked
                    row[variant + '_export_valid'] = checked['valid']
                    row[variant + '_makespan'] = result.schedule.makespan
            if full.graph is not None:
                after = joint_graph_audit(full.graph, initial, goals)
                detail['after_audit'] = after.to_dict()
                row['after_joint_valid'] = after.valid
                row['after_closure_rate'] = after.state_audit.closure_rate
                row['after_resource_conflict_pairs'] = len(after.resource_conflicts)
                row['after_parallel_pairs'] = len(full.graph.parallel_pairs()) if after.acyclic else None
                for gate in GATES:
                    row['before_' + gate] = before.to_dict()['checks'][gate]
                    row['after_' + gate] = after.to_dict()['checks'][gate]
            if full.audit is not None:
                row['accepted_events'] = sum(e.accepted for e in full.audit.events)
                row['rejected_events'] = sum(not e.accepted for e in full.audit.events)
                stage_graphs, prefix_events = {}, []
                for i, stage in enumerate(STAGES, 1):
                    stage_events = [e for e in full.audit.events if e.stage == stage]
                    prefix_events.extend(stage_events)
                    stage_graphs[f'G{i}'] = replay_accepted_events(graph, prefix_events).to_dict()
                    row[stage + '_accepted_events'] = sum(e.accepted for e in stage_events)
                    row[stage + '_rejected_events'] = sum(not e.accepted for e in stage_events)
                detail['stage_graphs_from_accepted_events'] = stage_graphs
                for i, event in enumerate(full.audit.events, 1):
                    event_rows.append({'task_id': task_id, 'event_index': i, **event.to_dict()})
            if full.accepted:
                row['speedup_vs_same_nodes_serial'] = row['serial_duration'] / full.schedule.makespan
                row['relative_duration_reduction_vs_serial'] = 1 - full.schedule.makespan / row['serial_duration']
                row['executor_utilization'] = detail['full_export_check']['utilization_unrounded']
                row['left_busy_time'] = detail['full_export_check']['executor_busy_time']['left']
                row['right_busy_time'] = detail['full_export_check']['executor_busy_time']['right']
                row['scheduled_overlap_pairs'] = len(detail['full_export_check']['overlapping_node_pairs'])
                row['critical_path_duration'] = critical_path_length(full.graph)
                if row['before_strict_accepted']:
                    row['makespan_reduction_vs_raw_strict'] = row['before_makespan'] - full.schedule.makespan
            if full.accepted and no_comp.accepted:
                row['compression_makespan_reduction'] = no_comp.schedule.makespan - full.schedule.makespan
                row['compression_graph_same'] = full.graph.edge_keys() == no_comp.graph.edge_keys()
        except (ValueError, KeyError, TypeError, OverflowError) as exc:
            detail['evaluation_error'] = f'{type(exc).__name__}: {exc}'
            row['evaluation_error'] = detail['evaluation_error']
        detail['metrics'] = row
        rows.append(row)
        details.append(detail)
        dump(output / 'cases' / f'{task_id}.json', detail)
    write_csv(output / 'per_task_metrics.csv', rows)
    write_csv(output / 'edit_events.csv', event_rows)
    metrics = ['nodes', 'cooperative_nodes', 'serial_duration', 'full_makespan',
               'speedup_vs_same_nodes_serial', 'relative_duration_reduction_vs_serial',
               'executor_utilization', 'before_parallel_pairs', 'after_parallel_pairs',
               'scheduled_overlap_pairs', 'accepted_events', 'rejected_events',
               'makespan_reduction_vs_raw_strict', 'compression_makespan_reduction']
    summary = {'records': len(rows), 'protocol_valid': sum(r['raw_protocol_valid'] for r in rows),
               'parsed': sum(r['parsed'] for r in rows), 'counts': {}, 'statistics': {},
               'gates': {}, 'domains': {}, 'event_counts': {},
               'input_edge_counts': {kind: sum(r['raw_'+kind] for r in rows) for kind in EDGE_TYPES},
               'evaluation_errors': [r for r in rows if 'evaluation_error' in r]}
    for key in ['before_joint_valid', 'before_strict_accepted', 'after_joint_valid', 'full_accepted',
                'no_compression_accepted', 'full_replay_valid', 'no_compression_replay_valid',
                'full_export_valid', 'no_compression_export_valid', 'compression_graph_same']:
        summary['counts'][key] = {'passed': sum(bool(r.get(key)) for r in rows),
                                  'evaluated': sum(key in r for r in rows), 'total': len(rows)}
    for key in metrics:
        summary['statistics'][key] = stats([r.get(key) for r in rows])
    for gate in GATES:
        summary['gates'][gate] = {when: sum(bool(r.get(when+'_'+gate)) for r in rows) for when in ('before','after')}
    for stage in STAGES:
        summary['event_counts'][stage] = {decision: sum(r.get(stage+'_'+decision+'_events',0) for r in rows) for decision in ('accepted','rejected')}
    for domain in sorted({r['domain'] for r in rows}):
        group = [r for r in rows if r['domain']==domain]
        summary['domains'][domain] = {'records': len(group), 'before_accepted': sum(r['before_strict_accepted'] for r in group),
                                      'full_accepted': sum(r['full_accepted'] for r in group),
                                      **{key: stats([r.get(key) for r in group]) for key in metrics}}
    accepted = [r for r in rows if r['full_accepted']]
    summary['pooled_serial_to_schedule_ratio'] = sum(r['serial_duration'] for r in accepted) / sum(r['full_makespan'] for r in accepted) if accepted else None
    summary['pooled_executor_utilization'] = sum(r['left_busy_time']+r['right_busy_time'] for r in accepted) / (2*sum(r['full_makespan'] for r in accepted)) if accepted else None
    summary['frozen_files_verified_after_evaluation'] = verify_frozen()
    dump(output / 'summary.json', summary)
    dump(output / 'run_provenance.json', {'evaluation_completed_utc': datetime.now(timezone.utc).isoformat(),
        'python': sys.version, 'platform': platform.platform(), 'analysis_script_sha256': sha(Path(__file__)),
        'frozen_files_verified_before_evaluation': before_hashes,
        'candidate_source': 'Current GPT-6 assistant directly authored JSON; shared method-aware session.',
        'provider_request_ids': None, 'sampling_parameters': None, 'generation_token_counts': None,
        'independent_gold_reference': False, 'duration_unit': 'symbolic input estimate',
        'no_random_candidate_generator_called': True,
        'adapter': 'nine-field name mapping plus L/R/B to left/right/both; no relational inference',
        'code_output_optional_workspace': 'Legacy internal serialization adds workspace=shared; raw nine-field records remain unchanged.'})
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
