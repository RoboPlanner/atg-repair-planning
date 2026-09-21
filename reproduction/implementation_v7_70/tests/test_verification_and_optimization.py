from __future__ import annotations

import unittest

from atomic_task.extended_experiments import (
    _apply_annotation_perturbation,
    _complexity_record,
    _joint_audit_challenge_graph,
)
from atomic_task.generation import generate_dataset
from atomic_task.metrics import dependency_safety, state_closure_rate, unreachable_goal_rate
from atomic_task.optimization import (
    add_resource_mutex_edges,
    compress_redundant_order_edges,
    make_sequential_graph,
    optimize_graph_with_audit,
    replay_accepted_events,
    repair_state_dependencies,
)
from atomic_task.planning import PlanningValidationError, plan_graph
from atomic_task.pipeline import run_verified_atg
from atomic_task.schema import AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode
from atomic_task.schema import atomic_task_graph_json_schema
from atomic_task.verification import (
    causal_state_audit,
    graph_schema_issues,
    joint_graph_audit,
    resource_conflict_pairs,
)


def node(
    node_id: str,
    pre: list[str],
    post: list[str],
    duration: float = 1.0,
    resources: list[str] | None = None,
) -> AtomicTaskNode:
    return AtomicTaskNode(
        id=node_id,
        action="act",
        object_name=node_id,
        pre_state=pre,
        post_state=post,
        duration=duration,
        resource=list(resources or [node_id]),
        candidate_arm=["left", "right"],
    )


class CausalStateAuditTests(unittest.TestCase):
    def test_mutually_circular_state_claim_is_not_closed(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["s2"], ["s1"]), node("b", ["s1"], ["s2"])],
            edges=[],
        )
        audit = causal_state_audit(graph, set(), {"s1"})
        self.assertFalse(audit.valid)
        self.assertEqual(audit.executable_nodes, [])
        self.assertEqual(audit.unreachable_goals, {"s1"})
        self.assertEqual(state_closure_rate(graph, set(), {"s1"}), 0.0)
        self.assertEqual(unreachable_goal_rate(graph, set(), {"s1"}), 1.0)

    def test_state_is_not_closed_without_explicit_support_edge(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["seed"], ["s1"]), node("b", ["s1"], ["goal"])],
            edges=[AtomicTaskEdge("a", "b", "order")],
        )
        audit = causal_state_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.valid)
        self.assertEqual(audit.issues[0].node_id, "b")
        self.assertEqual(audit.issues[0].unsupported_states, ("s1",))

    def test_repair_adds_explicit_acyclic_support(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["seed"], ["s1"]), node("b", ["s1"], ["goal"])],
            edges=[],
        )
        repaired = repair_state_dependencies(graph, {"seed"})
        self.assertTrue(
            any(
                edge.source == "a" and edge.target == "b" and edge.type == "state_support"
                for edge in repaired.edges
            )
        )
        self.assertTrue(causal_state_audit(repaired, {"seed"}, {"goal"}).valid)

    def test_strict_scheduler_rejects_open_graph(self) -> None:
        graph = AtomicTaskGraph(nodes=[node("a", ["missing"], ["goal"])], edges=[])
        with self.assertRaises(PlanningValidationError):
            plan_graph(graph, initial_states=set(), goal_states={"goal"}, strict=True)


