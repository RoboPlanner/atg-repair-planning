from __future__ import annotations

import csv
from collections import defaultdict
from math import isfinite, sqrt
from pathlib import Path
from statistics import mean

from .planning import PlanTimeline, critical_path_length, plan_conflict_rate
from .schema import AtomicTaskGraph
from .verification import causal_state_audit


def _f1(pred: set[object], gold: set[object]) -> float:
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0
    tp = len(pred & gold)
    precision = tp / len(pred) if pred else 0.0
    recall = tp / len(gold) if gold else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def graph_quality(pred: AtomicTaskGraph, gold: AtomicTaskGraph) -> dict[str, float]:
    pred_nodes = {(node.id, node.action, node.object_name) for node in pred.nodes}
    gold_nodes = {(node.id, node.action, node.object_name) for node in gold.nodes}
    pred_edges = {edge.key() for edge in pred.edges if edge.type != "order"}
    gold_edges = {edge.key() for edge in gold.edges if edge.type != "order"}

    pred_map = pred.node_map
    gold_map = gold.node_map
    common = sorted(set(pred_map) & set(gold_map))
    state_hits = 0
    arm_hits = 0
    for node_id in common:
        pnode = pred_map[node_id]
        gnode = gold_map[node_id]
        if set(pnode.pre_state) == set(gnode.pre_state) and set(pnode.post_state) == set(gnode.post_state):
            state_hits += 1
        if set(pnode.candidate_arm) == set(gnode.candidate_arm):
            arm_hits += 1

    topo_errors = 0
    try:
        pred.topological_order()
    except ValueError:
        topo_errors += 1
    for edge in pred.edges:
        if edge.source not in pred_map or edge.target not in pred_map:
            topo_errors += 1

    denominator = max(1, len(gold.nodes))
    return {
        "Node F1": _f1(pred_nodes, gold_nodes),
        "Edge F1": _f1(pred_edges, gold_edges),
        "State Acc": state_hits / max(1, len(gold_map)),
        "Arm-Constraint Acc": arm_hits / max(1, len(gold_map)),
        "Topo Error": topo_errors / denominator,
    }


def state_closure_rate(graph: AtomicTaskGraph, initial_states: set[str], goal_states: set[str]) -> float:
    return causal_state_audit(graph, initial_states, goal_states).closure_rate


def invalid_edge_rate(graph: AtomicTaskGraph) -> float:
    node_ids = {node.id for node in graph.nodes}
    if not graph.edges:
        return 0.0
    invalid = sum(1 for edge in graph.edges if edge.source not in node_ids or edge.target not in node_ids)
    return invalid / len(graph.edges)


def has_cycle(graph: AtomicTaskGraph) -> bool:
    try:
        graph.topological_order()
    except ValueError:
        return True
    return False


def unreachable_goal_rate(graph: AtomicTaskGraph, initial_states: set[str], goal_states: set[str]) -> float:
    if not goal_states:
        return 0.0
    audit = causal_state_audit(graph, initial_states, goal_states)
    return len(audit.unreachable_goals) / len(goal_states)


def parallel_prf(
    true_positive: int, predicted_count: int, reference_count: int
) -> dict[str, float | None]:
    """Shared per-record and pooled convention; undefined values stay None.

    Precision is undefined with no prediction. Recall and F1 are inapplicable
    with an empty reference. A missed nonempty reference has recall/F1 zero.
    """
    if min(true_positive, predicted_count, reference_count) < 0 or true_positive > min(
        predicted_count, reference_count
    ):
        raise ValueError("inconsistent parallel-pair counts")
    precision = true_positive / predicted_count if predicted_count else None
    recall = true_positive / reference_count if reference_count else None
    f1 = 2 * true_positive / (predicted_count + reference_count) if reference_count else None
    return {"Parallel Precision": precision, "Parallel Recall": recall, "Parallel F1": f1}


def dependency_safety(
    pred: AtomicTaskGraph,
    gold: AtomicTaskGraph,
    plan: PlanTimeline,
) -> dict[str, float | int | None]:
    pred_edges = {edge.key() for edge in pred.edges if edge.type != "order"}
    gold_edges = {edge.key() for edge in gold.edges if edge.type != "order"}
    missing = len(gold_edges - pred_edges) / max(1, len(gold_edges))

    parallel_pairs = {tuple(sorted(pair)) for pair in pred.parallel_pairs()}
    gold_parallel = {tuple(sorted(pair)) for pair in gold.parallel_pairs()}
    true_parallel = len(parallel_pairs & gold_parallel)
    false_parallel = len(parallel_pairs - gold_parallel)
    missed_parallel = len(gold_parallel - parallel_pairs)
    parallel_scores = parallel_prf(true_parallel, len(parallel_pairs), len(gold_parallel))
    return {
        "Missing Dependency": missing,
        "False Parallel": false_parallel / len(parallel_pairs) if parallel_pairs else None,
        "Conflict Rate": plan_conflict_rate(plan),
        **parallel_scores,
        "Predicted Parallel Pairs": len(parallel_pairs),
        "Reference Parallel Pairs": len(gold_parallel),
        "True Parallel Pairs": true_parallel,
        "False Parallel Pairs": false_parallel,
        "Missed Parallel Pairs": missed_parallel,
        # Backward-compatible alias. It is undefined when no pair is predicted.
        "Safe Parallel Ratio": parallel_scores["Parallel Precision"],
    }


def plan_efficiency(graph: AtomicTaskGraph, plan: PlanTimeline, sequential_makespan: float) -> dict[str, float]:
    return {
        "Critical Path": critical_path_length(graph),
        "Waiting Time": plan.waiting_time,
        "Executor Utilization": plan.executor_utilization,
        "Estimated Makespan": plan.makespan,
        "Speedup": sequential_makespan / plan.makespan if plan.makespan else 0.0,
        "Sync Stability": plan.sync_stability,
    }


def summarize(rows: list[dict[str, object]], group_key: str, metric_keys: list[str]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        grouped[str(row[group_key])].append(row)
    output: list[dict[str, object]] = []
    for group, items in grouped.items():
        summary: dict[str, object] = {group_key: group}
        for key in metric_keys:
            values: list[float] = []
            for item in items:
                value = item.get(key)
                if value is None or value == "":
                    continue
                numeric = float(value)
                if isfinite(numeric):
                    values.append(numeric)
            if not values:
                summary[key] = ""
                summary[f"{key} Std"] = ""
                continue
            avg = mean(values)
            if len(values) > 1:
                var = sum((value - avg) ** 2 for value in values) / (len(values) - 1)
                std = sqrt(var)
            else:
                std = 0.0
            summary[key] = round(avg, 4)
            summary[f"{key} Std"] = round(std, 4)
        output.append(summary)
    return output


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        return
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
