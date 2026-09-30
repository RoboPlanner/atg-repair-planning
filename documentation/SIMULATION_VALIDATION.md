# Historical 30-run simulation validation

This document records the 2026-09-22 exploratory study. For the current 240-run study, use the [current guide](https://roboplanner.github.io/atg-repair-planning/guide.html#simulation) and [evidence index](https://roboplanner.github.io/atg-repair-planning/evidence.html). Historical manuscript numbers below are not current figure/table numbers.

Validated locally on 2026-09-22. The Chinese manuscript v7.74 adds Section 4.10, Table 17 and Appendix A.6. No historical video is used as evidence for this study.

## Frozen evaluation

| Constructed task template | Paired initial states | Full / serial success | Serial → full task window | Maximum final position error, full |
| --- | --- | --- | --- | --- |
| Parallel sorting | 5 | 5/5 / 5/5 | 24 → 12 s | 7.48 mm |
| Shared geometric inspection station | 5 | 5/5 / 5/5 | 40 → 28 s | 16.80 mm |
| Cooperative tray transfer | 5 | 5/5 / 5/5 | 22 → 17 s | 1.05 mm |

The 30 executions represent 15 paired initial conditions and **three task templates**, not 30 independent task categories. Initial XY positions vary uniformly within ±10 mm. Skill durations and waypoints are fixed. These are simulated task windows, excluding equal initialization/final settling; their differences follow from permitted concurrency. They do not measure hardware speed or compare alternative relation-repair heuristics.

The 30 runs passed the declared completion conditions and the independent saved-trajectory/event checker. A second execution of all 30 conditions from the packaged source reproduced every per-run summary field exactly except the intentionally omitted video frame-rate field. This rerun is a reproducibility check, not 30 additional experimental samples.

The original online `both_grippers_contact` label counts contacts from any robot link on each side. Frozen records retain that label. An additional finger-specific audit found both sides' finger-body contacts in 152/152 saved carry frames for each of the 10 cooperative runs. This audit is at 40 ms sampling; it does not establish full-rate or continuous finger contact. See `simulation/verify_finger_contacts.py` and `simulation/results/frozen_v2/finger_contact_verification.json`.

## Reproduction and media checks

- The formal planning code remains the frozen v7.70 implementation. The existing 269-file planning manifest and its ZIP still match all original hashes.
- The simulation source hashes match its before-run frozen protocol. Its separate manifest covers 244 files.
- The simulation ZIP contains code, imported model assets with Apache-2.0 notices, original project license, all final logs/trajectories and six MP4s. SHA-256: `b9e6fe72142860ea65b645d2b5ac6ad41100a2ed80e837b8ed91b9d6a0bc1488`.
- All six H.264 files fully decode at 1280×720 and 25 fps. Three sampled frames from each were inspected for task progression, layout and occupancy display. Seed 0 was selected before evaluation for both methods in each scene.
- Website playback, scene/method switching and 2× playback were tested. Desktop and mobile layouts were inspected; no document overflow at 390-pixel viewport and no browser error/warning were observed.
- The new JavaScript passes syntax checks. HTML IDs are unique. The 38 local link/asset candidates checked during packaging return matching local bytes where they reference files.

Failed pilots and the corrected 2 ms pose-log alignment are recorded separately in `simulation/development/`. Final results are `frozen_v2`; no failed developmental run is silently relabelled as a final success. All work remains local; no GitHub push or Pages publication was performed.

## Evidence boundary

The adapter uses inverse kinematics, fixed Cartesian waypoints, joint position actuators and frictional finger contact in MuJoCo 3.3.3. It is an execution connection for the planning method, not a new motion planner or learned controller. The station models geometric presence, not a real inspection sensor. Finite success in these scenes does not establish hardware transfer, continuous collision avoidance, natural-language semantic repair benefits or general industrial robustness.
