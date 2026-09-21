from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .optimization import OptimizationAudit, optimize_graph_with_audit
from .planning import PlanTimeline, PlanningValidationError, plan_graph
from .schema import AtomicTaskGraph
from .verification import graph_schema_issues


@dataclass
class VerifiedPlanningResult:
    """Fail-closed result for the full graph-repair and scheduling pipeline."""

    accepted: bool
    graph: AtomicTaskGraph | None = None
    audit: OptimizationAudit | None = None
    schedule: PlanTimeline | None = None
    failure_reasons: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "accepted": self.accepted,
            "graph": self.graph.to_dict() if self.graph is not None else None,
            "audit": self.audit.to_dict() if self.audit is not None else None,
            "schedule": self.schedule.to_dict() if self.schedule is not None else None,
            "failure_reasons": list(self.failure_reasons),
        }


def run_verified_atg(
    graph: AtomicTaskGraph | dict[str, Any],
    initial_states: set[str] | None = None,
    goal_states: set[str] | None = None,
    *,
    use_state_dependency: bool = True,
    use_synchronization_repair: bool = True,
    use_resource_constraint: bool = True,
    use_critical_path: bool = True,
    use_executor_assignment: bool = True,
) -> VerifiedPlanningResult:
    """Run strict parsing assumptions, repair, audit, and conditional scheduling.

    Expected validation failures are returned as data.  No schedule is exposed
    unless the refined graph passes the complete joint audit.
    """

    try:
        if isinstance(graph, dict):
            graph = AtomicTaskGraph.from_dict(graph)
        elif not isinstance(graph, AtomicTaskGraph):
            raise TypeError("graph must be an AtomicTaskGraph or a JSON object")
        structure_issues = graph_schema_issues(graph, check_relationships=False)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        return VerifiedPlanningResult(
            accepted=False, failure_reasons=[f"schema validation failed: {exc}"]
        )
    if structure_issues:
        return VerifiedPlanningResult(accepted=False, failure_reasons=structure_issues)

    try:
        optimized = optimize_graph_with_audit(
            graph,
            initial_states=initial_states,
            goal_states=goal_states,
            use_state_dependency=use_state_dependency,
            use_synchronization_repair=use_synchronization_repair,
            use_resource_constraint=use_resource_constraint,
            use_critical_path=use_critical_path,
        )
    except (KeyError, TypeError, ValueError) as exc:
        return VerifiedPlanningResult(
            accepted=False,
            failure_reasons=[f"optimization failed: {exc}"],
        )

    if not optimized.audit.valid:
        return VerifiedPlanningResult(
            accepted=False,
            graph=optimized.graph,
            audit=optimized.audit,
            failure_reasons=list(optimized.audit.failure_reasons),
        )

    try:
        schedule = plan_graph(
            optimized.graph,
            use_executor_assignment=use_executor_assignment,
            initial_states=initial_states,
            goal_states=goal_states,
            strict=True,
        )
    except (PlanningValidationError, KeyError, TypeError, ValueError) as exc:
        return VerifiedPlanningResult(
            accepted=False,
            graph=optimized.graph,
            audit=optimized.audit,
            failure_reasons=[f"planning failed: {exc}"],
        )

    if not schedule.valid:
        return VerifiedPlanningResult(
            accepted=False,
            graph=optimized.graph,
            audit=optimized.audit,
            failure_reasons=list(schedule.violations or ["schedule failed validation"]),
        )

    return VerifiedPlanningResult(
        accepted=True,
        graph=optimized.graph,
        audit=optimized.audit,
        schedule=schedule,
    )
