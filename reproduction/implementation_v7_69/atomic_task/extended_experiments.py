from __future__ import annotations

import json
import hashlib
import platform
import random
import sys
import time
from pathlib import Path
from statistics import median
from typing import Callable

from .metrics import (
    dependency_safety,
    graph_quality,
    has_cycle,
    invalid_edge_rate,
    state_closure_rate,
    summarize,
    unreachable_goal_rate,
    write_csv,
)
from .optimization import make_corrupted_graph, make_sequential_graph, optimize_graph
from .planning import plan_graph
from .schema import AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode, TaskRecord
from .verification import causal_state_audit, graph_schema_issues, joint_graph_audit


MethodGraphFn = Callable[[TaskRecord, str, int], AtomicTaskGraph]


def _node(
    node_id: str,
    action: str,
    obj: str,
    pre: list[str],
    post: list[str],
    duration: float,
    resources: list[str],
    executors: list[str],
    mode: str = "single",
) -> AtomicTaskNode:
    return AtomicTaskNode(
        id=node_id,
        action=action,
        object_name=obj,
        pre_state=pre,
        post_state=post,
        duration=duration,
        resource=resources,
        candidate_arm=executors,
        mode=mode,
    )


def _state_edges(nodes: list[AtomicTaskNode]) -> list[AtomicTaskEdge]:
    producers: dict[str, str] = {}
    for node in nodes:
        for state in node.post_state:
            producers[state] = node.id
    edges: list[AtomicTaskEdge] = []
    for node in nodes:
        for state in node.pre_state:
            source = producers.get(state)
            if source and source != node.id:
                edges.append(
                    AtomicTaskEdge(
                        source=source,
                        target=node.id,
                        type="state_support",
                        state=state,
                        reason=f"{source} produces {state} for {node.id}",
                    )
                )
    return edges


def _make_graph(nodes: list[AtomicTaskNode], extra_edges: list[AtomicTaskEdge] | None = None) -> AtomicTaskGraph:
    graph = AtomicTaskGraph(nodes=nodes, edges=[])
    for edge in _state_edges(nodes) + list(extra_edges or []):
        graph.add_edge(edge)
    return graph


def _complexity_record(node_count: int, index: int) -> TaskRecord:
    nodes = [
        _node("v1", "prepare", "workspace", ["workspace_empty"], ["workspace_ready"], 1.5, ["workspace"], ["left", "right"]),
        _node("v2", "pick", "part_a", ["part_a_available"], ["part_a_ready"], 1.8, ["part_a", "shared_table"], ["left"]),
        _node("v3", "pick", "part_b", ["part_b_available"], ["part_b_ready"], 1.8, ["part_b", "shared_table"], ["right"]),
        _node(
            "v4",
            "assemble",
            "subassembly",
            ["workspace_ready", "part_a_ready", "part_b_ready"],
            ["subassembly_ready"],
            3.5,
            ["workspace", "part_a", "part_b"],
            ["both"],
            mode="cooperative",
        ),
    ]
    initial_states = ["workspace_empty", "part_a_available", "part_b_available"]
    goal = "subassembly_ready"
    if node_count >= 6:
        nodes.extend(
            [
                _node("v5", "pick", "cover", ["cover_available"], ["cover_ready"], 1.4, ["cover"], ["right"]),
                _node(
                    "v6",
                    "close",
                    "subassembly",
                    ["subassembly_ready", "cover_ready"],
                    ["assembly_closed"],
                    2.4,
                    ["subassembly", "cover"],
                    ["both"],
                    mode="cooperative",
                ),
            ]
        )
        initial_states.append("cover_available")
        goal = "assembly_closed"
    if node_count >= 8:
        nodes.extend(
            [
                _node("v7", "label", "assembly", ["assembly_closed", "label_available"], ["assembly_labeled"], 1.2, ["label"], ["left"]),
                _node("v8", "inspect", "assembly", ["assembly_labeled"], ["assembly_inspected"], 1.6, ["assembly"], ["left", "right"]),
            ]
        )
        initial_states.append("label_available")
        goal = "assembly_inspected"
    if node_count >= 10:
        nodes.extend(
            [
                _node("v9", "package", "assembly", ["assembly_inspected", "package_available"], ["assembly_packaged"], 2.0, ["package", "assembly"], ["right"]),
                _node("v10", "verify", "package", ["assembly_packaged"], ["package_verified"], 1.3, ["package"], ["left", "right"]),
            ]
        )
        initial_states.append("package_available")
        goal = "package_verified"
    extra_edges = []
    if node_count >= 4:
        extra_edges.extend(
            [
                AtomicTaskEdge("v2", "v3", "resource_mutex", resource="shared_table", reason="parts are picked from a shared staging table"),
                AtomicTaskEdge("v1", "v4", "synchronization", state="workspace_ready", reason="cooperative assembly needs prepared workspace"),
                AtomicTaskEdge("v2", "v4", "synchronization", state="part_a_ready", reason="cooperative assembly needs part A"),
                AtomicTaskEdge("v3", "v4", "synchronization", state="part_b_ready", reason="cooperative assembly needs part B"),
            ]
        )
    if node_count >= 6:
        extra_edges.extend(
            [
                AtomicTaskEdge("v4", "v6", "synchronization", state="subassembly_ready", reason="cooperative closing needs subassembly"),
                AtomicTaskEdge("v5", "v6", "synchronization", state="cover_ready", reason="cooperative closing needs cover"),
            ]
        )
    graph = _make_graph(nodes[:node_count], extra_edges)
    return TaskRecord(
        task_id=f"complexity_{node_count}_{index:03d}",
        domain=f"complexity_{node_count}_nodes",
        instruction=f"Generate a {node_count}-node atomic task plan for preparing, assembling, and checking a tabletop product.",
        initial_state={"states": initial_states},
        goal_state={"states": [goal]},
        scene={"objects": [node.object_name for node in nodes[:node_count]], "executor_labels": ["left", "right", "both"]},
        gold_graph=graph,
    )


