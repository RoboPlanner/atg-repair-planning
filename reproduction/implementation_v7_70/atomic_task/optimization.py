from __future__ import annotations

import random
from dataclasses import dataclass, field

from .planning import critical_path_length
from .schema import AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode, node_sort_key
from .verification import (
    causal_state_audit,
    graph_schema_issues,
    infer_exogenous_states,
    joint_graph_audit,
    resource_conflict_pairs,
)


EDGE_DROP_PROBABILITIES = {
    "heuristic": 0.35,
    "llm_direct": 0.28,
    "llm_schema": 0.14,
    "default": 0.18,
}
SYNCHRONIZATION_DROP_BONUS = 0.15


@dataclass
class AuditEvent:
    stage: str
    action: str
    accepted: bool
    source: str | None = None
    target: str | None = None
    edge_type: str | None = None
    state: str | None = None
    resource: str | None = None
    reason: str = ""
    before_critical_path: float | None = None
    after_critical_path: float | None = None

    def to_dict(self) -> dict[str, object]:
        return {
            "stage": self.stage,
            "action": self.action,
            "accepted": self.accepted,
            "source": self.source,
            "target": self.target,
            "edge_type": self.edge_type,
            "state": self.state,
            "resource": self.resource,
            "reason": self.reason,
            "before_critical_path": self.before_critical_path,
            "after_critical_path": self.after_critical_path,
        }


@dataclass
class OptimizationAudit:
    before: dict[str, object]
    after: dict[str, object]
    resource_conflicts_before: list[tuple[str, str, tuple[str, ...]]]
    resource_conflicts_after: list[tuple[str, str, tuple[str, ...]]]
    joint_before: dict[str, object] = field(default_factory=dict)
    joint_after: dict[str, object] = field(default_factory=dict)
    events: list[AuditEvent] = field(default_factory=list)
    failure_reasons: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return bool(self.joint_after.get("valid"))

    def to_dict(self) -> dict[str, object]:
        return {
            "valid": self.valid,
            "before": self.before,
            "after": self.after,
            "resource_conflicts_before": self.resource_conflicts_before,
            "resource_conflicts_after": self.resource_conflicts_after,
            "joint_before": self.joint_before,
            "joint_after": self.joint_after,
            "events": [event.to_dict() for event in self.events],
            "failure_reasons": list(self.failure_reasons),
        }


@dataclass
class OptimizationResult:
    graph: AtomicTaskGraph
    audit: OptimizationAudit


def replay_accepted_events(
    graph: AtomicTaskGraph,
    events: list[AuditEvent],
) -> AtomicTaskGraph:
    """Replay accepted edge mutations from the original candidate graph."""
    output = graph.copy()
    add_actions = {
        "add_state_support",
        "add_resource_mutex",
        "add_synchronization",
    }
    remove_actions = {
        "remove_invalid_state_support",
        "remove_invalid_resource_mutex",
        "remove_synchronization",
        "remove_order_edge",
    }
    for event in events:
        if not event.accepted or event.source is None or event.target is None or event.edge_type is None:
            continue
        edge = AtomicTaskEdge(
            source=event.source,
            target=event.target,
            type=event.edge_type,
            state=event.state,
            resource=event.resource,
        )
        if event.action in add_actions:
            output.add_edge(edge)
        elif event.action in remove_actions:
            output.remove_edge(edge)
    return output


