from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from .schema import VALID_ARMS, VALID_EDGE_TYPES, VALID_MODES, AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode


STATE_SUPPORT_EDGE_TYPES = {"state_support"}


@dataclass(frozen=True)
class NodeStateIssue:
    node_id: str
    missing_states: tuple[str, ...] = ()
    unsupported_states: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, object]:
        return {
            "node_id": self.node_id,
            "missing_states": list(self.missing_states),
            "unsupported_states": list(self.unsupported_states),
        }


@dataclass
class CausalStateAudit:
    acyclic: bool
    initial_states: set[str]
    available_states: set[str]
    executable_nodes: list[str]
    issues: list[NodeStateIssue]
    reachable_goals: set[str]
    unreachable_goals: set[str]
    satisfied_obligations: int
    total_obligations: int
    cycle_error: str | None = None

    @property
    def closure_rate(self) -> float:
        if self.total_obligations == 0:
            return 1.0
        return self.satisfied_obligations / self.total_obligations

    @property
    def valid(self) -> bool:
        return self.acyclic and not self.issues and not self.unreachable_goals

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "acyclic": self.acyclic,
            "closure_rate": round(self.closure_rate, 6),
            "initial_states": sorted(self.initial_states),
            "available_states": sorted(self.available_states),
            "executable_nodes": list(self.executable_nodes),
            "issues": [issue.to_dict() for issue in self.issues],
            "reachable_goals": sorted(self.reachable_goals),
            "unreachable_goals": sorted(self.unreachable_goals),
            "cycle_error": self.cycle_error,
        }


@dataclass
class JointGraphAudit:
    schema_valid: bool
    closure_valid: bool
    goal_reachable: bool
    acyclic: bool
    synchronization_complete: bool
    resource_ordered: bool
    schema_issues: list[str]
    synchronization_issues: list[str]
    resource_conflicts: list[tuple[str, str, tuple[str, ...]]]
    state_audit: CausalStateAudit

    @property
    def valid(self) -> bool:
        return all(
            (
                self.schema_valid,
                self.closure_valid,
                self.goal_reachable,
                self.acyclic,
                self.synchronization_complete,
                self.resource_ordered,
            )
        )

    def failure_reasons(self) -> list[str]:
        reasons = list(self.schema_issues)
        if not self.acyclic:
            reasons.append(self.state_audit.cycle_error or "graph contains a cycle")
        for issue in self.state_audit.issues:
            reasons.append(
                f"{issue.node_id}: missing={list(issue.missing_states)}, "
                f"unsupported={list(issue.unsupported_states)}"
            )
        if self.state_audit.unreachable_goals:
            reasons.append(f"unreachable goals: {sorted(self.state_audit.unreachable_goals)}")
        reasons.extend(self.synchronization_issues)
        if self.resource_conflicts:
            reasons.append(f"unordered shared resources: {self.resource_conflicts}")
        return reasons

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "checks": {
                "schema_valid": self.schema_valid,
                "closed": self.closure_valid,
                "goal_reachable": self.goal_reachable,
                "acyclic": self.acyclic,
                "synchronization_complete": self.synchronization_complete,
                "resource_ordered": self.resource_ordered,
            },
            "schema_issues": list(self.schema_issues),
            "synchronization_issues": list(self.synchronization_issues),
            "resource_conflicts": list(self.resource_conflicts),
            "state_audit": self.state_audit.to_dict(),
            "failure_reasons": self.failure_reasons(),
        }


def infer_exogenous_states(graph: AtomicTaskGraph) -> set[str]:
    produced = {state for node in graph.nodes for state in node.post_state}
    required = {state for node in graph.nodes for state in node.pre_state}
    return required - produced


def causal_state_audit(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
) -> CausalStateAudit:
    initial = set(initial_states) if initial_states is not None else infer_exogenous_states(graph)
    goals = set(goal_states or set())
    total_obligations = sum(len(node.pre_state) for node in graph.nodes) + len(goals)

    try:
        order = graph.topological_order()
    except ValueError as exc:
        issues = [
            NodeStateIssue(node_id=node.id, missing_states=tuple(sorted(set(node.pre_state))))
            for node in graph.nodes
        ]
        return CausalStateAudit(
            acyclic=False,
            initial_states=initial,
            available_states=set(initial),
            executable_nodes=[],
            issues=issues,
            reachable_goals=goals & initial,
            unreachable_goals=goals - initial,
            satisfied_obligations=len(goals & initial),
            total_obligations=total_obligations,
            cycle_error=str(exc),
        )

    incoming = graph.predecessors()
    node_map = graph.node_map
    available = set(initial)
    executable: list[str] = []
    executed = set()
    issues: list[NodeStateIssue] = []
    satisfied = 0

    for node_id in order:
        node = node_map[node_id]
        missing: set[str] = set()
        unsupported: set[str] = set()
        for state in node.pre_state:
            if state not in available:
                missing.add(state)
                continue
            if state in initial:
                satisfied += 1
                continue
            support_exists = any(
                edge.type in STATE_SUPPORT_EDGE_TYPES
                and edge.source in executed
                and edge.state == state
                and state in node_map[edge.source].post_state
                for edge in incoming.get(node_id, [])
                if edge.source in node_map
            )
            if support_exists:
                satisfied += 1
            else:
                unsupported.add(state)
        if missing or unsupported:
            issues.append(
                NodeStateIssue(
                    node_id=node_id,
                    missing_states=tuple(sorted(missing)),
                    unsupported_states=tuple(sorted(unsupported)),
                )
            )
            continue
        executable.append(node_id)
        executed.add(node_id)
        available.update(node.post_state)

    reachable_goals = goals & available
    unreachable_goals = goals - available
    satisfied += len(reachable_goals)
    return CausalStateAudit(
        acyclic=True,
        initial_states=initial,
        available_states=available,
        executable_nodes=executable,
        issues=issues,
        reachable_goals=reachable_goals,
        unreachable_goals=unreachable_goals,
        satisfied_obligations=satisfied,
        total_obligations=total_obligations,
    )