def _json_schema_pass(graph: AtomicTaskGraph) -> bool:
    return not graph_schema_issues(graph)


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def _parallel_pair_set(graph: AtomicTaskGraph) -> set[tuple[str, str]]:
    return {tuple(sorted(pair)) for pair in graph.parallel_pairs()}


def _parallel_f1(graph: AtomicTaskGraph, gold: AtomicTaskGraph) -> float | None:
    plan = plan_graph(graph)
    value = dependency_safety(graph, gold, plan)["Parallel F1"]
    return float(value) if value is not None else None


def _plan_consistency(reference: AtomicTaskGraph, candidate: AtomicTaskGraph) -> float:
    ref = _parallel_pair_set(reference)
    cand = _parallel_pair_set(candidate)
    if not ref and not cand:
        return 1.0
    if not ref or not cand:
        return 0.0
    return len(ref & cand) / len(ref | cand)


def run_format_validity(
    records: list[TaskRecord],
    output_dir: Path,
    method_graph: MethodGraphFn,
    methods: list[str],
) -> Path:
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        initial = set(record.initial_state.get("states", []))
        goal = set(record.goal_state.get("states", []))
        for method in methods:
            graph = method_graph(record, method, index)
            try:
                encoded = json.dumps(graph.to_dict())
                AtomicTaskGraph.from_dict(json.loads(encoded))
                json_valid = 1.0
            except Exception:
                json_valid = 0.0
            rows.append(
                {
                    "task_id": record.task_id,
                    "Method": method,
                    "JSON Valid Rate": json_valid,
                    "Schema Pass Rate": 1.0 if _json_schema_pass(graph) else 0.0,
                    "Cycle Rate": 1.0 if has_cycle(graph) else 0.0,
                    "Unreachable Goal Rate": unreachable_goal_rate(graph, initial, goal),
                    "State Closure Rate": state_closure_rate(graph, initial, goal),
                    "Invalid Edge Rate": invalid_edge_rate(graph),
                }
            )
    table = summarize(
        rows,
        "Method",
        [
            "JSON Valid Rate",
            "Schema Pass Rate",
            "Cycle Rate",
            "Unreachable Goal Rate",
            "State Closure Rate",
            "Invalid Edge Rate",
        ],
    )
    path = output_dir / "tables" / "table5_format_validity_diagnostic.csv"
    write_csv(path, table)
    return path


