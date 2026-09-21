from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, field
from heapq import heappop, heappush
from math import isfinite
from typing import Any


VALID_ARMS = {"left", "right", "both"}
VALID_MODES = {"single", "cooperative"}
VALID_EDGE_TYPES = {"state_support", "resource_mutex", "synchronization", "order"}


def _require_object(data: Any, name: str) -> None:
    if not isinstance(data, dict):
        raise TypeError(f"{name} must be a JSON object")


def _require_text(value: Any, name: str) -> None:
    if not isinstance(value, str):
        raise TypeError(f"{name} must be a string")


def _require_string_list(value: Any, name: str) -> None:
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise TypeError(f"{name} must be an array of strings")


def node_sort_key(node_id: str) -> tuple[int, int, str]:
    """Canonical order used whenever the abstract graph has a tie."""
    digits = "".join(ch for ch in node_id if ch.isdigit())
    if digits:
        return (0, int(digits), node_id)
    return (1, 0, node_id)


def executor_occupancies(node: "AtomicTaskNode") -> tuple[frozenset[str], ...]:
    """Return the base-executor occupancy alternatives allowed by a node."""
    if node.mode == "cooperative":
        return (frozenset({"left", "right"}),)
    order = {"left": 0, "right": 1}
    arms = sorted({arm for arm in node.candidate_arm if arm in order}, key=order.get)
    return tuple(frozenset({arm}) for arm in arms)


@dataclass
class AtomicTaskNode:
    id: str
    action: str
    object_name: str
    pre_state: list[str]
    post_state: list[str]
    duration: float
    resource: list[str]
    candidate_arm: list[str]
    mode: str = "single"
    workspace: str = "shared"
    target: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "id": self.id,
            "action": self.action,
            "object": self.object_name,
            "pre_state": list(self.pre_state),
            "post_state": list(self.post_state),
            "duration": self.duration,
            "resource": list(self.resource),
            "candidate_arm": list(self.candidate_arm),
            "mode": self.mode,
            "workspace": self.workspace,
        }
        if self.target is not None:
            data["target"] = self.target
        if self.metadata:
            data["metadata"] = dict(self.metadata)
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AtomicTaskNode":
        # Check raw JSON types before conversion can hide malformed input.
        # Value and relationship semantics remain the joint audit's responsibility.
        _require_object(data, "node")
        for key in ("id", "action", "object", "mode"):
            _require_text(data[key], key)
        for key in ("pre_state", "post_state", "resource", "candidate_arm"):
            _require_string_list(data[key], key)
        duration = data["duration"]
        if isinstance(duration, bool) or not isinstance(duration, (int, float)):
            raise TypeError("duration must be a number, not a boolean or numeric string")
        try:
            finite_duration = isfinite(duration)
        except OverflowError as exc:
            raise ValueError("duration exceeds the supported numeric range") from exc
        if not finite_duration or duration <= 0:
            raise ValueError("duration must be finite and positive")
        if "workspace" in data:
            _require_text(data["workspace"], "workspace")
        if "target" in data:
            _require_text(data["target"], "target")
        if "metadata" in data:
            _require_object(data["metadata"], "metadata")
        return cls(
            id=data["id"],
            action=data["action"],
            object_name=data["object"],
            pre_state=list(data["pre_state"]),
            post_state=list(data["post_state"]),
            duration=float(data["duration"]),
            resource=list(data["resource"]),
            candidate_arm=list(data["candidate_arm"]),
            mode=data["mode"],
            workspace=data.get("workspace", "shared"),
            target=data.get("target"),
            metadata=dict(data.get("metadata", {})),
        )


@dataclass(frozen=True)
class AtomicTaskEdge:
    source: str
    target: str
    type: str
    reason: str = ""
    state: str | None = None
    resource: str | None = None

    def key(self) -> tuple[str, str, str, str | None, str | None]:
        return (self.source, self.target, self.type, self.state, self.resource)

    def to_dict(self) -> dict[str, Any]:
        data = {
            "source": self.source,
            "target": self.target,
            "type": self.type,
            "reason": self.reason,
        }
        if self.state is not None:
            data["state"] = self.state
        if self.resource is not None:
            data["resource"] = self.resource
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AtomicTaskEdge":
        _require_object(data, "edge")
        for key in ("source", "target", "type"):
            _require_text(data[key], key)
        for key in ("reason", "state", "resource"):
            if key in data:
                _require_text(data[key], key)
        return cls(
            source=data["source"],
            target=data["target"],
            type=data["type"],
            reason=data.get("reason", ""),
            state=data.get("state"),
            resource=data.get("resource"),
        )


