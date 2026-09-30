# Additional shared-compression comparison protocol: v7.69

English reading translation of the frozen protocol. Version labels and timing scope are historical.

The field_match_compressed setting was added after a pre-submission diagnostic identified the missing shared-compression comparison. It was not preregistered before the diagnostic result was known. Inputs retain all 256 v7.67 records and 986 candidates from the official GNN4TaskPlan archive; tasks were neither added nor selected by outcome.

The four settings are audit_only, field_match, field_match_compressed and full. The added setting applies the same compress_redundant_order_edges implementation used by the full method after one-pass field matching, with the same S0, Sg, final audit and strict scheduling. Repair does not read the reference. The three existing settings and their inputs remain unchanged. Every accepted result also passes independent graph and schedule checks.

For the 160 controlled records, the report retains non-order five-component edge-key F1 over all records, strict acceptance counts, and same-node serial-time/schedule-time ratios over accepted records. Means and sample standard deviations are saved separately. The 96 relation views still derive from 24 base tasks and are reported separately for the four views. Paired makespan counts use absolute tolerance 1e-10; no significance inference is made.

Adaptation, reference isolation and denominator conventions for the public archive remain those of v7.67; the two archived model groups are reported separately. Archive replay is not presented as a new API call, and formal acceptance in the tool domain is not robot semantic correctness. Full per-record artifacts for all four settings are retained.

The v7.69 change tightens floating-point schedule acceptance: strictly positive intervals, relative duration error no greater than 1e-9 without an absolute-tolerance exemption, and finite aggregate values. Existing three-method results on the frozen inputs are checked against v7.67. Historical wall-clock measurements retain their original environment and version and are not relabelled as current measurements.