def _joint_audit_challenge_graph(
    graph: AtomicTaskGraph,
    challenge: str,
    initial_states: set[str],
    goal_states: set[str],
) -> tuple[AtomicTaskGraph, set[str]]:
    challenged = graph.copy()
    challenged_goals = set(goal_states)

    if challenge == "Schema-invalid executor label":
        challenged.nodes[0].candidate_arm = ["invalid-executor"]
    elif challenge == "Open precondition":
        challenged.nodes[0].pre_state.append("audit_missing_state")
    elif challenge == "Directed cycle":
        base_edge = challenged.edges[0]
        challenged.add_edge(
            AtomicTaskEdge(
                source=base_edge.target,
                target=base_edge.source,
                type="order",
                reason="controlled cycle challenge",
            )
        )
    elif challenge == "Missing synchronization":
        node_map = challenged.node_map
        state_support_keys = {
            (edge.source, edge.target, edge.state)
            for edge in challenged.edges
            if edge.type == "state_support"
        }
        sync_edges = [
            edge
            for edge in challenged.edges
            if edge.type == "synchronization"
            and (edge.source, edge.target, edge.state) in state_support_keys
            and (
                node_map[edge.target].mode == "cooperative"
                or "both" in node_map[edge.target].candidate_arm
            )
        ]
        if not sync_edges:
            raise ValueError("controlled synchronization challenge requires a state-matched synchronization edge")
        challenged.remove_edge(sync_edges[0])
    elif challenge == "Wrong state-support label":
        supports = [edge for edge in challenged.edges if edge.type == "state_support"]
        if not supports:
            raise ValueError("controlled state-label challenge requires a state-support edge")
        edge = supports[0]
        challenged.remove_edge(edge)
        challenged.add_edge(
            AtomicTaskEdge(
                edge.source,
                edge.target,
                "state_support",
                state="audit_wrong_state",
                reason="controlled wrong state label",
            )
        )
    elif challenge == "Orphan synchronization":
        source, target = challenged.nodes[0].id, challenged.nodes[-1].id
        challenged.add_edge(
            AtomicTaskEdge(
                source,
                target,
                "synchronization",
                state="audit_orphan_sync",
                reason="controlled orphan synchronization",
            )
        )
    elif challenge == "Invalid resource label":
        resource_edges = [edge for edge in challenged.edges if edge.type == "resource_mutex"]
        edge = resource_edges[0] if resource_edges else AtomicTaskEdge(
            challenged.nodes[0].id,
            challenged.nodes[-1].id,
            "resource_mutex",
        )
        if resource_edges:
            challenged.remove_edge(edge)
        challenged.add_edge(
            AtomicTaskEdge(
                edge.source,
                edge.target,
                "resource_mutex",
                resource="audit_wrong_resource",
                reason="controlled wrong resource label",
            )
        )
    elif challenge == "Unordered shared resource":
        if not initial_states:
            raise ValueError("controlled resource challenge requires an initial state")
        ready_state = sorted(initial_states)[0]
        challenged.nodes.extend(
            [
                _node(
                    "audit_left",
                    "audit",
                    "left token",
                    [ready_state],
                    ["audit_left_done"],
                    1.0,
                    ["audit_shared_resource"],
                    ["left"],
                ),
                _node(
                    "audit_right",
                    "audit",
                    "right token",
                    [ready_state],
                    ["audit_right_done"],
                    1.0,
                    ["audit_shared_resource"],
                    ["right"],
                ),
            ]
        )
    elif challenge == "Unreachable goal":
        challenged_goals.add("audit_unreachable_goal")
    elif challenge != "Valid refined ATG":
        raise ValueError(f"unknown joint-audit challenge: {challenge}")

    return challenged, challenged_goals


