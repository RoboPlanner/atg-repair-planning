# English reading copies

These are **labelled English translations of existing frozen materials**, prepared on 1 October 2026. They are not new candidates, new experimental records, independently generated references or a rerun of any evaluation.

[Project guide](https://roboplanner.github.io/atg-repair-planning/guide.html) · [English data navigator](https://roboplanner.github.io/atg-repair-planning/translations.html) · [Download English copies](https://roboplanner.github.io/atg-repair-planning/assets/downloads/ATG_English_reading_copies_v1.zip)

## Start here

- [24 task specifications](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/task_specs.json)
- [All 24 plans and schedules](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/reports_v1/task_plans_24.md)
- [Statistical report](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/reports_v1/statistical_report_24_tasks.md) and [domain statistics](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/reports_v1/domain_statistics.csv)
- [Generation protocol](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/generation_protocol.md)
- [Per-task records](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/results_v1/cases/) and [per-task metrics](reproduction/analysis_outputs/gpt6_current_session_planning_20260917_v1/results_v1/per_task_metrics.csv)
- [Derived inputs](reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/inputs/) and [historical expansion report](reproduction/analysis_outputs/experiment_expansion_v7_63_20260917/experiment_expansion_report.md)
- [Shared-compression protocol](reproduction/experiment_protocol.md) and [public-specification protocol](reproduction/external_discrete_protocol.md)
- [Same-input comparison records](reproduction/inputs/frozen_comparison_inputs.jsonl)
- [Simulation aggregate](simulation_expanded/aggregate_results.json) and [nominal-window CSV](simulation_expanded/figures/figure10_nominal_windows.csv)
- [Upstream tool-request reading copy](reproduction/external/GNN4TaskPlan/data/huggingface/data.json)

## What changed

The 44 files comprise 38 dataset copies and six reading documents. Across the datasets, 1,810 descriptive string occurrences were translated, including task titles, natural-language instructions and CSV labels. Node identifiers, action/state/resource symbols, relation endpoints, record ordering, duration values, schedule intervals, numerical statistics, booleans and nulls are unchanged. The complete plan listing retains every node and schedule table row; report tables retain their numeric cells.

JSON keys are unchanged. Legacy keys such as `title_zh` therefore contain an English rendering in this reading layer; the field name alone does not indicate the language of a translated value. The `.json` file in the upstream tool dataset retains its original JSONL record format and ordering.

Two upstream GNN4TaskPlan records contain Chinese text, including a request to translate a quoted phrase. Their English renderings are for reader comprehension only. Feeding the translated text back into the benchmark would change the request; **do not use these reading copies as replacement experimental inputs**. Upstream source attribution and licenses remain in [the original source tree](https://github.com/RoboPlanner/atg-repair-planning/tree/main/reproduction/external/GNN4TaskPlan).

## Originals and provenance

Canonical reproduction uses the unchanged `reproduction/`, `simulation/` and `simulation_expanded/` trees and original ZIPs. Their original-language specifications, historical reports, report-generation code, source filenames and manifests are retained. This partial English mirror supplies readable copies, not a standalone executable replacement. Already-English code, candidate nodes and result files need no duplicate here. Frozen historical notes are not the current release guide; use the project guide and current code/evidence map for manuscript numbering and publication status.

[TRANSLATION_MANIFEST.json](TRANSLATION_MANIFEST.json) records every original path, its SHA-256, the translated path and its SHA-256. Original paths are percent-encoded UTF-8 URIs relative to the repository root; decode once. Each dataset substitution records its field path, a hash of the source string and the English rendering. Source manifests still validate original bytes and are not repurposed to validate translations.

From the cloned repository root, run:

```sh
python tools/verify_archive.py
python tools/verify_translations.py
python tools/check_public_language.py
```

The translation check compares every dataset field, verifies original and translated hashes, checks preserved plan rows and numeric report tables, and checks the English ZIP byte-for-byte. It verifies preservation and recorded substitutions; it is not an independent linguistic or process-semantic gold standard.
