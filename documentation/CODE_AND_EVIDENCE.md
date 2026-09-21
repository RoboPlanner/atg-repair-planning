# Code and evidence map

All paths below are relative to this repository. The immutable `reproduction/` tree is the v7.70 snapshot. The manuscript is not bundled; numbers below refer to that snapshot.

## Current implementation

| Responsibility | File under `reproduction/implementation_v7_70/atomic_task/` |
| --- | --- |
| Formal fail-closed interface | `pipeline.py`: `run_verified_atg` |
| Node/edge types and raw type checks | `schema.py` |
| Four ordered repair stages and edit log | `optimization.py` |
| Joint graph verification | `verification.py` |
| Strict list scheduling and actual occupancy checks | `planning.py` |
| Metrics and experimental utilities | `metrics.py`, `experiments.py` |
| Regression tests | `../tests/` |

The formal interface requires explicit `initial_states` and `goal_states`. Missing values are not inferred. Python callers supply sets; `tools/run_plan.py` accepts JSON arrays and validates their raw element types before constructing sets. The returned `accepted` flag, not the presence of an intermediate graph, determines acceptance.

Paper-to-JSON field mapping (exactly nine semantic fields): `id→id`, `action→action`, `object→object`, `Pre→pre_state`, `Post→post_state`, `d→duration`, `Res→resource`, `Cand→candidate_arm`, `mode→mode`. Serialized execution-unit names are `left`, `right`, `both`, corresponding to L, R, B. Internal classes also contain convenience metadata (`workspace`, `target`, `metadata`); these are not additional semantic fields in the paper's node definition. The example supplies only the nine semantic fields.

Edges use `state_support`, `resource_mutex`, `synchronization`, and `order`, corresponding to E_state, E_mutex, E_sync, and E_order. Existing state support and synchronization match the exact source/target/state triple. `both` is a joint occupancy mode, not a third machine.

Durations must be finite and positive. Float schedules must retain strictly positive representable intervals and pass duration/precedence/occupancy checks. Rescale symbolic durations if the accumulated horizon makes small intervals unrepresentable; rejection at extreme floating-point scales is intentional.

## Experiment entry points

| Manuscript evidence | Inputs / outputs | Entry point |
| --- | --- | --- |
| Tables 1–7, controlled study and Figures 5–6 | `reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/` | Historical evidence retained; current shared-input reevaluation below |
| Original 24 conversation plans | `reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/` | Frozen first-round artifacts; no API regeneration claimed |
| Tables 8–12, Figures 7–8, MILP and timing | `reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/` | `rerun_in_new_directory.py --name reproduction_run01` from that directory |
| Tables 13–14, same-input repair comparisons | `reproduction/inputs/`, `reproduction/external/`; outputs `results/fair_comparison/` | `reproduction/reproduce.py`; `repair_comparators.py`; `external_adapter.py` |
| Tables 15–16, public planning specifications | `reproduction/sources/`; outputs `results/external_discrete_run01/` | `reproduction/external_discrete.py`; frozen `external_discrete_protocol.md` |
| Finite three-node mechanism family | `reproduction/results/exhaustive_run01/` | `reproduction/exhaustive_mechanism.py` |
| Independent interval/resource and public source checks | Inputs and accepted outputs from the above | `reproduction/independent_audit.py`, `test_external_reference.py` |

Run all three current suites with `reproduction/reproduce_all.py`, following the root README. Do not interpret summary rows as independent replications when they reuse a task across settings. The public tool source is archived GNN4TaskPlan data; only representable records are adapted. Excluded cases and input hashes are retained.

## Manuscript figures used on the website

Figures 1–4 were rasterized from the exact current manuscript EMF parts. Figures 5–8 were copied byte-for-byte from the embedded PNG parts. The main page displays Figures 1–5; the remaining exported figures are retained as assets. `asset_provenance.json` records source hashes and conversion type. These exports do not modify the manuscript or its editable figure originals.

## Output interpretation

`accepted=false` means diagnostics and no accepted schedule. A failed repair is not a proof that no feasible plan exists. Stored schedule durations are symbolic except the explicitly labelled measured runtime experiments. No package command calls a model API or controls hardware.