def run_joint_audit_challenge(
    records: list[TaskRecord],
    output_dir: Path,
    *,
    structure_seed: int = 0,
) -> Path:
    challenges = [
        "Valid refined ATG",
        "Schema-invalid executor label",
        "Open precondition",
        "Directed cycle",
        "Missing synchronization",
        "Wrong state-support label",
        "Orphan synchronization",
        "Invalid resource label",
        "Unordered shared resource",
        "Unreachable goal",
    ]
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        refined = optimize_graph(
            make_corrupted_graph(
                record.gold_graph,
                "llm_schema",
                seed=structure_seed * 100_000 + 13000 + index,
            ),
            initial_states=initial,
            goal_states=goals,
        )
        for challenge in challenges:
            graph, challenged_goals = _joint_audit_challenge_graph(
                refined,
                challenge,
                initial,
                goals,
            )
            audit = joint_graph_audit(graph, initial, challenged_goals)
            rows.append(
                {
                    "task_id": record.task_id,
                    "Challenge": challenge,
                    "Schema Pass": float(audit.schema_valid),
                    "Closure Pass": float(audit.closure_valid),
                    "Goal Pass": float(audit.goal_reachable),
                    "Acyclic Pass": float(audit.acyclic),
                    "Sync Pass": float(audit.synchronization_complete),
                    "Resource Pass": float(audit.resource_ordered),
                    "Joint Accept": float(audit.valid),
                }
            )

    metrics = [
        "Schema Pass",
        "Closure Pass",
        "Goal Pass",
        "Acyclic Pass",
        "Sync Pass",
        "Resource Pass",
        "Joint Accept",
    ]
    table: list[dict[str, object]] = []
    for challenge in challenges:
        selected = [row for row in rows if row["Challenge"] == challenge]
        table.append(
            {
                "Challenge": challenge,
                "N": len(selected),
                **{
                    metric: sum(float(row[metric]) for row in selected) / len(selected)
                    for metric in metrics
                },
            }
        )

    detailed = output_dir / "tables" / "table5_joint_audit_challenge_detailed.csv"
    write_csv(detailed, rows)
    path = output_dir / "tables" / "table5_joint_audit_challenge.csv"
    write_csv(path, table)
    return path


