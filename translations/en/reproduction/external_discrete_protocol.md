# Public discrete-reference evaluation protocol

English reading translation of the frozen protocol. The original protocol and experimental inputs remain in the immutable planning archive. This translation does not change source selection, inputs, evaluation settings or recorded results.

## Sources and selection

1. AssemblyGrid_v1 is pinned to commit `ce61f635e47d312d633eda022b5f08bc4dbe888f`. All ten original recipe JSON files are inspected individually. A recipe is directly adaptable only when every operation requires at most two collaborating units and no unresolved exclusive route remains. Required cardinalities are not reduced, and unsupported operations are not removed to manufacture a feasible graph. All exclusions and reasons are retained. Each recipe contributes one single-product record; seeds and product repetitions are not added.
2. The same commit's public `test_alternative_routes.py::_branch_recipe(False)` supplies a separate inclusive-OR, multiple-producer specification case. It is an explicitly identified extension test in the source benchmark and is counted separately from the official recipes. The exclusive-XOR counterpart remains an unsupported-case test; it is not relaxed into inclusive OR.
3. Instances `ft06`, `la01`, `la02`, `la03`, `la04` and `la05` are fixed in advance from OR-Library's `jobshop1.txt`. Original operation sequences, machine identifiers and durations are retained; cases are not selected by outcomes. The projection adds two abstract general-purpose execution units. Every operation is single-unit with `Cand={L,R}`, and each original machine is a capacity-one resource. This is a two-unit-constrained discrete projection, not a replication of the original JSP optimum or a comparison with its leaderboard.

## Candidates and comparisons

No model is called, and candidates are not presented as naturally generated model errors. Recipe candidates create completion-fact state edges only from explicit `predecessors` in the original files. Material input and output fields are mapped without alteration. Material dependencies, synchronization and resource ordering are left to post-processing. Job-shop candidates preserve all original job chains while leaving machine ordering unresolved. The evaluation tests repair obligations induced by public specifications; it does not randomly delete edges from a reference answer.

All four settings receive exactly the same candidate and explicit initial/goal states: audit only, one-pass field matching, one-pass field matching with shared compression, and the full method. Goals come from public recipe `final_token` fields or the last operations of public jobs, rather than being inferred from candidate outputs. Every successful and failed result is retained. No compression benefit is claimed when `E_order` is absent.

## Independent checks

A separate checker reads the frozen source recipes or job matrices and the schedule directly. It neither defines ground truth from the ATG's Pre/Post/Res fields nor calls the verifier under evaluation. It checks operation coverage, original durations, material consumption and production, explicit precedence, OR/XOR conditions, recipe collaboration cardinalities, original resource exclusion, actual L/R occupancy and externally specified goals. Finish events are processed before start events at the same timestamp.

The projection does not cover original AssemblyGrid spatial reachability, tools or skills, holding configurations, transport, faults, or full-simulation success. Both units are assumed to have the necessary skills, and raw materials are assumed ready. Role skills and geometry are not represented as verified properties. Independent material consumption is checked along a single-product operation sequence; this does not extend the paper's no-delete state model into a general consumptive planner.

## Reporting

Adaptation coverage, formal acceptance, independent discrete-semantic checks and symbolic makespan are reported separately for public recipes, the public OR specification test and job-shop projections. They are not pooled into one robot success rate. When no unique gold resource orientation exists, legal alternative orientations are not penalized solely for differing edge sets. Per-instance differences between simple matching with shared compression and the full method are reported without significance claims.

A separate, exhaustively enumerated small mechanism family and independent enumeration of feasible orders examine the multiple-producer strategy. These author-constructed mechanism cases are reported separately from external semantic evidence and are not described as independent industrial tasks.
