from __future__ import annotations

import json
from pathlib import Path

from .extended_experiments import run_extended_experiments
from .generation import generation_prompt_template, write_jsonl
from .metrics import dependency_safety, graph_quality, parallel_prf, plan_efficiency, state_closure_rate, summarize, write_csv
from .optimization import (
    EDGE_DROP_PROBABILITIES,
    SYNCHRONIZATION_DROP_BONUS,
    make_corrupted_graph,
    make_sequential_graph,
    optimize_graph_with_audit,
)
from .pipeline import run_verified_atg
from .planning import PlanningValidationError, plan_graph
from .schema import TaskRecord, atomic_task_graph_json_schema
from .verification import joint_graph_audit


METHODS = [
    "Text-Order Heuristic",
    "Direct Candidate Graph",
    "Schema-Constrained Candidate",
    "Sequential Planning",
    "Verified ATG (Ours)",
]

ABLATIONS = {
    "w/o State-Support Repair": {
        "use_state_dependency": False,
        "use_synchronization_repair": True,
        "use_resource_constraint": True,
        "use_critical_path": True,
        "use_executor_assignment": True,
    },
    "w/o Synchronization Repair": {
        "use_state_dependency": True,
        "use_synchronization_repair": False,
        "use_resource_constraint": True,
        "use_critical_path": True,
        "use_executor_assignment": True,
    },
    "w/o Resource-Ordering Repair": {
        "use_state_dependency": True,
        "use_synchronization_repair": True,
        "use_resource_constraint": False,
        "use_critical_path": True,
        "use_executor_assignment": True,
    },
    "w/o Order-Edge Compression": {
        "use_state_dependency": True,
        "use_synchronization_repair": True,
        "use_resource_constraint": True,
        "use_critical_path": False,
        "use_executor_assignment": True,
    },
    "w/o Executor Assignment": {
        "use_state_dependency": True,
        "use_synchronization_repair": True,
        "use_resource_constraint": True,
        "use_critical_path": True,
        "use_executor_assignment": False,
    },
    "Full Model": {
        "use_state_dependency": True,
        "use_synchronization_repair": True,
        "use_resource_constraint": True,
        "use_critical_path": True,
        "use_executor_assignment": True,
    },
}


def _candidate_seed(index: int, offset: int, structure_seed: int) -> int:
    return structure_seed * 100_000 + index + offset


def _method_graph(record: TaskRecord, method: str, index: int, structure_seed: int = 0):
    initial = set(record.initial_state.get("states", []))
    goals = set(record.goal_state.get("states", []))
    if method == "Text-Order Heuristic":
        return make_corrupted_graph(record.gold_graph, "heuristic", seed=_candidate_seed(index, 11, structure_seed))
    if method == "Direct Candidate Graph":
        return make_corrupted_graph(record.gold_graph, "llm_direct", seed=_candidate_seed(index, 23, structure_seed))
    if method == "Schema-Constrained Candidate":
        return make_corrupted_graph(record.gold_graph, "llm_schema", seed=_candidate_seed(index, 37, structure_seed))
    if method == "Sequential Planning":
        return make_sequential_graph(record.gold_graph)
    if method == "Verified ATG (Ours)":
        noisy = make_corrupted_graph(
            record.gold_graph,
            "llm_schema",
            seed=_candidate_seed(index, 37, structure_seed),
        )
        return optimize_graph_with_audit(noisy, initial_states=initial, goal_states=goals).graph
    raise ValueError(f"unknown method: {method}")


