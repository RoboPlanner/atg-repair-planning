# GPT-6 conversation planning and statistical analysis: first batch

**English reading translation of the frozen 2026-09-17 report. Historical version and conclusions are retained; this is not a new experiment or an updated manuscript summary.**

The batch contains 24 directly generated tasks and 254 nodes, evaluated by running the code. All 24 original candidates and all 24 post-processed outputs passed formal auditing and strict scheduling. Parallel scheduling improved on the fully serial baseline, but this batch showed no additional benefit from relation repair.

The task specifications and candidates were written by the same method-aware GPT-6 assistant in one conversation, with the user's authorization to use them as experimental inputs. Specifications were frozen at 09:41:14 UTC on 2026-09-17; all six candidate files were frozen at 09:59:55 UTC, before evaluation. Each task has one candidate. No random edge deletion, retrospective candidate edits or exclusions were used. Model identity comes from the conversation; independent provider request IDs and sampling parameters were not saved. This is not an independently verifiable API benchmark.

## Generated plans

There are four tasks in each of six domains. Node counts range from 7 to 16, with mean 10.5833 and sample standard deviation 2.4302. Of 254 nodes, 24 cooperative nodes occur in 17 tasks; seven tasks contain no cooperative node. The candidates contain 266 state edges, 41 synchronization edges and 54 resource-order edges; E_order is empty. Tasks cover bracket assembly, sealed enclosures, packing and kitting, electrical inspection, pallet securing, sorting, fixture replacement and tooling handover. Every original node has exactly nine fields.

| Domain | Tasks | Total nodes | Strict acceptance: before → after | Mean symbolic makespan | Mean serial-baseline speedup | Mean unit utilization |
|---|---:|---:|---|---:|---:|---:|
| Assembly | 4 | 38 | 4/4 → 4/4 | 17.25 | 1.2390 | 71.00% |
| Packing | 4 | 43 | 4/4 → 4/4 | 14.75 | 1.3034 | 77.64% |
| Inspection | 4 | 41 | 4/4 → 4/4 | 18.00 | 1.1063 | 64.77% |
| Warehousing | 4 | 44 | 4/4 → 4/4 | 16.75 | 1.2240 | 70.71% |
| Sorting | 4 | 43 | 4/4 → 4/4 | 13.25 | 1.3546 | 70.07% |
| Workstation preparation | 4 | 45 | 4/4 → 4/4 | 23.50 | 1.2193 | 69.58% |

## Auditing and replay

| Measure | Original candidates | Full post-processing |
|---|---:|---:|
| Nine-field format, types and resource declarations | 24/24 | Same nodes |
| schema_valid | 24/24 | 24/24 |
| closed | 24/24 | 24/24 |
| goal_reachable | 24/24 | 24/24 |
| acyclic | 24/24 | 24/24 |
| synchronization_complete | 24/24 | 24/24 |
| resource_ordered | 24/24 | 24/24 |
| Joint passage of all six checks | 24/24 | 24/24 |
| Acceptance with strict=True actually invoked | 24/24 | 24/24 |
| Independent check of exported intervals, preconditions, edge timing, resources and L/R occupancy | 24/24 | 24/24 |

Comparison by the complete edge key (source, target, type, state, resource) found zero net additions and zero net deletions. Node intervals and unit assignments in all 24 output schedules also matched strict scheduling of the original graphs. Replay agreed for 24/24 records. A separate script that does not import the original verifier independently replayed and checked graphs and timelines; all passed. All 24 B nodes occupied L+R, with no B–L/R overlap or capacity-one resource overlap detected.

The 82 accepted log events must be distinguished from net repairs. The synchronization stage deletes 41 existing synchronization edges and reconstructs the same 41 edges from valid state support. Thus, 82 is an operation count, not 82 errors or 82 net repaired relations. The state, resource and compression stages each accepted zero events; no events were rejected. The synchronization-set reconstruction produced real log operations but no net change to semantic relations in this batch.

## Scheduling statistics and definitions

Every d is a model-specified positive integer in symbolic time units, not device time or algorithm runtime in milliseconds. The serial baseline uses the same nodes, final unit assignments and a valid topological order, executing all nodes consecutively. All 24 serial plans were saved and independently checked. With Tserial=Σd and strict makespan T, speedup=Tserial/T and relative time reduction=1−T/Tserial. A B duration counts once in Tserial and twice in total L/R busy time. Utilization=(L busy time+R busy time)/(2T).

| Measure | Per-task mean ± sample standard deviation | Median | Range |
|---|---:|---:|---:|
| Fully serial time | 21.1250 ± 5.5271 | 21.5000 | 13.0000–35.0000 |
| Strict schedule makespan | 17.2500 ± 4.9978 | 17.5000 | 9.0000–30.0000 |
| Speedup over serial execution | 1.2411 ± 0.1402 | 1.1739 | 1.0556–1.5455 |
| Time reduction relative to serial execution | 18.4861 ± 8.7320% | 14.8148% | 5.2632–35.2941% |
| Two-unit utilization | 70.6264 ± 6.9887% | 70.8333% | 54.1667–81.5789% |

