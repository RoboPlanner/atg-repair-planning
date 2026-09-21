from __future__ import annotations

import copy
import unittest

from atomic_task.extended_experiments import _parallel_f1
from atomic_task.metrics import dependency_safety, parallel_prf, summarize
from atomic_task.optimization import optimize_graph_with_audit, replay_accepted_events
from atomic_task.pipeline import run_verified_atg
from atomic_task.planning import PlannedStep, PlanningValidationError, plan_graph, schedule_issues
from atomic_task.schema import AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode
from atomic_task.verification import graph_schema_issues, joint_graph_audit


def raw_node() -> dict[str, object]:
    return {
        "id": "t1", "action": "act", "object": "cup", "pre_state": ["seed"],
        "post_state": ["goal"], "duration": 1, "resource": [],
        "candidate_arm": ["left"], "mode": "single",
    }


def one_node(mode: str = "single", candidates: list[str] | None = None) -> AtomicTaskGraph:
    data = raw_node()
    data["mode"] = mode
    data["candidate_arm"] = candidates or (["both"] if mode == "cooperative" else ["left"])
    return AtomicTaskGraph.from_dict({"nodes": [data], "edges": []})


class InputBoundaryTests(unittest.TestCase):
    def test_object_boolean_duration_is_rejected_at_schema_gate(self) -> None:
        graph = one_node()
        graph.nodes[0].duration = True
        self.assertTrue(any("duration" in issue for issue in graph_schema_issues(graph)))
        result = run_verified_atg(graph, {"seed"}, {"goal"})
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)
        self.assertIsNone(result.audit)
        self.assertTrue(any("duration" in issue for issue in result.failure_reasons))

    def test_object_string_precondition_cannot_be_normalized_into_characters(self) -> None:
        for malformed_pre in ("x", "xyz"):
            with self.subTest(pre=malformed_pre):
                graph = one_node()
                graph.nodes[0].pre_state = malformed_pre
                self.assertTrue(any("pre_state" in issue for issue in graph_schema_issues(graph)))
                result = run_verified_atg(graph, set(malformed_pre), {"goal"})
                self.assertFalse(result.accepted)
                self.assertIsNone(result.schedule)
                self.assertIsNone(result.audit)
                self.assertEqual(graph.nodes[0].pre_state, malformed_pre)

    def test_overflowing_integer_duration_returns_diagnostic(self) -> None:
        data = raw_node()
        data["duration"] = 10 ** 10000
        with self.assertRaisesRegex(ValueError, "numeric range"):
            AtomicTaskNode.from_dict(data)
        raw_result = run_verified_atg({"nodes": [data], "edges": []}, {"seed"}, {"goal"})
        self.assertFalse(raw_result.accepted)
        self.assertIsNone(raw_result.schedule)
        self.assertIn("schema validation failed", raw_result.failure_reasons[0])
        graph = one_node()
        graph.nodes[0].duration = 10 ** 10000
        object_result = run_verified_atg(graph, {"seed"}, {"goal"})
        self.assertFalse(object_result.accepted)
        self.assertIsNone(object_result.schedule)
        self.assertIn("schema validation failed", object_result.failure_reasons[0])

    def test_raw_node_types_are_rejected_before_coercion(self) -> None:
        bad_fields = {
            "id": [None, 4, []], "action": [None, True], "object": [None, 3],
            "pre_state": ["seed", {"seed": 1}, [None]],
            "post_state": ["goal", [1]], "resource": ["cup", [False]],
            "candidate_arm": ["left", [None]], "mode": [None, False],
            "duration": [True, False, "1.0", None, float("nan"), float("inf"), 0, -1],
        }
        for field, values in bad_fields.items():
            for value in values:
                with self.subTest(field=field, value=value):
                    data = raw_node()
                    data[field] = value
                    with self.assertRaises((TypeError, ValueError)):
                        AtomicTaskNode.from_dict(data)
                    result = run_verified_atg({"nodes": [data], "edges": []}, {"seed"}, {"goal"})
                    self.assertFalse(result.accepted)
                    self.assertIsNone(result.schedule)
                    self.assertIn("schema validation failed", result.failure_reasons[0])

    def test_required_graph_containers_and_edge_types_are_checked(self) -> None:
        invalid = [
            {}, {"nodes": [], "edges": None}, {"nodes": "bad", "edges": []},
            {"nodes": [raw_node()], "edges": [{"source": None, "target": "t1", "type": "order"}]},
            {"nodes": [raw_node()], "edges": [{"source": "t1", "target": "t2", "type": "state_support", "state": []}]},
        ]
        for data in invalid:
            with self.subTest(data=data):
                result = run_verified_atg(data, {"seed"}, {"goal"})
                self.assertFalse(result.accepted)
                self.assertIsNone(result.schedule)

    def test_valid_raw_input_and_object_have_identical_results(self) -> None:
        raw = {"nodes": [raw_node()], "edges": []}
        before = copy.deepcopy(raw)
        parsed = AtomicTaskGraph.from_dict(raw)
        object_result = run_verified_atg(parsed, {"seed"}, {"goal"})
        raw_result = run_verified_atg(raw, {"seed"}, {"goal"})
        self.assertTrue(raw_result.accepted)
        self.assertEqual(raw_result.to_dict(), object_result.to_dict())
        self.assertEqual(raw, before)

    def test_semantically_mislabeled_edges_still_enter_repair(self) -> None:
        graph = AtomicTaskGraph(
            [AtomicTaskNode("p", "act", "p", ["seed"], ["ready"], 1, ["shared"], ["left"]),
             AtomicTaskNode("c", "act", "c", ["ready"], ["goal"], 1, ["shared"], ["right"])],
            [AtomicTaskEdge("p", "c", "state_support", state="wrong"),
             AtomicTaskEdge("p", "c", "resource_mutex", resource="wrong")],
        )
        result = run_verified_atg(graph.to_dict(), {"seed"}, {"goal"})
        self.assertTrue(result.accepted, result.failure_reasons)
        self.assertNotIn(("p", "c", "state_support", "wrong", None), result.graph.edge_keys())
        self.assertNotIn(("p", "c", "resource_mutex", None, "wrong"), result.graph.edge_keys())
        self.assertEqual(replay_accepted_events(graph, result.audit.events).edge_keys(), result.graph.edge_keys())


