from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite

from .schema import AtomicTaskGraph
from .verification import causal_state_audit, joint_graph_audit


class PlanningValidationError(ValueError):
    pass


@dataclass
class PlannedStep:
    node_id: str
    action: str
    object_name: str
    start: float
    finish: float
    executors: list[str]
    resources: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "action": self.action,
            "object": self.object_name,
            "start": self.start,
            "finish": self.finish,
            "executors": list(self.executors),
            "resources": list(self.resources),
        }


@dataclass
class PlanTimeline:
    items: list[PlannedStep]
    makespan: float
    waiting_time: float
    executor_utilization: float
    sync_stability: float
    valid: bool = True
    violations: list[str] | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "estimated_makespan": self.makespan,
            "waiting_time": round(self.waiting_time, 3),
            "executor_utilization": round(self.executor_utilization, 4),
            "sync_stability": round(self.sync_stability, 4),
            "verification": {
                "valid": self.valid,
                "violations": list(self.violations or []),
            },
            "items": [item.to_dict() for item in self.items],
        }


def critical_path_length(graph: AtomicTaskGraph) -> float:
    node_map = graph.node_map
    pred = graph.predecessors()
    longest: dict[str, float] = {}
    for node_id in graph.topological_order():
        base = max((longest[edge.source] for edge in pred.get(node_id, [])), default=0.0)
        longest[node_id] = base + node_map[node_id].duration
    return max(longest.values(), default=0.0)


def _choose_executor(candidate_arm: list[str], executor_available: dict[str, float], earliest: float) -> list[str]:
    executor_key = {"left": 0, "right": 1}
    candidates = sorted(
        {executor for executor in candidate_arm if executor in executor_key},
        key=executor_key.get,
    )
    if not candidates:
        candidates = ["left", "right"]
    return [
        min(
            candidates,
            key=lambda executor: (
                max(earliest, executor_available[executor]),
                executor_key[executor],
            ),
        )
    ]


def schedule_issues(graph: AtomicTaskGraph, items: list[PlannedStep]) -> list[str]:
    """Check the produced schedule against represented discrete constraints."""
    issues: list[str] = []
    node_map = graph.node_map
    item_map = {item.node_id: item for item in items}
    if len(item_map) != len(items) or set(item_map) != set(node_map):
        issues.append("schedule must contain every graph node exactly once")
    for item in items:
        node = node_map.get(item.node_id)
        if node is None:
            continue
        if (
            not isfinite(item.start)
            or not isfinite(item.finish)
            or item.start < 0
            or not isclose(item.finish - item.start, node.duration, rel_tol=1e-9, abs_tol=1e-9)
        ):
            issues.append(f"{node.id}: invalid schedule interval or duration")
        if node.mode == "cooperative":
            allowed = len(item.executors) == 2 and set(item.executors) == {"left", "right"}
        else:
            allowed = (
                len(item.executors) == 1
                and item.executors[0] in {"left", "right"}
                and item.executors[0] in node.candidate_arm
            )
        if not allowed:
            issues.append(f"{node.id}: executor occupancy violates mode or candidate_arm")
        if set(item.resources) != set(node.resource):
            issues.append(f"{node.id}: schedule resources differ from declared resources")
    for edge in graph.edges:
        source, target = item_map.get(edge.source), item_map.get(edge.target)
        if source is not None and target is not None and source.finish > target.start + 1e-9:
            issues.append(f"{edge.source}->{edge.target}: schedule violates precedence")
    for index, left in enumerate(items):
        for right in items[index + 1 :]:
            if left.start < right.finish and right.start < left.finish:
                if set(left.executors) & set(right.executors):
                    issues.append(f"{left.node_id}/{right.node_id}: overlapping base-executor occupancy")
                if set(left.resources) & set(right.resources):
                    issues.append(f"{left.node_id}/{right.node_id}: overlapping capacity-1 resource")
    return issues


def plan_graph(
    graph: AtomicTaskGraph,
    use_executor_assignment: bool = True,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
    strict: bool = False,
) -> PlanTimeline:
    state_audit = causal_state_audit(graph, initial_states, goal_states)
    violations: list[str] = []
    if not state_audit.acyclic:
        violations.append(state_audit.cycle_error or "graph contains a cycle")
    for issue in state_audit.issues:
        if issue.missing_states:
            violations.append(f"{issue.node_id}: missing states {', '.join(issue.missing_states)}")
        if issue.unsupported_states:
            violations.append(f"{issue.node_id}: unsupported states {', '.join(issue.unsupported_states)}")
    if state_audit.unreachable_goals:
        violations.append(f"unreachable goals: {', '.join(sorted(state_audit.unreachable_goals))}")
    if strict:
        joint_audit = joint_graph_audit(graph, initial_states, goal_states)
        if not joint_audit.valid:
            raise PlanningValidationError("; ".join(joint_audit.failure_reasons()))

    node_map = graph.node_map
    pred = graph.predecessors()
    finish: dict[str, float] = {}
    executor_available = {"left": 0.0, "right": 0.0}
    intervals = {"left": [], "right": []}
    items: list[PlannedStep] = []

    for node_id in graph.topological_order():
        node = node_map[node_id]
        dep_ready = max((finish[edge.source] for edge in pred.get(node_id, [])), default=0.0)
        if not use_executor_assignment:
            executors = ["left"]
        elif node.mode == "cooperative":
            executors = ["left", "right"]
        else:
            executors = _choose_executor(node.candidate_arm, executor_available, dep_ready)
        start = max([dep_ready] + [executor_available[executor] for executor in executors])
        end = start + node.duration
        for executor in executors:
            intervals[executor].append((start, end))
            executor_available[executor] = end
        finish[node_id] = end
        items.append(
            PlannedStep(
                node_id=node.id,
                action=node.action,
                object_name=node.object_name,
                start=start,
                finish=end,
                executors=executors,
                resources=list(node.resource),
            )
        )

    makespan = max(finish.values(), default=0.0)
    waiting_time = 0.0
    for executor_intervals in intervals.values():
        executor_intervals = sorted(executor_intervals)
        previous = 0.0
        for start, end in executor_intervals:
            if start > previous:
                waiting_time += start - previous
            previous = end
    busy = sum(end - start for executor_intervals in intervals.values() for start, end in executor_intervals)
    utilization = busy / (2.0 * makespan) if makespan > 0 else 0.0

    coop_total = 0
    coop_ok = 0
    item_map = {item.node_id: item for item in items}
    for node in graph.nodes:
        if node.mode == "cooperative" or "both" in node.candidate_arm:
            coop_total += 1
            item = item_map.get(node.id)
            if item is not None and set(item.executors) == {"left", "right"}:
                coop_ok += 1
    sync_stability = coop_ok / coop_total if coop_total else 1.0
    violations.extend(schedule_issues(graph, items))
    if strict and violations:
        raise PlanningValidationError("; ".join(violations))
    return PlanTimeline(
        items=items,
        makespan=makespan,
        waiting_time=waiting_time,
        executor_utilization=utilization,
        sync_stability=sync_stability,
        valid=not violations,
        violations=violations,
    )


def plan_conflict_rate(plan: PlanTimeline) -> float:
    conflicts = 0
    comparisons = 0
    items = plan.items
    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            overlap = left.start < right.finish and right.start < left.finish
            if not overlap:
                continue
            comparisons += 1
            if set(left.resources) & set(right.resources):
                conflicts += 1
    return conflicts / comparisons if comparisons else 0.0