def repair_state_dependencies(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    events: list[AuditEvent] | None = None,
) -> AtomicTaskGraph:
    graph = graph.copy()
    initial = set(initial_states) if initial_states is not None else infer_exogenous_states(graph)
    node_map = graph.node_map
    retained_edges: list[AtomicTaskEdge] = []
    for edge in graph.edges:
        valid = (
            edge.type != "state_support"
            or (
                edge.source in node_map
                and edge.target in node_map
                and edge.state is not None
                and edge.state in node_map[edge.source].post_state
                and edge.state in node_map[edge.target].pre_state
            )
        )
        if valid:
            retained_edges.append(edge)
        elif events is not None:
            events.append(
                AuditEvent(
                    stage="state_closure",
                    action="remove_invalid_state_support",
                    accepted=True,
                    source=edge.source,
                    target=edge.target,
                    edge_type="state_support",
                    state=edge.state,
                    reason=f"removed invalid state label {edge.state!r}",
                )
            )
    graph.edges = retained_edges
    producers: dict[str, list[str]] = {}
    for node in sorted(graph.nodes, key=lambda item: node_sort_key(item.id)):
        for state in sorted(set(node.post_state)):
            producers.setdefault(state, []).append(node.id)
    for node in sorted(graph.nodes, key=lambda item: node_sort_key(item.id)):
        for state in sorted(set(node.pre_state)):
            if state in initial:
                continue
            explicit = any(
                edge.target == node.id
                and edge.type == "state_support"
                and edge.source in graph.node_map
                and edge.state == state
                and state in graph.node_map[edge.source].post_state
                for edge in graph.edges
            )
            if explicit:
                continue
            candidates: list[tuple[float, tuple[int, int, str], str]] = []
            for source in sorted(producers.get(state, []), key=node_sort_key):
                if source == node.id or graph.has_path(node.id, source):
                    continue
                candidate = graph.copy()
                candidate.add_edge(
                    AtomicTaskEdge(
                        source=source,
                        target=node.id,
                        type="state_support",
                        state=state,
                        reason=f"repaired explicit support for {state}",
                    )
                )
                try:
                    score = critical_path_length(candidate)
                except ValueError:
                    continue
                candidates.append((score, node_sort_key(source), source))
            if not candidates:
                if events is not None:
                    events.append(
                        AuditEvent(
                            stage="state_closure",
                            action="add_state_support",
                            accepted=False,
                            target=node.id,
                            edge_type="state_support",
                            state=state,
                            reason=f"no acyclic producer is available for {state}",
                        )
                    )
                continue
            _, _, source = min(candidates)
            edge = AtomicTaskEdge(
                source=source,
                target=node.id,
                type="state_support",
                state=state,
                reason=f"repaired explicit support for {state}",
            )
            graph.add_edge(edge)
            if events is not None:
                events.append(
                    AuditEvent(
                        stage="state_closure",
                        action="add_state_support",
                        accepted=True,
                        source=source,
                        target=node.id,
                        edge_type="state_support",
                        state=state,
                        reason=f"selected an acyclic producer for {state}",
                    )
                )
    return graph


def add_resource_mutex_edges(
    graph: AtomicTaskGraph,
    events: list[AuditEvent] | None = None,
) -> AtomicTaskGraph:
    graph = graph.copy()
    node_map = graph.node_map
    retained_edges: list[AtomicTaskEdge] = []
    for edge in graph.edges:
        valid = (
            edge.type != "resource_mutex"
            or (
                edge.source in node_map
                and edge.target in node_map
                and edge.resource is not None
                and edge.resource in node_map[edge.source].resource
                and edge.resource in node_map[edge.target].resource
            )
        )
        if valid:
            retained_edges.append(edge)
        elif events is not None:
            events.append(
                AuditEvent(
                    stage="resource_mutex",
                    action="remove_invalid_resource_mutex",
                    accepted=True,
                    source=edge.source,
                    target=edge.target,
                    edge_type="resource_mutex",
                    resource=edge.resource,
                    reason=f"removed invalid resource label {edge.resource!r}",
                )
            )
    graph.edges = retained_edges
    nodes = sorted(graph.nodes, key=lambda item: node_sort_key(item.id))
    for i, left in enumerate(nodes):
        for right in nodes[i + 1 :]:
            if graph.has_path(left.id, right.id) or graph.has_path(right.id, left.id):
                continue
            shared = sorted(set(left.resource) & set(right.resource))
            if not shared:
                continue
            candidates: list[tuple[float, tuple[int, int, str], str, str]] = []
            for source, target in ((left.id, right.id), (right.id, left.id)):
                candidate = graph.copy()
                candidate.add_edge(
                    AtomicTaskEdge(
                        source=source,
                        target=target,
                        type="resource_mutex",
                        resource=shared[0],
                        reason=f"serialize shared resource {shared[0]}",
                    )
                )
                try:
                    score = critical_path_length(candidate)
                except ValueError:
                    continue
                candidates.append((score, node_sort_key(source), source, target))
            if not candidates:
                if events is not None:
                    events.append(
                        AuditEvent(
                            stage="resource_mutex",
                            action="add_resource_mutex",
                            accepted=False,
                            source=left.id,
                            target=right.id,
                            edge_type="resource_mutex",
                            resource=shared[0],
                            reason=f"both directions would create a cycle for {shared[0]}",
                        )
                    )
                continue
            score, _, source, target = min(candidates)
            for resource in shared:
                graph.add_edge(
                    AtomicTaskEdge(
                        source=source,
                        target=target,
                        type="resource_mutex",
                        resource=resource,
                        reason=f"minimum-critical-path orientation for shared resource {resource}",
                    )
                )
            if events is not None:
                for resource in shared:
                    events.append(
                        AuditEvent(
                            stage="resource_mutex",
                            action="add_resource_mutex",
                            accepted=True,
                            source=source,
                            target=target,
                            edge_type="resource_mutex",
                            resource=resource,
                            reason=f"selected lower critical-path orientation for {resource}",
                            after_critical_path=score,
                        )
                    )
    return graph