Mean per-task speedup is 1.2411, symbolic time reduction 18.4861% and two-unit utilization 70.6264%. These gains arise from parallel execution on the same relation graph and cannot be attributed to relation repair. Summed serial time is 507 and summed scheduled time is 414; their ratio, 1.2246, differs from the mean of per-task ratios, 1.2411. Time-pooled utilization is 70.4106%, also distinct from the per-task mean, 70.6264%. Means and sample standard deviations describe differences within this batch, not uncertainty from independent repeated model samples.

Both before and after repair, there are 225 statically parallelizable node pairs in total. The strict schedules contain 67 pairs with actual time overlap. These count potential pairs permitted by graph and candidate units versus pairs realized by this schedule. The ratio 67/225 is not recall. No independent reference planning graph exists for this batch, so edge F1, parallel F1, precision, recall and semantic accuracy are not reported.

The preplanned comparison of the full method against disabled order compression yielded identical relation sets and makespans on all 24 jointly accepted tasks. Original E_order sets are empty, so this batch does not exercise or establish a contribution from compression. Makespan improvement over strict scheduling of the original graphs is also zero.

## Two inspectable examples

**A01, bracket and base assembly:** locating the base [L,0–2] and preparing the bracket [R,0–2] proceed in parallel. Alignment [B,2–5] occupies both units. The first fastening [L,5–7], second fastening [R,7–9], inspection [L,9–11] and labelling [L,11–12] then proceed sequentially. Total d is 14, makespan is 12 and speedup is 1.1667. This example checks exclusive B occupancy and serial use of the shared torque tool.

**W02, replenishing two storage locations:** the two location checks can run in parallel. The scanner serves A before B. Placing A can legally overlap scanning B and placing B; the registration terminal is used serially. Total d is 17, makespan is 11 and speedup is 1.5455. This is the largest observed speedup in the batch, not evidence of optimality.

## Evidence and remaining limits

The batch supplies inspectable GPT-6 conversation-generated inputs showing that the nine-field interface, exact synchronization pairing, represented resource constraints and strict scheduling outputs operate together. Fixed code produces checkable results for the same inputs. Controlled repair experiments address a different question and remain separate. These records are not pooled with the earlier 160 records or treated as a fair cross-model comparison with historical outputs bearing other model names.

Formal acceptance does not establish real-world semantic correctness for all 24 plans. In I02, test nodes produce continuity_test_recorded and insulation_test_recorded; archiving is followed directly by movement to the accepted-items area, without representing passing-test conditions or lead disconnection. S02 assumes A is accepted and B requires rework in the task specification; it does not measure classification accuracy. T02 includes combined actions such as “label and stow”, whose granularity still needs independent process review. These original contents were preserved without retrospective correction. This qualitative inspection is not an independent gold standard.

The batch does not establish 100% general GPT-6 planning accuracy, increased repair success, superiority to other models, statistical significance, real-robot safety or hardware performance. The model knew the method and verifier, specifications and candidates came from the same conversation, and each task has only one candidate. Evidence about repair of failed inputs requires a separate, fixed protocol; deliberately damaging already accepted candidates must not be relabelled as naturally occurring LLM errors.

The original report proposed wording that describes a method-aware, single-conversation interface experiment with 24 plans, six domains and 254 nodes; all candidates pass formal auditing and strict scheduling before and after post-processing, with consistent replay and occupancy checks. Mean per-task symbolic makespan falls by 18.49% relative to the same-node serial baseline. Since relation sets have no net changes, the evidence supports interface acceptability and planning-level scheduling demonstrations, not repair gains or general semantic accuracy.

## Files and reproduction

Original paths below refer to the frozen batch directory, not to this partial English reading mirror.

- `raw_candidates_*.json`: six original candidate files; bytes match frozen hashes.
- `task_specs.json`, `common_prompt.txt`, `generation_protocol.md`: task inputs and protocol.
- `results_v1/cases/`: candidates, adapted inputs, audits, accepted/rejected logs, plans and G1–G4 replay graphs.
- `results_v1/per_task_metrics.csv`, `results_v1/edit_events.csv`: numeric records and edit events.
- [All 24 plans](task_plans_24.md) and [domain statistics](domain_statistics.csv): English reading copies.
- `reports_v1/independent_verification.json`, `reports_v1/verified_serial_baselines.jsonl`: independent checks and serial plans.
- Run `python -B evaluate_batch.py --output results_reproduction` from the original batch directory using a new output directory.
- `frozen_evaluator/` and the two freeze manifests retain the code, data and SHA-256 values.

The adapter only renames Pre/Post/d/Res/Cand and maps L/R/B labels. It does not infer or generate edges. The existing internal serialization field workspace=shared remains in code outputs and is not written back into the original nine-field nodes. The historical batch did not alter the manuscript, original code or earlier experiments.