def run_experiments(
    records: list[TaskRecord],
    output_dir: Path,
    *,
    structure_seed: int = 0,
    generation_seed: int | None = None,
    duration_jitter: float | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "tasks": output_dir / "tasks.jsonl",
        "schema": output_dir / "schema" / "atomic_task_graph_schema.json",
        "prompt": output_dir / "prompts" / "atomic_graph_generation_prompt.txt",
        "configuration": output_dir / "analysis" / "experiment_configuration.json",
        "graphs": output_dir / "graphs" / "optimized_graphs.jsonl",
        "method_graphs": output_dir / "graphs" / "all_method_graphs.jsonl",
        "plans": output_dir / "plans" / "plans.jsonl",
        "table1": output_dir / "tables" / "table1_atomic_graph_quality.csv",
        "table2": output_dir / "tables" / "table2_dependency_parallel_safety.csv",
        "table3": output_dir / "tables" / "table3_plan_efficiency.csv",
        "table4": output_dir / "tables" / "table4_ablation.csv",
        "table1_detailed": output_dir / "tables" / "table1_atomic_graph_quality_detailed.csv",
        "table2_detailed": output_dir / "tables" / "table2_dependency_parallel_safety_detailed.csv",
        "table3_detailed": output_dir / "tables" / "table3_plan_efficiency_detailed.csv",
        "table4_detailed": output_dir / "tables" / "table4_ablation_detailed.csv",
    }

    write_jsonl(records, paths["tasks"])
    paths["schema"].parent.mkdir(parents=True, exist_ok=True)
    paths["schema"].write_text(json.dumps(atomic_task_graph_json_schema(), indent=2), encoding="utf-8")
    paths["prompt"].parent.mkdir(parents=True, exist_ok=True)
    paths["prompt"].write_text(generation_prompt_template() + "\n", encoding="utf-8")
    paths["configuration"].parent.mkdir(parents=True, exist_ok=True)
    paths["configuration"].write_text(
        json.dumps(
            {
                "record_count": len(records),
                "independent_reference_topologies": len({record.domain for record in records}),
                "generation_seed": generation_seed,
                "duration_jitter": duration_jitter,
                "structure_seed": structure_seed,
                "candidate_seed_formula": "structure_seed*100000 + record_index + method_offset",
                "method_seed_offsets": {
                    "Text-Order Heuristic": 11,
                    "Direct Candidate Graph": 23,
                    "Schema-Constrained Candidate": 37,
                    "Verified ATG (Ours)": 37,
                },
                "edge_drop_probabilities": EDGE_DROP_PROBABILITIES,
                "synchronization_drop_bonus": SYNCHRONIZATION_DROP_BONUS,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    graph_rows: list[dict[str, object]] = []
    safety_rows: list[dict[str, object]] = []
    plan_rows: list[dict[str, object]] = []
    graph_exports: list[dict[str, object]] = []
    all_graph_exports: list[dict[str, object]] = []
    plan_exports: list[dict[str, object]] = []

    for index, record in enumerate(records):
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        sequential_graph = make_sequential_graph(record.gold_graph)
        sequential_plan = plan_graph(sequential_graph, initial_states=initial, goal_states=goals, strict=True)
        sequential_makespan = sequential_plan.makespan
        for method in METHODS:
            optimization_audit = None
            noisy_input = None
            if method == "Verified ATG (Ours)":
                noisy = make_corrupted_graph(
                    record.gold_graph,
                    "llm_schema",
                    seed=_candidate_seed(index, 37, structure_seed),
                )
                verified = run_verified_atg(noisy, initial_states=initial, goal_states=goals)
                if not verified.accepted or verified.graph is None or verified.schedule is None:
                    raise RuntimeError(
                        f"{record.task_id}: verified pipeline rejected input: {verified.failure_reasons}"
                    )
                graph = verified.graph
                plan = verified.schedule
                optimization_audit = verified.audit
                noisy_input = noisy
            else:
                graph = _method_graph(record, method, index, structure_seed)
                plan = plan_graph(
                    graph,
                    initial_states=initial,
                    goal_states=goals,
                    strict=False,
                )
            graph_scores = graph_quality(graph, record.gold_graph)
            safety_scores = dependency_safety(graph, record.gold_graph, plan)
            graph_audit = joint_graph_audit(graph, initial, goals)
            safety_scores["Joint Accept"] = float(graph_audit.valid)
            safety_scores["State Closure Rate"] = state_closure_rate(
                graph,
                set(record.initial_state.get("states", [])),
                set(record.goal_state.get("states", [])),
            )
            plan_scores = plan_efficiency(graph, plan, sequential_makespan)

            if method != "Sequential Planning":
                graph_rows.append({"task_id": record.task_id, "Method": method, **graph_scores})
            safety_rows.append({"task_id": record.task_id, "Method": method, **safety_scores})
            plan_rows.append({"task_id": record.task_id, "Method": method, **plan_scores})
            all_graph_exports.append(
                {
                    "task_id": record.task_id,
                    "method": method,
                    "graph": graph.to_dict(),
                    "joint_audit": graph_audit.to_dict(),
                }
            )
            if method == "Verified ATG (Ours)":
                graph_exports.append(
                    {
                        "task_id": record.task_id,
                        "method": method,
                        "input_graph": noisy_input.to_dict() if noisy_input is not None else None,
                        "graph": graph.to_dict(),
                        "audit": optimization_audit.to_dict() if optimization_audit is not None else None,
                    }
                )
                plan_exports.append({"task_id": record.task_id, "method": method, "plan": plan.to_dict()})

    table1 = summarize(
        graph_rows,
        "Method",
        ["Node F1", "Edge F1", "State Acc", "Arm-Constraint Acc", "Topo Error"],
    )
    table2_base = summarize(
        safety_rows,
        "Method",
        ["Missing Dependency", "Conflict Rate", "Joint Accept", "State Closure Rate"],
    )
    table2: list[dict[str, object]] = []
    for base in table2_base:
        method = str(base["Method"])
        selected = [row for row in safety_rows if row["Method"] == method]
        predicted = sum(int(row["Predicted Parallel Pairs"]) for row in selected)
        reference = sum(int(row["Reference Parallel Pairs"]) for row in selected)
        true_positive = sum(int(row["True Parallel Pairs"]) for row in selected)
        false_positive = sum(int(row["False Parallel Pairs"]) for row in selected)
        parallel_scores = parallel_prf(true_positive, predicted, reference)
        table2.append(
            {
                "Method": method,
                "N": len(selected),
                "Missing Dependency": base["Missing Dependency"],
                "Missing Dependency Std": base["Missing Dependency Std"],
                "False Parallel": false_positive / predicted if predicted else "",
                **parallel_scores,
                "Predicted Parallel Pairs": predicted,
                "Reference Parallel Pairs": reference,
                "Conflict Rate": base["Conflict Rate"],
                "Conflict Rate Std": base["Conflict Rate Std"],
                "Joint Accept Rate": base["Joint Accept"],
                "Joint Accept Rate Std": base["Joint Accept Std"],
                "State Closure Rate": base["State Closure Rate"],
                "State Closure Rate Std": base["State Closure Rate Std"],
            }
        )
    table3 = summarize(
        plan_rows,
        "Method",
        ["Critical Path", "Waiting Time", "Executor Utilization", "Estimated Makespan", "Speedup"],
    )

    ablation_rows: list[dict[str, object]] = []
    for index, record in enumerate(records):
        initial = set(record.initial_state.get("states", []))
        goals = set(record.goal_state.get("states", []))
        sequential_makespan = plan_graph(
            make_sequential_graph(record.gold_graph),
            initial_states=initial,
            goal_states=goals,
            strict=True,
        ).makespan
        noisy = make_corrupted_graph(
            record.gold_graph,
            "llm_schema",
            seed=_candidate_seed(index, 37, structure_seed),
        )
        for setting, options in ABLATIONS.items():
            result = optimize_graph_with_audit(
                noisy,
                initial_states=initial,
                goal_states=goals,
                use_state_dependency=bool(options["use_state_dependency"]),
                use_synchronization_repair=bool(options["use_synchronization_repair"]),
                use_resource_constraint=bool(options["use_resource_constraint"]),
                use_critical_path=bool(options["use_critical_path"]),
            )
            graph = result.graph
            diagnostic_plan = plan_graph(
                graph,
                use_executor_assignment=bool(options["use_executor_assignment"]),
                initial_states=initial,
                goal_states=goals,
                strict=False,
            )
            quality = graph_quality(graph, record.gold_graph)
            safety = dependency_safety(graph, record.gold_graph, diagnostic_plan)
            efficiency = plan_efficiency(graph, diagnostic_plan, sequential_makespan)
            graph_accept = result.audit.valid
            # Acceptance is exercised through the strict scheduler. The separate
            # diagnostic plan above remains available for rejected ablations.
            accepted_plan = None
            strict_failure = ""
            try:
                accepted_plan = plan_graph(
                    graph,
                    use_executor_assignment=bool(options["use_executor_assignment"]),
                    initial_states=initial,
                    goal_states=goals,
                    strict=True,
                )
            except PlanningValidationError as exc:
                strict_failure = str(exc)
            plan_accept = graph_accept and accepted_plan is not None and accepted_plan.valid
            ablation_rows.append(
                {
                    "task_id": record.task_id,
                    "Setting": setting,
                    "Edge F1": quality["Edge F1"],
                    "Missing Dependency": safety["Missing Dependency"],
                    "False Parallel": safety["False Parallel"],
                    "Parallel F1": safety["Parallel F1"],
                    "Conflict Rate": safety["Conflict Rate"],
                    "Joint Accept": float(graph_accept),
                    "Plan Accept": float(plan_accept),
                    "Strict Schedule Failure": strict_failure,
                    "Diagnostic Speedup": efficiency["Speedup"],
                    "Accepted Speedup": (
                        sequential_makespan / accepted_plan.makespan
                        if plan_accept and accepted_plan is not None and accepted_plan.makespan
                        else None
                    ),
                    "Sync Stability": efficiency["Sync Stability"],
                }
            )

    table4 = summarize(
        ablation_rows,
        "Setting",
        [
            "Edge F1",
            "Missing Dependency",
            "False Parallel",
            "Parallel F1",
            "Conflict Rate",
            "Joint Accept",
            "Plan Accept",
            "Diagnostic Speedup",
            "Accepted Speedup",
            "Sync Stability",
        ],
    )
    for row in table4:
        setting = str(row["Setting"])
        selected = [item for item in ablation_rows if item["Setting"] == setting]
        row["Accepted N"] = sum(int(float(item["Plan Accept"])) for item in selected)
        row["Total N"] = len(selected)

    write_csv(paths["table1"], table1)
    write_csv(paths["table2"], table2)
    write_csv(paths["table3"], table3)
    write_csv(paths["table4"], table4)
    write_csv(paths["table1_detailed"], graph_rows)
    write_csv(paths["table2_detailed"], safety_rows)
    write_csv(paths["table3_detailed"], plan_rows)
    write_csv(paths["table4_detailed"], ablation_rows)

    paths["graphs"].parent.mkdir(parents=True, exist_ok=True)
    with paths["graphs"].open("w", encoding="utf-8") as handle:
        for row in graph_exports:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    paths["method_graphs"].parent.mkdir(parents=True, exist_ok=True)
    with paths["method_graphs"].open("w", encoding="utf-8") as handle:
        for row in all_graph_exports:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
    paths["plans"].parent.mkdir(parents=True, exist_ok=True)
    with paths["plans"].open("w", encoding="utf-8") as handle:
        for row in plan_exports:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")

    def seeded_method_graph(record: TaskRecord, method: str, index: int):
        return _method_graph(record, method, index, structure_seed)

    return run_extended_experiments(
        records,
        output_dir,
        seeded_method_graph,
        METHODS,
        paths,
        structure_seed=structure_seed,
    )