@dataclass
class AtomicTaskGraph:
    nodes: list[AtomicTaskNode]
    edges: list[AtomicTaskEdge]

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [node.to_dict() for node in self.nodes],
            "edges": [edge.to_dict() for edge in self.edges],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AtomicTaskGraph":
        _require_object(data, "graph")
        for key in ("nodes", "edges"):
            if not isinstance(data[key], list):
                raise TypeError(f"{key} must be an array")
        return cls(
            nodes=[AtomicTaskNode.from_dict(item) for item in data["nodes"]],
            edges=[AtomicTaskEdge.from_dict(item) for item in data["edges"]],
        )

    def copy(self) -> "AtomicTaskGraph":
        return AtomicTaskGraph.from_dict(self.to_dict())

    @property
    def node_map(self) -> dict[str, AtomicTaskNode]:
        return {node.id: node for node in self.nodes}

    def edge_keys(self) -> set[tuple[str, str, str, str | None, str | None]]:
        return {edge.key() for edge in self.edges}

    def add_edge(self, edge: AtomicTaskEdge) -> None:
        if edge.key() not in self.edge_keys():
            self.edges.append(edge)

    def remove_edge(self, edge: AtomicTaskEdge) -> None:
        self.edges = [item for item in self.edges if item.key() != edge.key()]

    def predecessors(self) -> dict[str, list[AtomicTaskEdge]]:
        pred: dict[str, list[AtomicTaskEdge]] = defaultdict(list)
        for edge in self.edges:
            pred[edge.target].append(edge)
        return pred

    def successors(self) -> dict[str, list[AtomicTaskEdge]]:
        succ: dict[str, list[AtomicTaskEdge]] = defaultdict(list)
        for edge in self.edges:
            succ[edge.source].append(edge)
        return succ

    def topological_order(self) -> list[str]:
        node_ids = [node.id for node in self.nodes]
        indegree = {node_id: 0 for node_id in node_ids}
        succ = defaultdict(list)
        for edge in self.edges:
            if edge.source not in indegree or edge.target not in indegree:
                continue
            indegree[edge.target] += 1
            succ[edge.source].append(edge.target)
        queue: list[tuple[tuple[int, int, str], str]] = []
        for node_id in node_ids:
            if indegree[node_id] == 0:
                heappush(queue, (node_sort_key(node_id), node_id))
        order: list[str] = []
        while queue:
            _, node_id = heappop(queue)
            order.append(node_id)
            for child in sorted(succ[node_id], key=node_sort_key):
                indegree[child] -= 1
                if indegree[child] == 0:
                    heappush(queue, (node_sort_key(child), child))
        if len(order) != len(node_ids):
            raise ValueError("graph contains a cycle")
        return order

    def has_path(self, source: str, target: str, ignore_edge: AtomicTaskEdge | None = None) -> bool:
        if source == target:
            return True
        succ = self.successors()
        seen = {source}
        queue = deque([source])
        while queue:
            cur = queue.popleft()
            for edge in succ.get(cur, []):
                if ignore_edge is not None and edge.key() == ignore_edge.key():
                    continue
                nxt = edge.target
                if nxt == target:
                    return True
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append(nxt)
        return False

    def incomparable_pairs(self) -> list[tuple[str, str]]:
        ids = sorted((node.id for node in self.nodes), key=node_sort_key)
        pairs: list[tuple[str, str]] = []
        for i, left in enumerate(ids):
            for right in ids[i + 1 :]:
                if not self.has_path(left, right) and not self.has_path(right, left):
                    pairs.append((left, right))
        return pairs

    def parallel_pairs(self) -> list[tuple[str, str]]:
        """Static parallel-feasible pairs, excluding resource and arm conflicts."""
        node_map = self.node_map
        supports = {
            (edge.source, edge.target, edge.state)
            for edge in self.edges
            if edge.type == "state_support" and edge.state is not None
        }
        syncs = {
            (edge.source, edge.target, edge.state)
            for edge in self.edges
            if edge.type == "synchronization"
        }

        def sync_complete(node_id: str) -> bool:
            node = node_map[node_id]
            required = {item for item in supports if item[1] == node_id} if node.mode == "cooperative" else set()
            actual = {item for item in syncs if item[1] == node_id}
            return required == actual

        pairs: list[tuple[str, str]] = []
        for left, right in self.incomparable_pairs():
            left_node = node_map[left]
            right_node = node_map[right]
            if set(left_node.resource) & set(right_node.resource):
                continue
            if not sync_complete(left) or not sync_complete(right):
                continue
            if any(
                left_occ.isdisjoint(right_occ)
                for left_occ in executor_occupancies(left_node)
                for right_occ in executor_occupancies(right_node)
            ):
                pairs.append((left, right))
        return pairs


