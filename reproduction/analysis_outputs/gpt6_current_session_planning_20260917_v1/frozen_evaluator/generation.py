from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Callable

from .schema import AtomicTaskEdge, AtomicTaskGraph, AtomicTaskNode, TaskRecord
from .verification import joint_graph_audit


def generation_prompt_template() -> str:
    return (
        "Given a natural-language task, initial scene state, and goal state, "
        "output an atomic task graph in JSON. Each node must include id, action, "
        "object, pre_state, post_state, duration, resource, candidate_arm, and "
        "mode. The resource array may be empty when no exclusive resource is "
        "declared. Each edge must explain its source as state_support, "
        "resource_mutex, synchronization, or order. Do not add dependencies only "
        "because the text order suggests them; when a dependency comes from an "
        "object state producer-consumer relation, explicitly name the state. A "
        "synchronization edge marks cooperative joint-start readiness and must "
        "pair with a matching state_support edge; it cannot replace causal support."
    )


def _node(
    node_id: str,
    action: str,
    object_name: str,
    pre: list[str],
    post: list[str],
    duration: float,
    resources: list[str],
    arms: list[str],
    mode: str = "single",
    workspace: str = "shared",
    target: str | None = None,
) -> AtomicTaskNode:
    return AtomicTaskNode(
        id=node_id,
        action=action,
        object_name=object_name,
        pre_state=pre,
        post_state=post,
        duration=duration,
        resource=resources,
        candidate_arm=arms,
        mode=mode,
        workspace=workspace,
        target=target,
    )


def _state_edges(nodes: list[AtomicTaskNode]) -> list[AtomicTaskEdge]:
    producer: dict[str, str] = {}
    for node in nodes:
        for state in node.post_state:
            producer[state] = node.id
    edges: list[AtomicTaskEdge] = []
    for node in nodes:
        for state in node.pre_state:
            source = producer.get(state)
            if source is not None and source != node.id:
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


def _graph(nodes: list[AtomicTaskNode], extra_edges: list[AtomicTaskEdge]) -> AtomicTaskGraph:
    graph = AtomicTaskGraph(nodes=nodes, edges=[])
    for edge in _state_edges(nodes) + extra_edges:
        graph.add_edge(edge)
    return graph


def _scene(objects: list[str]) -> dict[str, object]:
    return {
        "objects": objects,
        "workspace": ["left_zone", "right_zone", "shared_zone"],
        "arms": {
            "left": {"reachable": ["left_zone", "shared_zone"]},
            "right": {"reachable": ["right_zone", "shared_zone"]},
        },
    }


def _with_jitter(nodes: list[AtomicTaskNode], rng: random.Random, jitter: float) -> list[AtomicTaskNode]:
    output: list[AtomicTaskNode] = []
    for node in nodes:
        item = AtomicTaskNode.from_dict(node.to_dict())
        scale = 1.0 + rng.uniform(-jitter, jitter)
        item.duration = round(max(0.5, item.duration * scale), 2)
        output.append(item)
    return output


def _pour_drink(index: int, rng: random.Random, jitter: float) -> TaskRecord:
    nodes = _with_jitter(
        [
            _node("v1", "stabilize", "cup", ["cup_on_mat"], ["cup_stabilized"], 2.0, ["cup"], ["left", "right"]),
            _node("v2", "grasp", "kettle", ["kettle_on_stand"], ["kettle_grasped"], 2.5, ["kettle"], ["right"]),
            _node(
                "v3",
                "pour",
                "kettle",
                ["cup_stabilized", "kettle_grasped", "water_in_kettle"],
                ["cup_filled"],
                5.0,
                ["cup", "kettle"],
                ["both"],
                mode="cooperative",
                target="cup",
            ),
            _node("v4", "place", "kettle", ["kettle_grasped", "cup_filled"], ["kettle_returned"], 1.5, ["kettle"], ["right"]),
            _node("v5", "insert", "tea_bag", ["tea_bag_available", "cup_filled"], ["tea_bag_in_cup"], 2.0, ["tea_bag", "cup"], ["left", "right"]),
            _node("v6", "stir", "spoon", ["spoon_available", "tea_bag_in_cup"], ["drink_ready"], 3.0, ["spoon", "cup"], ["left", "right"]),
        ],
        rng,
        jitter,
    )
    graph = _graph(
        nodes,
        [
            AtomicTaskEdge(
                "v1",
                "v3",
                "synchronization",
                state="cup_stabilized",
                reason="cup must be held while pouring",
            ),
            AtomicTaskEdge(
                "v2",
                "v3",
                "synchronization",
                state="kettle_grasped",
                reason="kettle must be held while pouring",
            ),
        ],
    )
    return TaskRecord(
        task_id=f"pour_drink_{index:03d}",
        domain="tabletop_drink",
        instruction="Use both arms to stabilize the cup, lift the kettle, pour water, add a tea bag, and stir the drink.",
        initial_state={
            "states": ["cup_on_mat", "kettle_on_stand", "water_in_kettle", "tea_bag_available", "spoon_available"]
        },
        goal_state={"states": ["drink_ready", "kettle_returned"]},
        scene=_scene(["cup", "kettle", "tea_bag", "spoon"]),
        gold_graph=graph,
    )


