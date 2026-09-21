# Verifiable Atomic Task Graph Repair and Dual-Unit Planning

Reproduction materials for the manuscript **Verifiable Atomic Task Graph Relation Repair and Planning-Layer Parallel Planning for Dual Execution Units** (Chinese manuscript revision v7_70).

This repository studies a planning-layer interface: typed candidate task graphs are processed by deterministic relation repair, joint auditing, and strict list scheduling. `L` and `R` are two abstract execution units. `B` occupies both units simultaneously. This is not a trajectory-planning or robot-hardware package.

## Reproduce the archived evaluations

Use Python 3.11 or newer. The current three evaluation suites use the Python standard library only; no model API or robot connection is required.

```sh
cd reproduction
python reproduce_all.py results/new_run
```

The output directory must not already exist. Stable evaluation results are compared with their archived counterparts. Timings and freeze timestamps are not expected to be identical. Historical MILP and timing experiments have separate dependencies and instructions in [the package README](reproduction/README.md).

To run the current implementation and public-source checker tests:

```sh
cd reproduction/implementation_v7_70
python -m unittest discover -s tests -v
cd ..
python -m unittest test_external_reference -v
```

From the repository root, the commands above run 58 implementation tests and 8 public-source checker tests.

## Evidence and limits

- Four-setting comparisons include 1,024 internal and 3,944 public archived-tool evaluation records. Setting records are not independent task counts.
- Public planning specifications comprise 6 fully adaptable AssemblyGrid recipes, one official OR specification test, and 6 two-unit projections of OR-Library job-shop instances (13 inputs, 52 setting records). All 41 accepted outputs passed source-level constraint checks.
- A constructed three-node family contains 1,728 inputs and five diagnostic settings. The full method accepts 720 of the 736 independently feasible inputs; repair is not complete.
- On 160 controlled inputs, simple field matching with the same order-compression component slightly outperforms the full method. Public archived-tool edge agreement can deteriorate even when formal acceptance increases. These negative results are retained.
- On the six two-unit job-shop projections, the full method has shorter makespans than the shared-compression simple comparator, with a mean paired reduction of 25.7167%. These finite instances do not establish general superiority or statistical significance.
- The 24 original GPT-6 conversation candidates are method-aware, single-session artifacts. They are not an independently verifiable provider API benchmark. Public-specification candidates are deterministic adaptations, not additional naturally generated model failures.
- Guarantees concern represented discrete states, capacity-one resources, and unit occupancy. They do not cover omitted semantics, continuous collisions, trajectories, or hardware execution.

See [the frozen public-source protocol](reproduction/external_discrete_protocol.md), [the Chinese package README](reproduction/README.md), and the archived per-record results for details.

## Archive integrity and provenance

The release asset `ATG_reproduction_v7_70.zip` is the fixed supplementary archive. Its SHA-256 is:

```text
922881a57e08e3cc1a0f28e283e2837dabfb486d1c612fc282feb4575a8f0f4a
```

Files under `reproduction/` retain the original archive bytes; [MANIFEST_SHA256.json](reproduction/MANIFEST_SHA256.json) lists their hashes. Third-party source versions, licenses, and attribution are retained in `reproduction/sources/` and `reproduction/external/`. The manuscript and the author's EndNote library are not distributed here.

No additional blanket license is applied to third-party materials. Consult their preserved licenses before reuse.
