# Code and evidence map · manuscript v7.87

[Current project guide](https://roboplanner.github.io/atg-repair-planning/guide.html) · [Complete figure and table index](https://roboplanner.github.io/atg-repair-planning/evidence.html)

This index follows the current manuscript and supplement. The immutable planning tree remains v7.70 and the expanded simulation archive remains v2. Historical CSV filenames retain their original numbers; the mapping below supplies current paper numbers.

For translated task descriptions, complete plans and historical reports, use the [English reading copies](../translations/en/README.md). Source paths below identify canonical evidence; translations do not replace frozen reproduction inputs.

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


## Current table mapping

| Current table | Section | Content | Archived evidence |
| --- | --- | --- | --- |
| 1 | 4.2 | Atomic task graph quality | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table1_atomic_graph_quality.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table1_atomic_graph_quality.csv) |
| 2 | 4.3 | Dependencies, static parallel sets and acceptance | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table2_dependency_parallel_safety.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table2_dependency_parallel_safety.csv) |
| 3 | 4.3 | Planning efficiency and accepted schedules | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table3_plan_efficiency.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table3_plan_efficiency.csv) |
| 4 | 4.3 | Component ablation; graph and strict plan passes | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table4_ablation.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table4_ablation.csv) |
| 5(a–b) | 4.4 | Field sensitivity and reference agreement | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table7_robustness.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table7_robustness.csv) |
| 6 | 4.5 | 24 directly generated conversation candidates | [reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/results_v1/summary.json](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/results_v1/summary.json) |
| 7 | 4.7 | List scheduling versus same-graph MILP | [reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/milp_metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/milp_metrics.csv) |
| 8 | 4.8 | Same-input repair with shared compression | [reproduction/results/fair_comparison/comparison_metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/results/fair_comparison/comparison_metrics.csv) |
| 9 | 4.8 | Archived tool candidates and external agreement | [reproduction/results/fair_comparison/external_metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/results/fair_comparison/external_metrics.csv) |
| 10 | 4.9 | Public source specifications and acceptance | [reproduction/results/external_discrete_run01/summary.json](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/results/external_discrete_run01/summary.json) |
| 11 | 4.9 | Resource orientation on six job-shop projections | [reproduction/results/external_discrete_run01/metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/results/external_discrete_run01/metrics.csv) |
| 12 | 4.10 | Eight simulation templates and nominal windows | [English aggregate (original in archive)](https://github.com/RoboPlanner/atg-repair-planning/blob/main/translations/en/simulation_expanded/aggregate_results.json) |
| 13 | 4.10 | 96 same-input planning settings | [simulation_expanded/planning_frozen_v2/records.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/simulation_expanded/planning_frozen_v2/records.csv) |
| 14 | 4.10 | Planning acceptance and physical completion | [simulation_expanded/figures/simulation_condition_totals.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/simulation_expanded/figures/simulation_condition_totals.csv) |
| A1 | A.3 | Small-graph size and measured local runtime | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table6_complexity.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table6_complexity.csv) |
| A2 | A.3 | Detailed field-perturbation reference agreement | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table7_robustness.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table7_robustness.csv) |
| A3 | A.3 | Auxiliary audit and timeline metrics | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/](https://github.com/RoboPlanner/atg-repair-planning/tree/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/) |
| A4 | A.3 | Nonstrict diagnostic ablation speedup | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table4_ablation.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table4_ablation.csv) |
| B1 | B | Failure diagnostics and distinct counting units | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/analysis/failure_summary.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/analysis/failure_summary.csv) |
| C1 | C.1 | Nine single-fault regression classes | [reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table5_joint_audit_challenge.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/dual_arm_task_experiments/full_experiment_outputs_v7_40_internal_validity_20260907/tables/table5_joint_audit_challenge.csv) |
| C2 | C.2 | Acceptance contract and guarantee scope | [reproduction/implementation_v7_70/atomic_task/pipeline.py](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/implementation_v7_70/atomic_task/pipeline.py) |
| C3 | C.3 | Component comparison on 24 shared inputs | [reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/information_metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/information_metrics.csv) |
| C4(a–b) | C.4 | Controlled relation deletion and duration sensitivity | [reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/](https://github.com/RoboPlanner/atg-repair-planning/tree/main/reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/) |
| C5 | C.5 | Measured post-processing time by configuration | [reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/shape_metrics.csv](https://github.com/RoboPlanner/atg-repair-planning/blob/main/reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/results/shape_metrics.csv) |

Table 4 reports strict plan passes and accepted-subset speedups from the current reevaluation. Historical nonstrict diagnostic speedups belong to Supplement Table A4; they must not be substituted for accepted-plan metrics. Source directories may contain more diagnostics than the published tables.

## Reproduction entry points

- The three frozen planning evaluations: `cd reproduction`, then `python reproduce_all.py results/new_run`.
- Historical MILP and measured timing: install `reproduction/requirements-historical.txt`, then run `rerun_in_new_directory.py --name reproduction_run01` from `reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/`.
- Current simulation: `python simulation_expanded/run_expanded.py --output results/new_physics --workers 4 --videos` and `python simulation_expanded/verify_expanded.py results/new_physics`.
- Same-input simulation planning: `python simulation_expanded/planning_study.py --output results/new_planning`.
- Supplement C.6 discusses an archived resource-orientation counterexample; the finite mechanism family in main Section 4.9 is in `reproduction/results/exhaustive_run01/`, reproduced by `reproduction/exhaustive_mechanism.py`.

Use new output directories. Conversation artifacts are archived first-round outputs; these commands do not regenerate model API experiments. Timing environments retain their original scope.

## Figures and provenance

- Figure 1 · Section 3.1–3.3 · [Method overview](../docs/assets/images/figure1.png).
- Figure 2 · Section 3.1 · [Typed atomic task graph](../docs/assets/images/figure2.png).
- Figure 3 · Section 3.2 · [Relation repair and scheduling](../docs/assets/images/figure3.png).
- Figure 4 · Section 3.3 · [Audit, replay and output contract](../docs/assets/images/figure4.png).
- Figure 5 · Section 4.2 · [Controlled reference agreement and audit](../docs/assets/images/figure5.png).
- Figure 6 · Section 4.3 · [Planning efficiency and joint acceptance](../docs/assets/images/figure6.png).
- Figure 7 · Section 4.6 · [Measured post-processing runtime](../docs/assets/images/figure7.png).
- Figure 8 · Section 4.7 · [Paired efficiency and same-graph MILP gap](../docs/assets/images/figure8.png).
- Figure 9 · Section 4.10 · [Eight simulated task scenes](../docs/assets/images/figure9.png).
- Figure 10 · Section 4.10 · [Fixed-skill windows and same-input repair](../docs/assets/images/figure10.png).
- Figure 11 · Section 4.10 · [Stress completions and failures](../docs/assets/images/figure11.png).
- Figure A1 · Section A.3 · [Small-graph size trends](../docs/assets/images/figureA1.png).

Figures 1–4 share the current manuscript EMF sources, with separate PNG rendering. Figures 5–11 and A1 match the current submission PNG files byte-for-byte. `asset_provenance.json` and `current_manuscript_assets.json` record both provenance stages. All figures can be opened from the public evidence index.

`accepted=false` means diagnostics without an accepted schedule; rejection does not establish infeasibility. Only explicitly labelled runtime measurements are wall-clock times.