def add_cooperative_sync_edges(
    graph: AtomicTaskGraph,
    events: list[AuditEvent] | None = None,
) -> AtomicTaskGraph:
    graph = graph.copy()
    old_sync = [edge for edge in graph.edges if edge.type == "synchronization"]
    graph.edges = [edge for edge in graph.edges if edge.type != "synchronization"]
    if events is not None:
        for edge in old_sync:
            events.append(
                AuditEvent(
                    stage="synchronization",
                    action="remove_synchronization",
                    accepted=True,
                    source=edge.source,
                    target=edge.target,
                    edge_type="synchronization",
                    state=edge.state,
                    reason=f"rebuild exact synchronization set for {edge.state}",
                )
            )
    for node in sorted(graph.nodes, key=lambda item: node_sort_key(item.id)):
        if node.mode != "cooperative":
            continue
        for state in sorted(set(node.pre_state)):
            sources = [
                edge.source
                for edge in graph.edges
                if edge.target == node.id
                and edge.type == "state_support"
                and edge.source in graph.node_map
                and edge.state == state
                and state in graph.node_map[edge.source].post_state
            ]
            for source in sorted(set(sources), key=node_sort_key):
                graph.add_edge(
                    AtomicTaskEdge(
                        source=source,
                        target=node.id,
                        type="synchronization",
                        state=state,
                        reason="cooperative action requires synchronized input states",
                    )
                )
                if events is not None:
                    events.append(
                        AuditEvent(
                            stage="synchronization",
                            action="add_synchronization",
                            accepted=True,
                            source=source,
                            target=node.id,
                            edge_type="synchronization",
                            state=state,
                            reason=f"cooperative input state {state}",
                        )
                    )
    return graph


def compress_redundant_order_edges(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
    events: list[AuditEvent] | None = None,
) -> AtomicTaskGraph:
    graph = graph.copy()
    for edge in sorted(
        (item for item in graph.edges if item.type == "order"),
        key=lambda item: (
            node_sort_key(item.source),
            node_sort_key(item.target),
            item.type,
            item.state or "",
            item.resource or "",
        ),
    ):
        before_cp = critical_path_length(graph)
        candidate = graph.copy()
        candidate.remove_edge(edge)
        state_audit = causal_state_audit(candidate, initial_states, goal_states)
        conflicts = resource_conflict_pairs(candidate)
        accepted = state_audit.valid and not conflicts
        after_cp: float | None = None
        if accepted:
            after_cp = critical_path_length(candidate)
            graph = candidate
        if events is not None:
            reasons: list[str] = []
            if not state_audit.valid:
                reasons.append("state/goal closure would be violated")
            if conflicts:
                reasons.append("a shared resource would become unordered")
            if accepted:
                reasons.append("closure and resource ordering remain valid")
            events.append(
                AuditEvent(
                    stage="compression",
                    action="remove_order_edge",
                    accepted=accepted,
                    source=edge.source,
                    target=edge.target,
                    edge_type="order",
                    reason="; ".join(reasons),
                    before_critical_path=before_cp,
                    after_critical_path=after_cp,
                )
            )
    return graph