def _pack_box(index: int, rng: random.Random, jitter: float) -> TaskRecord:
    nodes = _with_jitter(
        [
            _node("v1", "open", "box", ["box_closed"], ["box_open"], 2.0, ["box"], ["left", "right"]),
            _node("v2", "grasp", "snack", ["snack_on_table"], ["snack_grasped"], 1.5, ["snack"], ["left"]),
            _node("v3", "grasp", "bottle", ["bottle_on_table"], ["bottle_grasped"], 1.5, ["bottle"], ["right"]),
            _node("v4", "place", "snack", ["box_open", "snack_grasped"], ["snack_in_box"], 2.0, ["snack", "box"], ["left"]),
            _node("v5", "place", "bottle", ["box_open", "bottle_grasped"], ["bottle_in_box"], 2.2, ["bottle", "box"], ["right"]),
            _node(
                "v6",
                "close",
                "box",
                ["snack_in_box", "bottle_in_box"],
                ["box_packed"],
                2.5,
                ["box"],
                ["both"],
                mode="cooperative",
            ),
        ],
        rng,
        jitter,
    )
    graph = _graph(
        nodes,
        [
            AtomicTaskEdge("v4", "v5", "resource_mutex", resource="box", reason="only one item can be inserted into the box opening at a time"),
            AtomicTaskEdge(
                "v4",
                "v6",
                "synchronization",
                state="snack_in_box",
                reason="box closing requires the snack placement to finish",
            ),
            AtomicTaskEdge(
                "v5",
                "v6",
                "synchronization",
                state="bottle_in_box",
                reason="box closing requires the bottle placement to finish",
            ),
        ],
    )
    return TaskRecord(
        task_id=f"pack_box_{index:03d}",
        domain="packing",
        instruction="Open the box, pick up the snack and bottle in parallel, place both items inside, and close the box with both arms.",
        initial_state={"states": ["box_closed", "snack_on_table", "bottle_on_table"]},
        goal_state={"states": ["box_packed"]},
        scene=_scene(["box", "snack", "bottle"]),
        gold_graph=graph,
    )


def _assemble_bracket(index: int, rng: random.Random, jitter: float) -> TaskRecord:
    nodes = _with_jitter(
        [
            _node("v1", "place", "base_plate", ["base_plate_on_table"], ["base_plate_positioned"], 2.0, ["base_plate"], ["left", "right"]),
            _node("v2", "grasp", "bracket", ["bracket_on_table"], ["bracket_grasped"], 1.8, ["bracket"], ["right"]),
            _node("v3", "pick", "screwdriver", ["screwdriver_available"], ["screwdriver_grasped"], 1.4, ["screwdriver"], ["left"]),
            _node(
                "v4",
                "align",
                "bracket",
                ["base_plate_positioned", "bracket_grasped"],
                ["bracket_aligned"],
                4.5,
                ["base_plate", "bracket"],
                ["both"],
                mode="cooperative",
            ),
            _node("v5", "fasten", "screw", ["bracket_aligned", "screwdriver_grasped"], ["screw_fastened"], 5.0, ["screwdriver", "screw", "bracket"], ["left", "right"]),
            _node("v6", "inspect", "assembly", ["screw_fastened"], ["assembly_ready"], 2.0, ["assembly"], ["left", "right"]),
        ],
        rng,
        jitter,
    )
    graph = _graph(
        nodes,
        [
            AtomicTaskEdge(
                "v1",
                "v4",
                "synchronization",
                state="base_plate_positioned",
                reason="alignment requires the positioned base plate",
            ),
            AtomicTaskEdge(
                "v2",
                "v4",
                "synchronization",
                state="bracket_grasped",
                reason="alignment requires the grasped bracket",
            ),
        ],
    )
    return TaskRecord(
        task_id=f"assemble_bracket_{index:03d}",
        domain="assembly",
        instruction="Position the base plate, pick the bracket and screwdriver, align the bracket with both arms, fasten the screw, and inspect the assembly.",
        initial_state={"states": ["base_plate_on_table", "bracket_on_table", "screwdriver_available"]},
        goal_state={"states": ["assembly_ready"]},
        scene=_scene(["base_plate", "bracket", "screwdriver", "screw", "assembly"]),
        gold_graph=graph,
    )