def run_complexity_experiment(output_dir: Path, *, structure_seed: int = 0) -> Path:
    rows: list[dict[str, object]] = []
    warmup_runs = 10
    measured_runs = 50
    methods = ["Direct Candidate Graph", "Schema-Constrained Candidate", "Verified ATG (Ours)"]
    profile = {
        "Direct Candidate Graph": "llm_direct",
        "Schema-Constrained Candidate": "llm_schema",
    }
    for node_count in [4, 6, 8, 10]:
        for sample_idx in range(1, 7):
            record = _complexity_record(node_count, sample_idx)
            initial = set(record.initial_state.get("states", []))
            goals = set(record.goal_state.get("states", []))
            for method in methods:
                def run_once() -> AtomicTaskGraph:
                    if method == "Verified ATG (Ours)":
                        candidate = make_corrupted_graph(
                            record.gold_graph,
                            "llm_schema",
                            seed=structure_seed * 100_000 + node_count * 100 + sample_idx,
                        )
                        result = optimize_graph(
                            candidate,
                            initial_states=initial,
                            goal_states=goals,
                        )
                    else:
                        result = make_corrupted_graph(
                            record.gold_graph,
                            profile[method],
                            seed=structure_seed * 100_000 + node_count * 100 + sample_idx,
                        )
                    plan_graph(
                        result,
                        initial_states=initial,
                        goal_states=goals,
                        strict=method == "Verified ATG (Ours)",
                    )
                    return result

                for _ in range(warmup_runs):
                    run_once()
                timings: list[float] = []
                graph = record.gold_graph
                for _ in range(measured_runs):
                    start = time.perf_counter()
                    graph = run_once()
                    timings.append((time.perf_counter() - start) * 1000.0)
                elapsed_ms = median(timings)
                quality = graph_quality(graph, record.gold_graph)
                rows.append(
                    {
                        "Complexity Setting": f"{node_count} nodes / {method}",
                        "Node Bucket": f"{node_count} nodes",
                        "Method": method,
                        "Edge F1": quality["Edge F1"],
                        "Topo Error": quality["Topo Error"],
                        "Parallel F1": _parallel_f1(graph, record.gold_graph),
                        "Planning Time": elapsed_ms,
                    }
                )
    table = summarize(rows, "Complexity Setting", ["Edge F1", "Topo Error", "Parallel F1", "Planning Time"])
    detailed = output_dir / "tables" / "table6_complexity_detailed.csv"
    write_csv(detailed, rows)
    environment = {
        "python_version": sys.version,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "clock": "time.perf_counter",
        "warmup_runs_per_instance_method": warmup_runs,
        "measured_runs_per_instance_method": measured_runs,
        "reported_instance_statistic": "median elapsed milliseconds",
        "reference_graphs_per_bucket": 1,
        "candidate_perturbation_replicates_per_bucket": 6,
        "structure_seed": structure_seed,
        "candidate_seed_formula": "structure_seed*100000 + node_count*100 + sample_idx",
        "node_buckets": [4, 6, 8, 10],
    }
    environment_path = output_dir / "analysis" / "runtime_environment.json"
    environment_path.parent.mkdir(parents=True, exist_ok=True)
    environment_path.write_text(json.dumps(environment, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    path = output_dir / "tables" / "table6_complexity.csv"
    write_csv(path, table)
    return path


def _apply_annotation_perturbation(graph: AtomicTaskGraph, perturbation: str, seed: int) -> AtomicTaskGraph:
    output = graph.copy()
    rng = random.Random(seed)
    if perturbation in {"state-edge deletion", "combined"}:
        candidates = [edge for edge in output.edges if edge.type in {"state_support", "synchronization"}]
        if candidates:
            output.remove_edge(candidates[rng.randrange(len(candidates))])
    if perturbation in {"resource omission", "combined"}:
        candidates = [node for node in output.nodes if len(node.resource) > 1]
        if candidates:
            node = candidates[rng.randrange(len(candidates))]
            node.resource = node.resource[:-1]
    if perturbation in {"precondition deletion", "combined"}:
        candidates = [node for node in output.nodes if len(node.pre_state) > 1]
        if candidates:
            node = candidates[rng.randrange(len(candidates))]
            node.pre_state = node.pre_state[:-1]
    if perturbation in {"executor-label change", "combined"}:
        candidates = [
            node
            for node in output.nodes
            if node.candidate_arm and node.mode != "cooperative" and "both" not in node.candidate_arm
        ]
        if candidates:
            node = candidates[rng.randrange(len(candidates))]
            alternatives = [
                value
                for value in (["left"], ["right"], ["left", "right"])
                if set(value) != set(node.candidate_arm)
            ]
            node.candidate_arm = alternatives[rng.randrange(len(alternatives))]
    return output


def run_robustness_experiment(
    records: list[TaskRecord],
    output_dir: Path,
    *,
    structure_seed: int = 0,
) -> Path:
    perturbations = [
        "state-edge deletion",
        "resource omission",
        "precondition deletion",
        "executor-label change",
        "combined",
    ]
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        reference_graph = optimize_graph(
            record.gold_graph,
            initial_states=initial,
            goal_states=goals,
        )
        for perturbation in perturbations:
            candidate = _apply_annotation_perturbation(
                record.gold_graph,
                perturbation,
                seed=structure_seed * 100_000 + index + 101,
            )
            candidate_plan = plan_graph(
                candidate,
                initial_states=initial,
                goal_states=goals,
                strict=False,
            )
            candidate_quality = graph_quality(candidate, record.gold_graph)
            candidate_safety = dependency_safety(candidate, record.gold_graph, candidate_plan)
            candidate_audit = causal_state_audit(candidate, initial, goals)
            candidate_joint = joint_graph_audit(candidate, initial, goals)
            graph = optimize_graph(candidate, initial_states=initial, goal_states=goals)
            plan = plan_graph(graph, initial_states=initial, goal_states=goals, strict=True)
            quality = graph_quality(graph, record.gold_graph)
            safety = dependency_safety(graph, record.gold_graph, plan)
            state_audit = causal_state_audit(graph, initial, goals)
            common = sorted(set(graph.node_map) & set(record.gold_graph.node_map))
            resource_acc = sum(
                set(graph.node_map[node_id].resource) == set(record.gold_graph.node_map[node_id].resource)
                for node_id in common
            ) / max(1, len(common))
            executor_effective = any(
                set(candidate.node_map[node_id].candidate_arm)
                != set(record.gold_graph.node_map[node_id].candidate_arm)
                for node_id in common
            )
            rows.append(
                {
                    "Perturbation": perturbation,
                    "task_id": record.task_id,
                    "Node F1": quality["Node F1"],
                    "Edge F1 Before": candidate_quality["Edge F1"],
                    "Edge F1": quality["Edge F1"],
                    "State Acc": quality["State Acc"],
                    "Resource Acc": resource_acc,
                    "Executor Acc": quality["Arm-Constraint Acc"],
                    "State Closure Before": candidate_audit.closure_rate,
                    "State Closure After": state_audit.closure_rate,
                    "False Parallel Before": candidate_safety["False Parallel"],
                    "False Parallel After": safety["False Parallel"],
                    "Parallel F1 Before": candidate_safety["Parallel F1"],
                    "Parallel F1 After": safety["Parallel F1"],
                    "Input Joint Accept": float(candidate_joint.valid),
                    "Verifier Accepts": 1.0
                    if joint_graph_audit(graph, initial, goals).valid
                    else 0.0,
                    "Perturbation Effective": float(candidate.to_dict() != record.gold_graph.to_dict()),
                    "Executor Perturbation Effective": float(executor_effective)
                    if perturbation in {"executor-label change", "combined"}
                    else None,
                    "Plan Consistency": _plan_consistency(reference_graph, graph),
                    "Goal Closure Rate": 1.0
                    - unreachable_goal_rate(
                        graph,
                        initial,
                        goals,
                    ),
                }
            )
    table = summarize(
        rows,
        "Perturbation",
        [
            "Node F1",
            "Edge F1",
            "State Acc",
            "Resource Acc",
            "Executor Acc",
            "Parallel F1 After",
            "Input Joint Accept",
            "Verifier Accepts",
            "Perturbation Effective",
            "Executor Perturbation Effective",
            "Plan Consistency",
            "Goal Closure Rate",
        ],
    )
    detailed = output_dir / "tables" / "table7_robustness_detailed.csv"
    write_csv(detailed, rows)
    path = output_dir / "tables" / "table7_robustness.csv"
    write_csv(path, table)
    return path


def _unsafe_parallel_pairs(graph: AtomicTaskGraph, gold: AtomicTaskGraph) -> set[tuple[str, str]]:
    output: set[tuple[str, str]] = set()
    gold_parallel = {tuple(sorted(pair)) for pair in gold.parallel_pairs()}
    for left, right in graph.parallel_pairs():
        if tuple(sorted((left, right))) not in gold_parallel:
            output.add(tuple(sorted((left, right))))
    return output


def run_case_analysis(
    records: list[TaskRecord],
    output_dir: Path,
    *,
    structure_seed: int = 0,
) -> Path:
    case_dir = output_dir / "cases"
    case_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records[:4]):
        noisy = make_corrupted_graph(
            record.gold_graph,
            "llm_schema",
            seed=structure_seed * 100_000 + index + 37,
        )
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        optimized = optimize_graph(noisy, initial_states=initial, goal_states=goals)
        plan = plan_graph(optimized, initial_states=initial, goal_states=goals, strict=True)
        removed_false_parallel = sorted(_unsafe_parallel_pairs(noisy, record.gold_graph) - _unsafe_parallel_pairs(optimized, record.gold_graph))
        released_parallel = sorted(_parallel_pair_set(optimized) - _parallel_pair_set(make_sequential_graph(record.gold_graph)))
        row = {
            "task_id": record.task_id,
            "domain": record.domain,
            "instruction": record.instruction,
            "initial_state": record.initial_state,
            "goal_state": record.goal_state,
            "optimized_graph": optimized.to_dict(),
            "plan": plan.to_dict(),
            "removed_false_parallel": removed_false_parallel,
            "released_parallel_pairs": released_parallel,
        }
        rows.append(row)
        report = case_dir / f"{record.task_id}.md"
        lines = [
            f"# {record.task_id}",
            "",
            f"Instruction: {record.instruction}",
            "",
            "## Atomic Nodes",
        ]
        for node in optimized.nodes:
            lines.append(f"- {node.id}: {node.action}({node.object_name}), pre={node.pre_state}, post={node.post_state}, executors={node.candidate_arm}, resources={node.resource}")
        lines.append("")
        lines.append("## Optimized Edges")
        for edge in optimized.edges:
            lines.append(f"- {edge.source} -> {edge.target}: {edge.type}, state={edge.state}, resource={edge.resource}")
        lines.append("")
        lines.append("## Parallel Plan")
        for item in plan.items:
            lines.append(f"- {item.node_id}: {item.start:.2f} -> {item.finish:.2f}, executors={item.executors}, resources={item.resources}")
        lines.append("")
        lines.append(f"Removed false-parallel pairs: {removed_false_parallel}")
        lines.append(f"Released parallel pairs: {released_parallel}")
        report.write_text("\n".join(lines) + "\n", encoding="utf-8")
    path = output_dir / "cases" / "case_summary.jsonl"
    _write_jsonl(path, rows)
    return path


def _failure_counts(graph: AtomicTaskGraph, gold: AtomicTaskGraph, record: TaskRecord) -> dict[str, int]:
    plan = plan_graph(
        graph,
        initial_states=set(record.initial_state.get("states", [])),
        goal_states=set(record.goal_state.get("states", [])),
        strict=False,
    )
    pred_edges = {edge.key() for edge in graph.edges if edge.type != "order"}
    gold_edges = {edge.key() for edge in gold.edges if edge.type != "order"}
    wrong_executor = 0
    for node_id, gold_node in gold.node_map.items():
        pred_node = graph.node_map.get(node_id)
        if pred_node is not None and set(pred_node.candidate_arm) != set(gold_node.candidate_arm):
            wrong_executor += 1
    over_serial = 0
    for edge in graph.edges:
        if edge.type != "order":
            continue
        left = graph.node_map.get(edge.source)
        right = graph.node_map.get(edge.target)
        if left is None or right is None:
            continue
        no_state_link = not bool(set(left.post_state) & set(right.pre_state))
        no_resource_link = not bool(set(left.resource) & set(right.resource))
        if no_state_link and no_resource_link:
            over_serial += 1
    return {
        "missing state dependency": len(gold_edges - pred_edges),
        "false parallel": len(_unsafe_parallel_pairs(graph, gold)),
        "wrong executor constraint": wrong_executor,
        "resource conflict": 1 if dependency_safety(graph, gold, plan)["Conflict Rate"] > 0 else 0,
        "unreachable goal": 1
        if unreachable_goal_rate(graph, set(record.initial_state.get("states", [])), set(record.goal_state.get("states", []))) > 0
        else 0,
        "over-conservative serialization": over_serial,
    }


def run_failure_analysis(records: list[TaskRecord], output_dir: Path, method_graph: MethodGraphFn, methods: list[str]) -> Path:
    rows: list[dict[str, object]] = []
    examples: list[dict[str, object]] = []
    for index, record in enumerate(records):
        for method in methods:
            graph = method_graph(record, method, index)
            counts = _failure_counts(graph, record.gold_graph, record)
            for failure_type, count in counts.items():
                rows.append({"Method": method, "Failure Type": failure_type, "Count": count})
                if count and len(examples) < 30:
                    examples.append({"task_id": record.task_id, "method": method, "failure_type": failure_type, "count": count})
    grouped: dict[tuple[str, str], int] = {}
    for row in rows:
        key = (str(row["Method"]), str(row["Failure Type"]))
        grouped[key] = grouped.get(key, 0) + int(row["Count"])
    summary = [{"Method": method, "Failure Type": failure_type, "Count": count} for (method, failure_type), count in sorted(grouped.items())]
    path = output_dir / "analysis" / "failure_summary.csv"
    write_csv(path, summary)
    _write_jsonl(output_dir / "analysis" / "failure_examples.jsonl", examples)
    return path


def run_rule_based_diagnostics(
    records: list[TaskRecord],
    output_dir: Path,
    *,
    structure_seed: int = 0,
) -> Path:
    rows: list[dict[str, object]] = []
    for index, record in enumerate(records[:12]):
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        graph = optimize_graph(
            make_corrupted_graph(
                record.gold_graph,
                "llm_schema",
                seed=structure_seed * 100_000 + index + 37,
            ),
            initial_states=initial,
            goal_states=goals,
        )
        plan = plan_graph(graph, initial_states=initial, goal_states=goals, strict=True)
        quality = graph_quality(graph, record.gold_graph)
        safety = dependency_safety(graph, record.gold_graph, plan)
        goal_closure = 1.0 - unreachable_goal_rate(
            graph,
            set(record.initial_state.get("states", [])),
            set(record.goal_state.get("states", [])),
        )
        rows.append(
            {
                "task_id": record.task_id,
                "Node F1": quality["Node F1"],
                "Edge F1": quality["Edge F1"],
                "Parallel Precision": safety["Parallel Precision"],
                "Parallel Recall": safety["Parallel Recall"],
                "Parallel F1": safety["Parallel F1"],
                "Goal Closure": goal_closure,
                "Note": "automated planning-level diagnostic; not a human rating",
            }
        )
    path = output_dir / "diagnostics" / "rule_based_diagnostics.csv"
    write_csv(path, rows)
    return path


def write_completion_log(output_dir: Path, paths: dict[str, Path], diagnostics: Path) -> Path:
    log_path = output_dir / "experiment_completion_log.md"
    lines = [
        "# Experiment Completion Log",
        "",
        "Status is generated by the offline planning experiment pipeline.",
        "",
        "## Required Experiments",
        f"- COMPLETED: Controlled node/typed-relation quality -> {paths['table1']}",
        f"- COMPLETED: Dependency repair and false-parallel suppression -> {paths['table2']}",
        f"- COMPLETED: Parallel plan quality -> {paths['table3']}",
        f"- COMPLETED: Ablation study -> {paths['table4']}",
        f"- COMPLETED: Controlled JointAudit regression challenges -> {paths['table5']}",
        f"- COMPLETED: Serialization and format diagnostic -> {paths['format_diagnostic']}",
        "",
        "## Strengthening Experiments",
        f"- COMPLETED: Task complexity scaling -> {paths['table6']}",
        f"- COMPLETED: Controlled candidate-annotation perturbations -> {paths['table7']}",
        f"- COMPLETED: End-to-end case analysis -> {paths['cases']}",
        f"- COMPLETED: Failure case analysis -> {paths['failures']}",
        f"- COMPLETED: Automated planning-level diagnostics -> {diagnostics}",
        "",
        "## Important Interpretation",
        "- Estimated Makespan is a planning-layer estimate, not a physical execution measurement.",
        "- Executor labels are abstract planning resources used to express parallelism and synchronization.",
    ]
    log_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return log_path


def write_sha256_manifest(output_dir: Path) -> Path:
    path = output_dir / "analysis" / "sha256_manifest.csv"
    rows: list[dict[str, object]] = []
    for file_path in sorted(item for item in output_dir.rglob("*") if item.is_file() and item != path):
        digest = hashlib.sha256()
        with file_path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                digest.update(chunk)
        rows.append(
            {
                "relative_path": file_path.relative_to(output_dir).as_posix(),
                "size_bytes": file_path.stat().st_size,
                "sha256": digest.hexdigest(),
            }
        )
    write_csv(path, rows)
    return path


def run_extended_experiments(
    records: list[TaskRecord],
    output_dir: Path,
    method_graph: MethodGraphFn,
    methods: list[str],
    paths: dict[str, Path],
    *,
    structure_seed: int = 0,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    extended_paths = dict(paths)
    extended_paths["format_diagnostic"] = run_format_validity(records, output_dir, method_graph, methods)
    extended_paths["table5"] = run_joint_audit_challenge(
        records, output_dir, structure_seed=structure_seed
    )
    extended_paths["table6"] = run_complexity_experiment(
        output_dir, structure_seed=structure_seed
    )
    extended_paths["table7"] = run_robustness_experiment(
        records, output_dir, structure_seed=structure_seed
    )
    extended_paths["cases"] = run_case_analysis(
        records, output_dir, structure_seed=structure_seed
    )
    extended_paths["failures"] = run_failure_analysis(records, output_dir, method_graph, methods)
    diagnostics = run_rule_based_diagnostics(
        records, output_dir, structure_seed=structure_seed
    )
    extended_paths["diagnostics"] = diagnostics
    extended_paths["completion_log"] = write_completion_log(output_dir, extended_paths, diagnostics)
    extended_paths["sha256_manifest"] = write_sha256_manifest(output_dir)
    return extended_paths
