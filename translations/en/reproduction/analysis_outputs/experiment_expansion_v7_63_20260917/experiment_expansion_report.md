# Experimental expansion and measured statistical report

**English reading translation of the frozen v7.63 report. Historical section numbers and results are retained. This is not a new experiment or the current manuscript guide.**

This report accompanied Sections 4.5–4.7 and Appendix A.4 of the Chinese v7.63 manuscript. Starting from 24 frozen GPT-6 Astra conversation-generated plans, the study ran paired relation-input views, component disabling, relation deletion, duration perturbations, branching/resource stress configurations and same-graph MILP. The original 160 controlled records and main tables were retained.

## Samples and evidence sources

| Input or evaluation | Count | Supported interpretation |
| --- | ---: | --- |
| Original GPT-6 plans | 24 tasks, 254 nodes | Candidate-interface behavior in this method-aware conversation |
| Four relation-information views | 24×4=96 inputs, six settings each, 576 evaluations | Component obligations on shared nodes and input relations |
| Relation-deletion variants | 24×3 rates×3 seeds=216 inputs | Relation recoverability given correct node fields |
| Duration variants | 24+24×2 magnitudes×3 seeds=168 inputs | Acceptance and efficiency under the tested positive durations |
| Programmatically constructed branching graphs | 24 configurations, 6–36 nodes | Runtime under branching, resource bottlenecks and join occupancy |
| Same-graph MILP | 24 solves | Scheduling gaps on fixed accepted graphs |

The counts 96, 216, 168 and 24 must not be added and described as new model-generated tasks. Information views, seeded variants and repeated timings share base content. No significance inference was made. Specifications and candidates came from the same model conversation, without an independent human gold standard; model-batch edge F1, parallel F1 and process-semantic accuracy are not computed.

## Original plans and paired inputs

Original candidates and full-method outputs both achieved 24/24 strict acceptance with zero net edge changes. The 82 log operations delete and rebuild the same 41 synchronization edges. Mean speedup 1.2411 and mean symbolic makespan reduction 18.49% describe parallel scheduling gains.

| Setting | All relations | Nodes only | State only | Linear order only |
| --- | ---: | ---: | ---: | ---: |
| Full method | 24/24 | 24/24 | 24/24 | 24/24 |
| State stage disabled | 24/24 | 0/24 | 24/24 | 0/24 |
| Synchronization disabled | 24/24 | 7/24 | 7/24 | 7/24 |
| Resource stage disabled | 24/24 | 2/24 | 2/24 | 24/24 |
| Compression disabled | 24/24 | 24/24 | 24/24 | 24/24 |
| Unit assignment disabled | 0/24 | 0/24 | 0/24 | 0/24 |

The historical report described disabled unit assignment as a configuration rejected by the formal acceptance interface and stressed that this row did not represent an accepted schedule with relaxed occupancy. **Reading note:** later manuscript corrections explain rejection of this batch by actual occupancy failing Cand/mode; disabled assignment alone is not a universal rejection condition. This note does not change the archived 0/24 counts. The remaining settings use the same formal checks on obligations left after disabling a component. On nodes-only inputs, the full method adds 266 state, 41 synchronization and 73 resource edges, 380 in total. Added edges are not scored against the method's own outputs as accuracy.

On linear-order inputs, the full method deletes 175 conservative order edges. Across 24 jointly accepted tasks, speedup is 1.2388±0.1438 with the full method and 1.0000±0.0000 with compression disabled.

## Perturbation and structure tests

| Nominal deletion rate | Variants | Joint passes before repair | Strict passes after repair | Replay passes |
| --- | ---: | ---: | ---: | ---: |
| 10% | 72 | 0 | 72 | 72 |
| 30% | 72 | 0 | 72 | 72 |
| 50% | 72 | 0 | 72 | 72 |

Each rate uses fixed seeds 11, 29 and 47. Actual deleted counts, fractions and complete edge lists remain in the input JSONL. These are constructed deletions, not natural model error rates.

