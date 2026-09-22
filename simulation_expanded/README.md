# Eight-template planning and dual-Panda simulation study

This is an actual MuJoCo 3.3.3 execution study with constructed task specifications and fixed skills. It is **not hardware evidence**, a natural LLM-error benchmark, or an independent industrial semantic reference. All frozen outcomes are retained.

## Results

- 8 templates, 5 initial-position seeds, nominal full/serial schedules: **80 runs, 80 completed**.
- 4 one-factor stress conditions under full scheduling: **160 runs, 104 completed, 56 failed**.
- Full scheduling completes 40/40 nominal, 30/40 mass ×5, 0/40 low friction, 35/40 pose bias, and 39/40 half-window runs.
- Independent state reconstruction agrees with all 240 online verdicts. This is an implementation-level cross-check, not third-party certification.
- 32 constructed graph inputs ×3 methods =96 planning settings. Audit only accepts 8/32; field matching with shared compression and the full method each accept 24/32. Their accepted schedule windows are identical in all 24 pairs. All 56 accepted settings pass independent graph/schedule checks.
- No inference of statistical significance, heuristic superiority, hardware speedup, or general physical robustness is made.

| Code | Task | Nodes | Cooperative nodes | Serial/full window (s) |
|---|---|---:|---:|---:|
| T01 | Parallel sorting | 4 | 0 | 24 / 12 |
| T02 | Shared inspection | 6 | 0 | 40 / 28 |
| T03 | Synchronized kitting | 4 | 0 | 24 / 12 |
| T04 | Two-stage shared service | 8 | 0 | 56 / 44 |
| T05 | Cooperative transfer | 5 | 1 | 22 / 17 |
| T06 | Two-leg cooperative transfer | 6 | 2 | 34 / 29 |
| T07 | Tray loading and transfer | 9 | 1 | 46 / 29 |
| T08 | Transfer and unloading | 9 | 1 | 46 / 29 |

T03 adds a two-object state barrier to T01; equal pick durations yield the same nominal schedule. The templates reuse object geometry and supplied skills. Shared service is geometric dwell, not a modeled inspection sensor. B occupies both L and R.

## Reproduce

Use the repository root, with sibling `simulation/`, `simulation_expanded/` and `reproduction/`. The downloadable code/data ZIP preserves this layout. Python 3.11 is recommended. A local OpenGL-capable environment is needed for video rendering; FFmpeg must be on PATH. No API key or robot connection is used.

```sh
python -m pip install -r simulation_expanded/requirements.txt
python simulation_expanded/run_expanded.py --output results/new_physics --workers 4 --videos
python simulation_expanded/verify_expanded.py results/new_physics
python simulation_expanded/planning_study.py --output results/new_planning
python simulation_expanded/test_verifier.py simulation_expanded/pilot_02
```

Always use new output directories. `verify_expanded.py` intentionally refuses to overwrite an existing verification report. To recheck archived trajectories directly without changing them, use `recheck_archive.py` below. Regression reports are saved under the given development directory; a repeated regression check recomputes that development-only report.

```sh
python simulation_expanded/recheck_archive.py
python simulation_expanded/check_manifest.py
```

`analyze_and_plot.py` rebuilds aggregate data and Figures 9–11 from archived evaluation directories. It requires Times New Roman installed locally; the font is not distributed. Figures use English text, editable SVG/PDF and 600-dpi PNG/TIFF, no error bars, with panel labels centered below. Videos must be present to extract the figure plate. The separate videos ZIP restores them at their original trial paths. Source CSVs include all successes, all failures and explicit zero counts.

## Protocol and evidence boundaries

Formal seeds are 100–104. Initial object XY positions vary by ±10 mm. Nominal sliding friction is 1.5; the stress value is 0.15. Other one-factor stresses are object mass ×5, initial grasp-position estimate bias up to ±20 mm per XY coordinate, and all skill windows ×0.5. No controller tuning occurred after the frozen formal run. Goal locations remain supplied by the specification, so the bias condition does not benchmark visual perception. Stress conditions have no serial counterpart and cannot isolate a causal effect of concurrency on physical failure.

The controller uses inverse kinematics, fixed Cartesian waypoints, position actuators, gravity compensation and frictional contact. No weld, object attachment, or post-initialization object teleportation is used. Skill windows are supplied durations, not learned or measured hardware execution time. Exact action-event snapshots supplement 40-ms saved samples. Physics contact/collision counters run every 2 ms; offline sampled checks do not certify unsampled continuous collision freedom.

Every primitive has an explicit predicate, including retreat. The offline checker reconstructs predicates from qpos/qvel/ctrl rather than trusting event success flags. Nine regression cases include fake success, failed lift, off-target placement, missing service dwell, incorrect B occupancy and unsupported primitives. All nine passed before the formal evaluation. Both fingers on each arm must contact the tray for more than 90% of the designated carry interval.

Failure categories count the **first failed check per run**: 25 pick, 25 cooperative-transfer, 5 placement and 1 final-state failures. Secondary predicate failures remain in the records. These categories are observations, not exhaustive causal diagnoses.

## Files and provenance

- `evaluation_frozen_v1/`: 240 complete trials, frozen protocol, source snapshots and independent reconstruction results.
- `planning_frozen_v2/`: 32 inputs frozen before evaluation, 96 records and independent graph/schedule checks. The prior construction attempt stopped before evaluation because optional edge fields were encoded as null; it is not part of these results.
- `pilot_02/`: development seed −11, 16 nominal runs and nine checker regressions. Excluded from all formal counts. The earlier multiprocessing permission failure is retained in project work records.
- `aggregate_results.json`, `figures/*.csv`: exact tabulation and chart sources.
- `MANIFEST_SHA256.json`: all distribution files except the manifest itself.
- Videos: S4–S11 are T01–T08, seed100, full and serial. S12 contains T08 seed100 under all four stress conditions, including the heavy/low-friction failures. Selection was fixed before evaluation, not based on success.

The original 30-run simulation and frozen v7.70 planning package remain unchanged. This expanded batch supersedes the exploratory simulation numbers in the current manuscript; it is not pooled with them. The independent audit shares the same physical model and data and is not external semantic annotation.

Original study code uses the repository MIT license. Robot assets retain the notices in `simulation/assets/`; inherited simulation code is byte-preserved. No Word draft, EndNote library, credentials or account email is included. Preparation is local only; no GitHub upload is performed.