class OptimizationSafetyTests(unittest.TestCase):
    def test_resource_orientation_uses_shorter_critical_path(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("p", ["p0"], ["p1"], 10.0),
                node("left", ["p1"], ["left_done"], 1.0, ["shared"]),
                node("right", ["r0"], ["right_done"], 5.0, ["shared"]),
                node("q", ["right_done"], ["q_done"], 10.0),
            ],
            edges=[
                AtomicTaskEdge("p", "left", "state_support", state="p1"),
                AtomicTaskEdge("right", "q", "state_support", state="right_done"),
            ],
        )
        repaired = add_resource_mutex_edges(graph)
        self.assertTrue(
            any(
                edge.source == "right" and edge.target == "left" and edge.type == "resource_mutex"
                for edge in repaired.edges
            )
        )
        self.assertEqual(resource_conflict_pairs(repaired), [])

    def test_compression_releases_independent_order(self) -> None:
        order = AtomicTaskEdge("a", "b", "order")
        graph = AtomicTaskGraph(
            nodes=[node("a", ["a0"], ["a1"]), node("b", ["b0"], ["b1"])],
            edges=[order],
        )
        compressed = compress_redundant_order_edges(graph, {"a0", "b0"}, {"a1", "b1"})
        self.assertNotIn(order.key(), compressed.edge_keys())

    def test_compression_keeps_resource_protection(self) -> None:
        order = AtomicTaskEdge("a", "b", "order")
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["a0"], ["a1"], resources=["shared"]),
                node("b", ["b0"], ["b1"], resources=["shared"]),
            ],
            edges=[order],
        )
        compressed = compress_redundant_order_edges(graph, {"a0", "b0"}, {"a1", "b1"})
        self.assertIn(order.key(), compressed.edge_keys())

    def test_optimizer_reports_unrepairable_circular_support(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["s2"], ["s1"]), node("b", ["s1"], ["s2"])],
            edges=[],
        )
        result = optimize_graph_with_audit(graph, initial_states=set(), goal_states={"s1"})
        self.assertFalse(result.audit.valid)
        self.assertTrue(result.audit.failure_reasons)