def resource_conflict_pairs(graph: AtomicTaskGraph) -> list[tuple[str, str, tuple[str, ...]]]:
    node_map = graph.node_map
    conflicts: list[tuple[str, str, tuple[str, ...]]] = []
    for left, right in graph.incomparable_pairs():
        shared = tuple(sorted(set(node_map[left].resource) & set(node_map[right].resource)))
        if shared:
            conflicts.append((left, right, shared))
    return conflicts


def graph_schema_issues(
    graph: AtomicTaskGraph,
    *,
    check_relationships: bool = True,
    resource_universe: set[str] | None = None,
) -> list[str]:
    issues: list[str] = []
    # Dataclass annotations do not validate values at runtime. Check the original
    # attributes before hashing, graph traversal, or to_dict can normalize them.
    if not isinstance(graph, AtomicTaskGraph):
        return ["graph must be an AtomicTaskGraph"]
    if not isinstance(graph.nodes, list) or not isinstance(graph.edges, list):
        return ["nodes and edges must be lists"]
    for index, node in enumerate(graph.nodes):
        prefix = f"node[{index}]"
        if not isinstance(node, AtomicTaskNode):
            issues.append(f"{prefix}: expected AtomicTaskNode")
            continue
        for name in ("id", "action", "object_name", "mode", "workspace"):
            if not isinstance(getattr(node, name), str):
                issues.append(f"{prefix}: {name} must be a string")
        for name in ("pre_state", "post_state", "resource", "candidate_arm"):
            values = getattr(node, name)
            if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
                issues.append(f"{prefix}: {name} must be a list of strings")
        if isinstance(node.duration, bool) or not isinstance(node.duration, (int, float)):
            issues.append(f"{prefix}: duration must be a number, not a boolean or numeric string")
        if node.target is not None and not isinstance(node.target, str):
            issues.append(f"{prefix}: target must be a string when provided")
        if not isinstance(node.metadata, dict):
            issues.append(f"{prefix}: metadata must be a dictionary")
    for index, edge in enumerate(graph.edges):
        prefix = f"edge[{index}]"
        if not isinstance(edge, AtomicTaskEdge):
            issues.append(f"{prefix}: expected AtomicTaskEdge")
            continue
        for name in ("source", "target", "type", "reason"):
            if not isinstance(getattr(edge, name), str):
                issues.append(f"{prefix}: {name} must be a string")
        for name in ("state", "resource"):
            value = getattr(edge, name)
            if value is not None and not isinstance(value, str):
                issues.append(f"{prefix}: {name} must be a string when provided")
    # Reject labels that do not belong to the declared relation type at input.
    # This applies before repair and also to dataclass callers.
    for edge in graph.edges:
        if not isinstance(edge, AtomicTaskEdge):
            continue
        if edge.type == "order" and (edge.state is not None or edge.resource is not None):
            issues.append(f"{edge.source}->{edge.target}: order edge cannot carry state/resource labels")
        if edge.type in ("state_support", "synchronization") and edge.resource is not None:
            issues.append(f"{edge.source}->{edge.target}: state/sync edge cannot carry resource labels")
        if edge.type == "resource_mutex" and edge.state is not None:
            issues.append(f"{edge.source}->{edge.target}: resource edge cannot carry a state label")
    if issues:
        return issues
    node_ids = [node.id for node in graph.nodes]
    if not node_ids:
        issues.append("graph has no nodes")
    if len(node_ids) != len(set(node_ids)):
        issues.append("graph contains duplicate node ids")
    known_ids = set(node_ids)
    for node in graph.nodes:
        if not node.id or not node.action or not node.object_name:
            issues.append(f"{node.id or '<missing-id>'}: required text field is empty")
        if not node.pre_state or not node.post_state:
            issues.append(f"{node.id}: pre_state and post_state must be non-empty")
        if not isfinite(node.duration) or node.duration <= 0:
            issues.append(f"{node.id}: duration must be finite and positive")
        for field_name, values in (
            ("pre_state", node.pre_state),
            ("post_state", node.post_state),
            ("resource", node.resource),
            ("candidate_arm", node.candidate_arm),
        ):
            if len(values) != len(set(values)):
                issues.append(f"{node.id}: {field_name} contains duplicate values")
            if any(not isinstance(value, str) or not value for value in values):
                issues.append(f"{node.id}: {field_name} contains an empty or non-string value")
        if not node.candidate_arm:
            issues.append(f"{node.id}: candidate_arm must be non-empty")
        invalid_arms = sorted(set(node.candidate_arm) - VALID_ARMS)
        if invalid_arms:
            issues.append(f"{node.id}: invalid candidate executors {invalid_arms}")
        if node.mode not in VALID_MODES:
            issues.append(f"{node.id}: invalid mode {node.mode}")
        if node.mode == "cooperative" and node.candidate_arm != ["both"]:
            issues.append(f"{node.id}: cooperative mode requires candidate_arm=['both']")
        if node.mode == "single" and "both" in node.candidate_arm:
            issues.append(f"{node.id}: single mode cannot use the both occupancy label")
        if resource_universe is not None:
            unknown_resources = sorted(set(node.resource) - resource_universe)
            if unknown_resources:
                issues.append(f"{node.id}: resources outside the declared universe {unknown_resources}")
    edge_keys = [edge.key() for edge in graph.edges]
    if len(edge_keys) != len(set(edge_keys)):
        issues.append("graph contains duplicate typed edges")
    node_map = graph.node_map
    for edge in graph.edges:
        if edge.type not in VALID_EDGE_TYPES:
            issues.append(f"{edge.source}->{edge.target}: invalid edge type {edge.type}")
        if edge.source not in known_ids or edge.target not in known_ids:
            issues.append(f"{edge.source}->{edge.target}: dangling edge")
            continue
        if edge.source == edge.target:
            issues.append(f"{edge.source}->{edge.target}: self-loop edge")
        if edge.type in {"state_support", "synchronization"} and not edge.state:
            issues.append(f"{edge.source}->{edge.target}: {edge.type} edge has no state label")
        if edge.type == "resource_mutex" and not edge.resource:
            issues.append(f"{edge.source}->{edge.target}: resource edge has no resource label")
        if not check_relationships:
            continue
        source = node_map[edge.source]
        target = node_map[edge.target]
        if edge.type == "state_support" and edge.state not in (
            set(source.post_state) & set(target.pre_state)
        ):
            issues.append(
                f"{edge.source}->{edge.target}: state_support label {edge.state!r} "
                "is not produced by the source and required by the target"
            )
        if edge.type == "resource_mutex" and edge.resource not in (
            set(source.resource) & set(target.resource)
        ):
            issues.append(
                f"{edge.source}->{edge.target}: resource label {edge.resource!r} "
                "is not shared by both endpoints"
            )
    return issues