def _sort_tray(index: int, rng: random.Random, jitter: float) -> TaskRecord:
    nodes = _with_jitter(
        [
            _node("v1", "stabilize", "tray", ["tray_on_table"], ["tray_stable"], 2.0, ["tray"], ["left"]),
            _node("v2", "move", "red_block", ["red_block_on_tray", "tray_stable"], ["red_block_in_left_bin"], 2.3, ["red_block", "tray"], ["right"]),
            _node("v3", "move", "blue_block", ["blue_block_on_tray", "tray_stable"], ["blue_block_in_right_bin"], 2.3, ["blue_block", "tray"], ["right"]),
            _node("v4", "grasp", "lid", ["lid_on_table"], ["lid_grasped"], 1.8, ["lid"], ["right"]),
            _node(
                "v5",
                "cover",
                "tray",
                ["red_block_in_left_bin", "blue_block_in_right_bin", "lid_grasped", "tray_stable"],
                ["tray_covered"],
                3.2,
                ["tray", "lid"],
                ["both"],
                mode="cooperative",
            ),
        ],
        rng,
        jitter,
    )
    graph = _graph(
        nodes,
        [
            AtomicTaskEdge("v2", "v3", "resource_mutex", resource="tray", reason="block moves share tray support"),
            AtomicTaskEdge(
                "v1",
                "v5",
                "synchronization",
                state="tray_stable",
                reason="tray must remain stable for cover placement",
            ),
            AtomicTaskEdge(
                "v2",
                "v5",
                "synchronization",
                state="red_block_in_left_bin",
                reason="cover placement waits for red-block sorting",
            ),
            AtomicTaskEdge(
                "v3",
                "v5",
                "synchronization",
                state="blue_block_in_right_bin",
                reason="cover placement waits for blue-block sorting",
            ),
            AtomicTaskEdge(
                "v4",
                "v5",
                "synchronization",
                state="lid_grasped",
                reason="cover placement requires the grasped lid",
            ),
        ],
    )
    return TaskRecord(
        task_id=f"sort_tray_{index:03d}",
        domain="sorting",
        instruction="Stabilize the tray, sort the red and blue blocks into bins, grasp the lid, and cover the tray using both arms.",
        initial_state={"states": ["tray_on_table", "red_block_on_tray", "blue_block_on_tray", "lid_on_table"]},
        goal_state={"states": ["tray_covered"]},
        scene=_scene(["tray", "red_block", "blue_block", "lid"]),
        gold_graph=graph,
    )


TEMPLATES: list[Callable[[int, random.Random, float], TaskRecord]] = [
    _pour_drink,
    _pack_box,
    _assemble_bracket,
    _sort_tray,
]


def validate_task(record: TaskRecord) -> list[str]:
    graph = record.gold_graph
    audit = joint_graph_audit(
        graph,
        set(record.initial_state.get("states", [])),
        set(record.goal_state.get("states", [])),
    )
    return audit.failure_reasons()


def generate_dataset(count: int, seed: int, duration_jitter: float = 0.2) -> list[TaskRecord]:
    rng = random.Random(seed)
    records: list[TaskRecord] = []
    index = 1
    while len(records) < count:
        template = TEMPLATES[(index - 1) % len(TEMPLATES)]
        record = template(index, rng, duration_jitter)
        errors = validate_task(record)
        if errors:
            raise ValueError(f"{record.task_id} is invalid: {errors}")
        records.append(record)
        index += 1
    return records


def write_jsonl(records: list[TaskRecord], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")


def read_jsonl(path: Path) -> list[TaskRecord]:
    with path.open("r", encoding="utf-8") as handle:
        return [TaskRecord.from_dict(json.loads(line)) for line in handle if line.strip()]