@dataclass
class TaskRecord:
    task_id: str
    domain: str
    instruction: str
    initial_state: dict[str, Any]
    goal_state: dict[str, Any]
    scene: dict[str, Any]
    gold_graph: AtomicTaskGraph

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "domain": self.domain,
            "instruction": self.instruction,
            "initial_state": self.initial_state,
            "goal_state": self.goal_state,
            "scene": self.scene,
            "gold_graph": self.gold_graph.to_dict(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TaskRecord":
        return cls(
            task_id=str(data["task_id"]),
            domain=str(data["domain"]),
            instruction=str(data["instruction"]),
            initial_state=dict(data["initial_state"]),
            goal_state=dict(data["goal_state"]),
            scene=dict(data.get("scene", {})),
            gold_graph=AtomicTaskGraph.from_dict(data["gold_graph"]),
        )


def atomic_task_graph_json_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "AtomicTaskGraph",
        "type": "object",
        "required": ["nodes", "edges"],
        "properties": {
            "nodes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "id",
                        "action",
                        "object",
                        "pre_state",
                        "post_state",
                        "duration",
                        "resource",
                        "candidate_arm",
                        "mode",
                    ],
                    "properties": {
                        "id": {"type": "string", "minLength": 1},
                        "action": {"type": "string", "minLength": 1},
                        "object": {"type": "string", "minLength": 1},
                        "pre_state": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                            "uniqueItems": True,
                        },
                        "post_state": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                            "uniqueItems": True,
                        },
                        "duration": {"type": "number", "exclusiveMinimum": 0},
                        "resource": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "uniqueItems": True,
                        },
                        "candidate_arm": {
                            "type": "array",
                            "items": {"enum": sorted(VALID_ARMS)},
                            "minItems": 1,
                            "uniqueItems": True,
                        },
                        "mode": {"enum": sorted(VALID_MODES)},
                        "workspace": {"type": "string"},
                        "target": {"type": "string"},
                    },
                    "allOf": [
                        {
                            "if": {"properties": {"mode": {"const": "cooperative"}}},
                            "then": {"properties": {"candidate_arm": {"const": ["both"]}}},
                        },
                        {
                            "if": {"properties": {"mode": {"const": "single"}}},
                            "then": {
                                "properties": {
                                    "candidate_arm": {
                                        "items": {"enum": ["left", "right"]}
                                    }
                                }
                            },
                        },
                    ],
                },
            },
            "edges": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["source", "target", "type"],
                    "properties": {
                        "source": {"type": "string"},
                        "target": {"type": "string"},
                        "type": {"enum": sorted(VALID_EDGE_TYPES)},
                        "reason": {"type": "string"},
                        "state": {"type": "string"},
                        "resource": {"type": "string"},
                    },
                    "allOf": [
                        {
                            "if": {
                                "properties": {
                                    "type": {"enum": ["state_support", "synchronization"]}
                                },
                                "required": ["type"],
                            },
                            "then": {"required": ["state"]},
                        },
                        {
                            "if": {
                                "properties": {"type": {"const": "resource_mutex"}},
                                "required": ["type"],
                            },
                            "then": {"required": ["resource"]},
                        },
                    ],
                },
            },
        },
    }