def synchronization_issues(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
) -> list[str]:
    issues: list[str] = []
    node_map = graph.node_map
    required = {
        (edge.source, edge.target, edge.state)
        for edge in graph.edges
        if edge.type == "state_support"
        and edge.source in node_map
        and edge.target in node_map
        and node_map[edge.target].mode == "cooperative"
        and edge.state is not None
    }
    actual = {
        (edge.source, edge.target, edge.state)
        for edge in graph.edges
        if edge.type == "synchronization"
    }
    sync_key = lambda item: (item[0], item[1], item[2] or "")
    for source, target, state in sorted(required - actual, key=sync_key):
        issues.append(f"{target}: missing synchronization for {state} from {source}")
    for source, target, state in sorted(actual - required, key=sync_key):
        issues.append(
            f"{source}->{target}: orphan or non-cooperative synchronization for {state}"
        )
    return issues


def joint_graph_audit(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
) -> JointGraphAudit:
    initial = set(initial_states) if initial_states is not None else infer_exogenous_states(graph)
    goals = set(goal_states or set())
    state_audit = causal_state_audit(graph, initial, goals)
    schema = graph_schema_issues(graph)
    sync = synchronization_issues(graph, initial)
    conflicts = resource_conflict_pairs(graph)
    closure_valid = state_audit.acyclic and not state_audit.issues
    return JointGraphAudit(
        schema_valid=not schema,
        closure_valid=closure_valid,
        goal_reachable=not state_audit.unreachable_goals,
        acyclic=state_audit.acyclic,
        synchronization_complete=not sync,
        resource_ordered=not conflicts,
        schema_issues=schema,
        synchronization_issues=sync,
        resource_conflicts=conflicts,
        state_audit=state_audit,
    )
