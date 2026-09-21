# MuJoCo dual-Panda execution experiment

This **new** simulation executes the accepted plans using two Panda models, joint position actuators, inverse kinematics, prescribed Cartesian waypoints, and frictional finger contacts. No weld, attachment or post-initialization object-pose reset is used. It is separate from the unchanged v7.70 planning archive and the older website schedule animations.

Three constructed templates cover parallel sorting (4 nodes), a shared geometric inspection station (6 nodes), and cooperative tray transfer (5 nodes, including one B task). Each has five XY initial-position seeds (uniform ±10 mm), paired between full scheduling and a serial control, giving **30 executions / 15 paired conditions / 3 task templates**. Candidates have fixed node fields and initially empty relations. The serial control uses the same repaired graph, assignment, durations and skill programs in a topological serialization. This evaluates schedule execution and concurrency, not superiority over alternative repair heuristics.

## Reproduce

Use Python 3.11, install `simulation/requirements.txt`, and put FFmpeg on PATH. From the repository root:

```sh
python simulation/run_experiments.py --output local_runs/mujoco_new
python simulation/verify_results.py local_runs/mujoco_new
```

The output directory must not exist. The protocol and code hashes are saved before execution. The default evaluates seeds 0–4; seed 0 is recorded for both methods in each case. To omit video while reproducing physics, pass `--record-seed -999`. Rendering uses a hidden OpenGL context; hardware/driver differences can affect numerical outputs. No robot connection is involved.

## Physical model and observation contract

MuJoCo 3.3.3, 2 ms physics steps, 20 ms controller updates, gravity −9.81 m/s², gravity compensation on robot bodies, position actuators within the imported joint-force limits, sliding friction 1.5, elliptic friction cone, 100 solver iterations, and 5 no-slip iterations. The local Panda model comes from `franka_description` 0.7.1 bundled with Isaac Sim's URDF importer. Kinematics/inertials and collision STL meshes are retained; these parameters are not calibrated to physical hardware. Source hashes, package metadata, conversion output and meshes are preserved under `assets/`.

Pick/place and station-service windows are fixed at 6 and 8 seconds. Cooperative approach, transfer and retreat windows are 3, 12 and 2 seconds. The station represents object presence within 35 mm horizontally and a height band of 0.58–0.66 m for at least 0.5 s; it is a geometric service proxy, not an inspection-sensor model. Simulation makespans are therefore conditional on these fixed skill windows. Initialization settling (0.4 s) and final settling (0.5 s plus one integration step) are excluded from the reported task window, equally for both methods.

Success requires task postconditions and final goals, final object-position error below 30 mm, final linear speed below 0.02 m/s, no detected inter-arm penetration contact deeper than 1 mm, no simultaneous station-zone occupancy, no physics warning, and—in the designated cooperative carry interval—contact between the tray and both robot arms on more than 90% of physics steps (the original online detector includes all robot links). These are finite experimental observations, not a theorem about continuous collision avoidance. Final error is the Euclidean distance from the body origin to its target, not a full pose error.

`states.jsonl` and `trajectory.npz` are sampled every 40 ms after synchronized integration. The independent checker reconstructs poses from saved generalized coordinates, checks event timing, relation order, execution-unit/resource capacity, final targets and sampled station/contact conditions. The live simulator additionally counts contacts at every 2 ms step. The independent checker does not certify unseen continuous-time behavior.

## Results and media

Read `results/aggregate_results.json`, the per-run `summary.json`, task events, trajectories and `independent_verification.json`. Video sources in `docs/assets/data/simulation.json` have hashes and predefined selection metadata. Six 1280×720, 25 fps MP4s show the three cases under full and serial scheduling; the project page provides a method switch.

Development failures and the corrected 2 ms logger-alignment issue are documented in `development/`. They are not mixed with the final evaluation. The three templates and five small position perturbations do not establish industrial generalization, sensor robustness, grasp-policy learning, hardware transfer or statistical significance.

## Finger-specific contact audit

The frozen protocol/summary uses the label `both_grippers_contact`, but the online implementation actually counts contacts from any link on each robot. Those frozen bytes are preserved. `verify_finger_contacts.py` adds a more specific check of saved 40 ms samples, requiring `leftfinger` or `rightfinger` body contacts from both arms. All 10 cooperative runs have 152/152 qualifying sampled frames. This additional audit was performed after evaluation; it does not certify finger contacts at unsampled times.

```sh
python simulation/verify_finger_contacts.py local_runs/mujoco_new
```
