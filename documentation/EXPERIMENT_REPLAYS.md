# Experimental schedule replays

The homepage replays accepted schedules already present in the v7.70 archive. No candidate is newly generated, repaired, rescheduled, or added to the experimental sample count by the exporter.

| Replay | Frozen record / setting | Nodes | Makespan in symbolic input units |
| --- | --- | ---: | ---: |
| Controlled drink preparation | `pour_drink_001` / `full` | 6 | 12.49 |
| Public parallel assembly | `parallel_branch_light` / `full` | 3 | 7 |
| Resource-ordering comparison | `ft06` / `field_match_compressed`, `full` | 36 each | 152, 113 |

The first case's raw candidate was rejected; only the accepted full-method output is replayed. It is not the five-node illustrative tea task. The assembly case is the retained planning projection of a public specification, not a replay of its original geometric simulator. The job-shop case uses the same input and shared order compression, with two added abstract execution units; its results are not original JSP optimal makespans. The 25.66% reduction shown for ft06 is instance-specific, distinct from the six-instance aggregate reported elsewhere.

## Source records

- `reproduction/results/fair_comparison/comparison_details.jsonl`
- `reproduction/results/fair_comparison/frozen_comparison_inputs.jsonl`
- `reproduction/results/external_discrete_run01/details.jsonl`
- `reproduction/results/external_discrete_run01/frozen_cases.json`

Each case in `docs/assets/data/replays.json` contains its full graph, schedule, metrics, selected setting, source file paths, and SHA-256 hashes. Graphs shown above single-plan timelines are explicitly state-support projections; the full accepted graph constrains each stored schedule. Precise state labels and task intervals are available in SVG tooltips and the downloadable JSON. Resources are taken verbatim from the archived schedule; missing declarations are not filled in for presentation.

## Generate and verify

Run from the repository root with Python 3.11+:

```sh
python tools/verify_archive.py
python tools/build_replays.py
```

The exporter selects unique accepted records, runs the archived independent graph and schedule validators for all four schedules, and runs the independent source validator for the three public-source schedules. It stops on failure. Results are recorded in `replay_verification.json`. The archive is read only.

Outputs:

- `docs/assets/data/replays.json`: data and provenance.
- `docs/assets/data/replays.js`: the same data in a local script, enabling offline `file://` use without network requests.
- `docs/assets/animations/*.svg`: three standalone animated SVGs.
- `documentation/replay_verification.json`: fresh independent check results.

`docs/assets/replays.js` implements the interactive player. SVG geometry is generated from stored start/finish times. B occupies both L and R in a single spanning rectangle. The ft06 panels share one time scale. The initial 12 seconds of a 14-second visual cycle traverse the schedule; the last 2 seconds hold the completed state. Playback speed is arbitrary and is not an experiment runtime measurement.

The homepage provides pause, restart, 0.5×/1×/2× speed, a time slider, and live unit/resource states. It pauses progression when off screen or the tab is hidden; reduced-motion preference starts it paused. On narrow screens, controls fit the page while the readable diagram scrolls horizontally. Standalone SVGs loop automatically in SVG-capable browsers and contain no JavaScript. Use the homepage player when manual playback control is required.

These visualizations establish no additional semantic correctness, hardware performance, or method superiority beyond the archived evidence and its stated limits.