| Duration magnitude | Records | Strict passes | Estimated makespan | Speedup |
| --- | ---: | ---: | --- | --- |
| ±0% | 24 | 24 | 17.2500±4.9978 | 1.2411±0.1402 |
| ±20% | 72 | 72 | 17.1207±4.9007 | 1.2398±0.1318 |
| ±50% | 72 | 72 | 17.4386±5.4083 | 1.2238±0.1240 |

| Nodes | Configurations | Passes before repair | Passes after repair | Post-processing ms |
| --- | ---: | ---: | ---: | --- |
| 6 | 4 | 2 | 4 | 2.5069±0.8473 |
| 10 | 4 | 2 | 4 | 10.4152±6.0375 |
| 12 | 4 | 2 | 4 | 8.0131±1.5149 |
| 18 | 4 | 2 | 4 | 60.4006±50.2747 |
| 20 | 4 | 2 | 4 | 41.5853±23.1331 |
| 36 | 4 | 2 | 4 | 311.1461±224.2847 |

Timing begins with an already loaded graph and includes repair, auditing and strict scheduling; model generation, file I/O and MILP are excluded. Each graph receives three warm-ups and ten repetitions, whose median is retained. Means and sample standard deviations in the table describe four configurations at the same node count. Both single and cooperative joins act as layer barriers here, producing equal makespans; this does not establish a general effect of cooperative-node proportion.

## Same-graph MILP

All 24 MILP solves returned optimal status and passed independent schedule checks. Mean list-schedule makespan is 17.2500 versus 16.1250 for MILP. Mean per-task relative gap is 6.95%, with standard deviation 8.59%; 10/24 list schedules attain the same-graph optimum. The largest gap is W04: 19 versus 14, or 35.71%.

Both methods fix the same accepted graph, node fields, candidate units, capacity-one resources and all typed precedence relations. MILP does not revise graph repair. The solver is SciPy 1.15.3/HiGHS, with a 10 s per-case limit and mip_rel_gap=0. Raw floating-point solutions are retained. Earliest feasible times are reconstructed from integer unit and ordering choices to remove tiny floating-point overlaps, followed by schedule verification. Same-graph optimality is assigned only when feasible upper and solver lower bounds agree within relative tolerance 1e-6.

## Verification and code scope

- All 984 pipeline evaluations completed: 745 strict acceptances and 239 rejections, with no accepted schedules exported for rejected records.
- Replay matched for 984/984 evaluations; independent accepted-output checks passed for 745/745.
- All 54 regression tests passed; MILP optima were cross-checked against exhaustive search on 13 small instances.
- Rerunning the fixed 160 historical inputs left the values in eight Table 1–4 summary/detail CSVs unchanged.
- Versioned code improves exported time precision and rejects inapplicable relation labels before repair; original project source remains preserved.
- Candidates, inputs, raw outputs, environment, seeds and hashes are retained. Algorithm runtimes are local measurements; other task durations are symbolic inputs.

## Evidence still absent at the time of this report

The report supports controlled reference agreement, the conversation candidate interface, relation repair under represented fields and same-graph scheduling evaluation. Independent process gold standards, external task distributions, independent-session or cross-model replication and hardware results were not established in this batch. Additional answers generated and labelled by the same model cannot replace those sources. The I02 distinction between a recorded test and a passing test was documented while preserving the original plan.

## File entries

Paths below refer to the original frozen expansion directory, not this partial reading mirror.

- `results/summary.json`, `*_metrics.csv`: summaries and per-record numbers.
- `results/*_details.jsonl`: input/output graphs, logs, acceptance/rejection, exported plans and independent checks; MILP records also contain raw solutions and bounds.
- `inputs/*.jsonl`, `experiment_protocol_frozen.json`: frozen inputs and hashes.
- `implementation_v7_63/`: the implementation used and its 45 existing tests.
- `milp_baseline.py`, `test_new_contract_and_milp.py`: MILP and nine added tests.
- `historical_replay/comparison.json`: numerical agreement with earlier main tables.