class JointAuditGateTests(unittest.TestCase):
    def test_state_support_label_must_match_required_state(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["seed"], ["ready"]), node("b", ["ready"], ["goal"])],
            edges=[AtomicTaskEdge("a", "b", "state_support", state="bogus")],
        )
        audit = joint_graph_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.schema_valid)
        self.assertFalse(audit.closure_valid)

    def test_orphan_synchronization_is_rejected(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["seed"], ["ready"]), node("b", ["ready"], ["goal"])],
            edges=[
                AtomicTaskEdge("a", "b", "state_support", state="ready"),
                AtomicTaskEdge("a", "b", "synchronization", state="ready"),
            ],
        )
        audit = joint_graph_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.synchronization_complete)

    def test_wrong_state_label_cannot_pass_with_matching_wrong_sync(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["seed"], ["ready"]),
                AtomicTaskNode(
                    "b", "act", "b", ["ready"], ["goal"], 1.0, ["b"], ["both"], mode="cooperative"
                ),
            ],
            edges=[
                AtomicTaskEdge("a", "b", "state_support", state="wrong"),
                AtomicTaskEdge("a", "b", "synchronization", state="wrong"),
            ],
        )
        audit = joint_graph_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.valid)
        self.assertFalse(audit.schema_valid)
        self.assertFalse(audit.closure_valid)

    def test_resource_mutex_label_must_be_shared_by_both_endpoints(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["a0"], ["a1"], resources=["shared"]),
                node("b", ["b0"], ["b1"], resources=["shared"]),
            ],
            edges=[AtomicTaskEdge("a", "b", "resource_mutex", resource="wrong")],
        )
        audit = joint_graph_audit(graph, {"a0", "b0"}, {"a1", "b1"})
        self.assertFalse(audit.valid)
        self.assertFalse(audit.schema_valid)

    def test_mode_and_candidate_occupancy_must_agree(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                AtomicTaskNode(
                    "a", "act", "a", ["seed"], ["goal"], 1.0, [], ["both"], mode="single"
                )
            ],
            edges=[],
        )
        self.assertTrue(any("single mode" in issue for issue in graph_schema_issues(graph)))

    def test_same_arm_nodes_are_not_parallel_feasible(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                AtomicTaskNode("a", "act", "a", ["a0"], ["a1"], 1.0, [], ["left"]),
                AtomicTaskNode("b", "act", "b", ["b0"], ["b1"], 1.0, [], ["left"]),
            ],
            edges=[],
        )
        self.assertEqual(graph.incomparable_pairs(), [("a", "b")])
        self.assertEqual(graph.parallel_pairs(), [])

    def test_candidate_order_does_not_change_assignment(self) -> None:
        def assigned(candidates: list[str]) -> list[str]:
            graph = AtomicTaskGraph(
                nodes=[AtomicTaskNode("a", "act", "a", ["seed"], ["goal"], 1.0, [], candidates)],
                edges=[],
            )
            return plan_graph(graph, initial_states={"seed"}, goal_states={"goal"}).items[0].executors

        self.assertEqual(assigned(["left", "right"]), ["left"])
        self.assertEqual(assigned(["right", "left"]), ["left"])

    def test_precondition_order_does_not_change_repair(self) -> None:
        def repaired(preconditions: list[str]) -> set[tuple[str, str, str | None]]:
            graph = AtomicTaskGraph(
                nodes=[
                    node("p1", ["seed"], ["s1"]),
                    node("p2", ["seed"], ["s2"]),
                    node("c", preconditions, ["goal"]),
                ],
                edges=[],
            )
            result = repair_state_dependencies(graph, {"seed"})
            return {
                (edge.source, edge.target, edge.state)
                for edge in result.edges
                if edge.type == "state_support"
            }

        self.assertEqual(repaired(["s1", "s2"]), repaired(["s2", "s1"]))

    def test_fail_closed_pipeline_returns_no_schedule_for_cycle(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[node("a", ["seed"], ["a1"]), node("b", ["a1"], ["goal"])],
            edges=[AtomicTaskEdge("a", "b", "order"), AtomicTaskEdge("b", "a", "order")],
        )
        result = run_verified_atg(graph, {"seed"}, {"goal"})
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)
        self.assertTrue(result.failure_reasons)

    def test_node_parser_rejects_missing_required_fields(self) -> None:
        with self.assertRaises(KeyError):
            AtomicTaskNode.from_dict({"id": "a", "action": "act", "object": "a"})

    def test_generated_gold_graphs_pass_exact_sync_audit(self) -> None:
        records = generate_dataset(count=8, seed=13, duration_jitter=0.2)
        for record in records:
            audit = joint_graph_audit(
                record.gold_graph,
                set(record.initial_state["states"]),
                set(record.goal_state["states"]),
            )
            self.assertTrue(audit.valid, record.task_id)

    def test_complexity_reference_graphs_pass_typed_edge_audit(self) -> None:
        for node_count in (4, 6, 8, 10):
            record = _complexity_record(node_count, 1)
            audit = joint_graph_audit(
                record.gold_graph,
                set(record.initial_state["states"]),
                set(record.goal_state["states"]),
            )
            self.assertTrue(audit.valid, f"{node_count}: {audit.failure_reasons()}")

    def test_disabled_repairs_retain_existing_typed_edges(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["seed"], ["ready"]),
                AtomicTaskNode(
                    "b", "act", "b", ["ready"], ["goal"], 1.0, ["shared"], ["both"], mode="cooperative"
                ),
            ],
            edges=[
                AtomicTaskEdge("a", "b", "state_support", state="ready"),
                AtomicTaskEdge("a", "b", "synchronization", state="ready"),
            ],
        )
        result = optimize_graph_with_audit(
            graph,
            {"seed"},
            {"goal"},
            use_state_dependency=False,
            use_synchronization_repair=False,
            use_resource_constraint=False,
            use_critical_path=False,
        )
        self.assertEqual(result.graph.edge_keys(), graph.edge_keys())

    def test_executor_perturbation_changes_every_record(self) -> None:
        records = generate_dataset(count=160, seed=13, duration_jitter=0.2)
        for index, record in enumerate(records):
            changed = _apply_annotation_perturbation(
                record.gold_graph,
                "executor-label change",
                seed=index + 101,
            )
            before = {node.id: set(node.candidate_arm) for node in record.gold_graph.nodes}
            after = {node.id: set(node.candidate_arm) for node in changed.nodes}
            self.assertTrue(any(before[node_id] != after[node_id] for node_id in before), record.task_id)

    def test_parallel_precision_is_undefined_when_no_pair_is_predicted(self) -> None:
        record = generate_dataset(count=1, seed=13, duration_jitter=0.2)[0]
        graph = make_sequential_graph(record.gold_graph)
        plan = plan_graph(
            graph,
            initial_states=set(record.initial_state["states"]),
            goal_states=set(record.goal_state["states"]),
            strict=True,
        )
        metrics = dependency_safety(graph, record.gold_graph, plan)
        self.assertEqual(metrics["Predicted Parallel Pairs"], 0)
        self.assertIsNone(metrics["Parallel Precision"])
        self.assertIsNone(metrics["False Parallel"])

    def test_exported_schema_allows_resource_free_nodes(self) -> None:
        schema = atomic_task_graph_json_schema()
        resource_schema = schema["properties"]["nodes"]["items"]["properties"]["resource"]
        self.assertNotIn("minItems", resource_schema)

        graph = AtomicTaskGraph(
            nodes=[AtomicTaskNode("a", "act", "a", ["seed"], ["goal"], 1.0, [], ["left"])],
            edges=[],
        )
        self.assertTrue(joint_graph_audit(graph, {"seed"}, {"goal"}).schema_valid)

    def test_strict_scheduler_rejects_unordered_shared_resource(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                AtomicTaskNode("a", "act", "a", ["a0"], ["a1"], 1.0, ["shared"], ["left"]),
                AtomicTaskNode("b", "act", "b", ["b0"], ["b1"], 1.0, ["shared"], ["right"]),
            ],
            edges=[],
        )
        with self.assertRaises(PlanningValidationError):
            plan_graph(graph, initial_states={"a0", "b0"}, goal_states={"a1", "b1"}, strict=True)

    def test_strict_scheduler_rejects_missing_cooperative_sync(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["seed"], ["ready"]),
                AtomicTaskNode(
                    "b",
                    "act",
                    "b",
                    ["ready"],
                    ["goal"],
                    1.0,
                    ["b"],
                    ["both"],
                    mode="cooperative",
                ),
            ],
            edges=[AtomicTaskEdge("a", "b", "state_support", state="ready")],
        )
        audit = joint_graph_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.synchronization_complete)
        with self.assertRaises(PlanningValidationError):
            plan_graph(graph, initial_states={"seed"}, goal_states={"goal"}, strict=True)

    def test_synchronization_edge_does_not_replace_state_support(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["seed"], ["ready"]),
                AtomicTaskNode(
                    "b",
                    "act",
                    "b",
                    ["ready"],
                    ["goal"],
                    1.0,
                    ["b"],
                    ["both"],
                    mode="cooperative",
                ),
            ],
            edges=[AtomicTaskEdge("a", "b", "synchronization", state="ready")],
        )
        audit = joint_graph_audit(graph, {"seed"}, {"goal"})
        self.assertFalse(audit.closure_valid)
        self.assertFalse(audit.goal_reachable)

    def test_optimizer_produces_jointly_accepted_graph(self) -> None:
        graph = AtomicTaskGraph(
            nodes=[
                node("a", ["seed"], ["ready"]),
                AtomicTaskNode(
                    "b",
                    "act",
                    "b",
                    ["ready"],
                    ["goal"],
                    1.0,
                    ["b"],
                    ["both"],
                    mode="cooperative",
                ),
            ],
            edges=[],
        )
        result = optimize_graph_with_audit(graph, initial_states={"seed"}, goal_states={"goal"})
        self.assertTrue(result.audit.valid)
        self.assertTrue(result.audit.joint_after["checks"]["synchronization_complete"])
        replayed = replay_accepted_events(graph, result.audit.events)
        self.assertEqual(replayed.edge_keys(), result.graph.edge_keys())

    def test_controlled_challenges_are_rejected_by_joint_audit(self) -> None:
        record = generate_dataset(count=1, seed=13, duration_jitter=0.2)[0]
        initial = set(record.initial_state["states"])
        goals = set(record.goal_state["states"])
        refined = optimize_graph_with_audit(
            record.gold_graph,
            initial_states=initial,
            goal_states=goals,
        ).graph
        for challenge in [
            "Schema-invalid executor label",
            "Open precondition",
            "Directed cycle",
            "Missing synchronization",
            "Wrong state-support label",
            "Orphan synchronization",
            "Invalid resource label",
            "Unordered shared resource",
            "Unreachable goal",
        ]:
            challenged, challenged_goals = _joint_audit_challenge_graph(
                refined,
                challenge,
                initial,
                goals,
            )
            self.assertFalse(
                joint_graph_audit(challenged, initial, challenged_goals).valid,
                challenge,
            )


if __name__ == "__main__":
    unittest.main()