def optimize_graph_with_audit(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
    use_state_dependency: bool = True,
    use_synchronization_repair: bool = True,
    use_resource_constraint: bool = True,
    use_critical_path: bool = True,
) -> OptimizationResult:
    initial = set(initial_states) if initial_states is not None else infer_exogenous_states(graph)
    goals = set(goal_states or set())
    structure_issues = graph_schema_issues(graph, check_relationships=False)
    before_state = causal_state_audit(graph, initial, goals)
    before_joint = joint_graph_audit(graph, initial, goals)
    conflicts_before = resource_conflict_pairs(graph)
    events: list[AuditEvent] = []
    optimized = graph.copy()

    if structure_issues or not before_state.acyclic:
        failures = list(structure_issues)
        if not before_state.acyclic:
            failures.append(before_state.cycle_error or "graph contains a cycle")
        audit = OptimizationAudit(
            before=before_state.to_dict(),
            after=before_state.to_dict(),
            resource_conflicts_before=conflicts_before,
            resource_conflicts_after=conflicts_before,
            joint_before=before_joint.to_dict(),
            joint_after=before_joint.to_dict(),
            events=events,
            failure_reasons=list(dict.fromkeys(failures + before_joint.failure_reasons())),
        )
        return OptimizationResult(graph=optimized, audit=audit)

    if use_state_dependency:
        optimized = repair_state_dependencies(optimized, initial, events)
    if use_synchronization_repair:
        optimized = add_cooperative_sync_edges(optimized, events)
    if use_resource_constraint:
        optimized = add_resource_mutex_edges(optimized, events)
    if use_critical_path:
        optimized = compress_redundant_order_edges(optimized, initial, goals, events)

    after_state = causal_state_audit(optimized, initial, goals)
    after_joint = joint_graph_audit(optimized, initial, goals)
    conflicts_after = resource_conflict_pairs(optimized)
    failures = after_joint.failure_reasons()
    audit = OptimizationAudit(
        before=before_state.to_dict(),
        after=after_state.to_dict(),
        resource_conflicts_before=conflicts_before,
        resource_conflicts_after=conflicts_after,
        joint_before=before_joint.to_dict(),
        joint_after=after_joint.to_dict(),
        events=events,
        failure_reasons=failures,
    )
    return OptimizationResult(graph=optimized, audit=audit)


def optimize_graph(
    graph: AtomicTaskGraph,
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
    use_state_dependency: bool = True,
    use_synchronization_repair: bool = True,
    use_resource_constraint: bool = True,
    use_critical_path: bool = True,
) -> AtomicTaskGraph:
    return optimize_graph_with_audit(
        graph,
        initial_states=initial_states,
        goal_states=goal_states,
        use_state_dependency=use_state_dependency,
        use_synchronization_repair=use_synchronization_repair,
        use_resource_constraint=use_resource_constraint,
        use_critical_path=use_critical_path,
    ).graph


def make_sequential_graph(graph: AtomicTaskGraph) -> AtomicTaskGraph:
    output = graph.copy()
    output.edges = [
        edge
        for edge in output.edges
        if edge.type in {"state_support", "resource_mutex", "synchronization"}
    ]
    ordered = sorted([node.id for node in output.nodes], key=node_sort_key)
    for source, target in zip(ordered, ordered[1:]):
        output.add_edge(AtomicTaskEdge(source=source, target=target, type="order", reason="sequential baseline"))
    return output


def make_corrupted_graph(graph: AtomicTaskGraph, profile: str, seed: int) -> AtomicTaskGraph:
    rng = random.Random(seed)
    output = graph.copy()
    nodes: list[AtomicTaskNode] = []
    for index, node in enumerate(output.nodes):
        item = AtomicTaskNode.from_dict(node.to_dict())
        if profile == "heuristic":
            if index % 3 == 1 and item.pre_state:
                item.pre_state = item.pre_state[:-1]
            if index % 4 == 2:
                item.candidate_arm = ["left"]
        elif profile in {"llm", "llm_direct", "llm_schema"}:
            if profile == "llm_direct" and index % 4 == 0:
                item.resource = []
            elif index % 4 == 0 and len(item.resource) > 1:
                item.resource = item.resource[:1]
            if profile == "llm_direct" and index % 3 == 0 and item.pre_state:
                item.pre_state = item.pre_state[:-1]
            if index % 5 == 2:
                item.candidate_arm = ["left", "right"]
            if profile == "llm_schema" and index % 5 == 2 and "both" in node.candidate_arm:
                item.candidate_arm = ["both"]
        nodes.append(item)
    output.nodes = nodes

    kept_edges: list[AtomicTaskEdge] = []
    for edge in output.edges:
        drop_prob = EDGE_DROP_PROBABILITIES.get(profile, EDGE_DROP_PROBABILITIES["default"])
        if edge.type == "synchronization":
            drop_prob += SYNCHRONIZATION_DROP_BONUS
        if rng.random() > drop_prob:
            kept_edges.append(edge)
    output.edges = kept_edges

    ordered = sorted([node.id for node in output.nodes], key=node_sort_key)
    if profile == "heuristic":
        for source, target in zip(ordered, ordered[1:]):
            output.add_edge(AtomicTaskEdge(source, target, "order", reason="text-order heuristic"))
    elif profile == "llm_schema" and len(ordered) >= 4:
        for pair_index, (source, target) in enumerate(zip(ordered, ordered[1:])):
            if pair_index % 2 == 0:
                output.add_edge(AtomicTaskEdge(source, target, "order", reason="controlled conservative ordering"))
    return output