class AcceptedScheduleTests(unittest.TestCase):
    def test_disabled_assignment_cannot_accept_cooperative_left_only(self) -> None:
        graph = one_node("cooperative")
        result = run_verified_atg(graph, {"seed"}, {"goal"}, use_executor_assignment=False)
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)
        self.assertTrue(any("occupancy" in issue for issue in result.failure_reasons))
        with self.assertRaises(PlanningValidationError):
            plan_graph(graph, False, {"seed"}, {"goal"}, strict=True)

    def test_disabled_assignment_cannot_accept_wrong_single_candidate(self) -> None:
        graph = one_node(candidates=["right"])
        result = run_verified_atg(graph, {"seed"}, {"goal"}, use_executor_assignment=False)
        self.assertFalse(result.accepted)
        self.assertIsNone(result.schedule)

    def test_diagnostic_ablation_remains_available_but_marked_invalid(self) -> None:
        plan = plan_graph(one_node("cooperative"), False, {"seed"}, {"goal"}, strict=False)
        self.assertEqual(plan.items[0].executors, ["left"])
        self.assertFalse(plan.valid)
        self.assertEqual(plan.sync_stability, 0.0)

    def test_valid_default_and_compatible_disabled_assignment_are_accepted(self) -> None:
        coop = run_verified_atg(one_node("cooperative"), {"seed"}, {"goal"})
        self.assertTrue(coop.accepted)
        self.assertEqual(coop.schedule.items[0].executors, ["left", "right"])
        single = run_verified_atg(one_node(), {"seed"}, {"goal"}, use_executor_assignment=False)
        self.assertTrue(single.accepted)

    def test_output_validator_detects_overlaps_and_missing_nodes(self) -> None:
        graph = AtomicTaskGraph(
            [AtomicTaskNode("a", "act", "a", ["seed"], ["a1"], 1, ["r"], ["left"]),
             AtomicTaskNode("b", "act", "b", ["seed"], ["b1"], 1, ["r"], ["left"])], [],
        )
        items = [PlannedStep(n.id, n.action, n.object_name, 0, 1, ["left"], ["r"]) for n in graph.nodes]
        issues = schedule_issues(graph, items)
        self.assertTrue(any("base-executor" in issue for issue in issues))
        self.assertTrue(any("capacity-1" in issue for issue in issues))
        self.assertTrue(any("exactly once" in issue for issue in schedule_issues(graph, items[:1])))

    def test_existing_support_in_initial_state_still_requires_exact_sync(self) -> None:
        graph = AtomicTaskGraph(
            [AtomicTaskNode("p", "act", "p", ["seed"], ["s"], 1, [], ["left"]),
             AtomicTaskNode("c", "act", "c", ["s"], ["goal"], 1, [], ["both"], "cooperative")],
            [AtomicTaskEdge("p", "c", "state_support", state="s")],
        )
        self.assertFalse(joint_graph_audit(graph, {"seed", "s"}, {"goal"}).synchronization_complete)
        result = optimize_graph_with_audit(graph, {"seed", "s"}, {"goal"})
        self.assertTrue(result.audit.valid)
        self.assertIn(("p", "c", "synchronization", "s", None), result.graph.edge_keys())


class ParallelMetricBoundaryTests(unittest.TestCase):
    def test_empty_reference_keeps_recall_and_f1_undefined(self) -> None:
        for predicted in (0, 2):
            scores = parallel_prf(0, predicted, 0)
            self.assertIsNone(scores["Parallel Recall"])
            self.assertIsNone(scores["Parallel F1"])
            self.assertEqual(scores["Parallel Precision"], 0.0 if predicted else None)

    def test_empty_prediction_with_nonempty_reference_has_zero_recall_f1(self) -> None:
        scores = parallel_prf(0, 0, 2)
        self.assertIsNone(scores["Parallel Precision"])
        self.assertEqual(scores["Parallel Recall"], 0.0)
        self.assertEqual(scores["Parallel F1"], 0.0)

    def test_extended_metric_and_summary_preserve_empty_reference(self) -> None:
        graph = one_node()
        scores = dependency_safety(graph, graph, plan_graph(graph))
        self.assertIsNone(scores["Parallel F1"])
        self.assertIsNone(_parallel_f1(graph, graph))
        rows = [{"group": "a", "F1": None}, {"group": "a", "F1": 0.8}]
        self.assertEqual(summarize(rows, "group", ["F1"])[0]["F1"], 0.8)
        self.assertEqual(summarize(rows[:1], "group", ["F1"])[0]["F1"], "")


if __name__ == "__main__":
    unittest.main()
