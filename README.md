# ATG Repair — Verifiable Dual-Unit Planning

[Current project guide](https://roboplanner.github.io/atg-repair-planning/guide.html) · [Complete evidence index](https://roboplanner.github.io/atg-repair-planning/evidence.html)

[GitHub repository](https://github.com/RoboPlanner/atg-repair-planning) · [Project page](https://roboplanner.github.io/atg-repair-planning/)

**Deterministic relation repair, joint auditing, and strict list scheduling for atomic task graphs.**

Manuscript author identities, affiliations and contact details are omitted. Third-party citations and license attribution identify upstream sources, not the manuscript authors.

[中文说明](README.zh-CN.md) · [Website HTML source](docs/index.html) · [Code & experiment map](documentation/CODE_AND_EVIDENCE.md) · [Reproduction protocol](reproduction/external_discrete_protocol.md)

Research materials for *Verifiable Atomic Task Graph Relation Repair and Planning-Level Parallel Planning for Dual-Unit Collaborative Tasks*. The current manuscript is v7.87 (2026-09-30). The original planning archive retains its v7.70 version, and the expanded MuJoCo study retains its v2 archive identity; manuscript formatting changes do not create new experimental results. This repository provides research code and data; no journal acceptance or DOI is asserted.

`L` and `R` are two abstract base execution units. Cooperative mode `B` occupies **both units simultaneously**. Candidates may originate from a language model, rules, or a user. A fixed deterministic pipeline performs state closure → sync pairing → resource orientation → conservative order compression. Six joint graph checks and actual schedule validation gate accepted outputs. Failed checks return diagnostics; rejection does not establish infeasibility.

## Quick start

Clone the repository once, then run the commands from its root:

```sh
git clone https://github.com/RoboPlanner/atg-repair-planning.git
cd atg-repair-planning
```

Use **Python 3.11+**. The planning implementation and its three frozen evaluation suites use the standard library only. The expanded physics simulation has separate dependencies listed below. No API key, model endpoint, GPU, or robot connection is needed. Commands below run from the repository root unless a `cd` is shown.

```sh
python tools/verify_archive.py
python tools/run_plan.py examples/tea_candidate.json --output local_runs/tea_result.json
```

The tea example is a hand-authored interface demonstration, **not a new experimental sample**. Its durations are symbolic illustrative values. The output contains the repaired graph, audit, accepted/rejected edit log, schedule when accepted, and failure diagnostics when rejected. Output files must not already exist.

## Reproduce the frozen evaluations

```sh
cd reproduction
python reproduce_all.py results/new_run
```

Use a new output directory. This reruns and compares stable outputs for:

- 1,024 internal and 3,944 archived public-tool **setting records**;
- 52 public-specification setting records (13 inputs × 4 settings);
- 8,640 finite mechanism setting records (1,728 constructed inputs × 5 settings).

Setting records are not independent task counts. Timings and timestamps are not expected to reproduce exactly. The script prints `All frozen evaluation results reproduced exactly; timing is not compared.` on success.

Historical MILP and timing experiments use `reproduction/requirements-historical.txt` (`numpy==1.26.0`, `scipy==1.15.3`). Their rerun entry is documented in [CODE_AND_EVIDENCE.md](documentation/CODE_AND_EVIDENCE.md). Historical measurements are retained as historical measurements, not relabelled as new v7.70 timing runs.

## Run checks

```sh
python tools/check.py
```

This verifies every manifest-listed archive file and runs **58 implementation tests + 8 independent public-source checker tests** with the current v7.70 implementation. It fails with a nonzero exit status if a check fails. No files under the frozen archive are rewritten.

## Local project page

```sh
python tools/serve.py
```

Open **http://127.0.0.1:8780/**. Keep the process running; Ctrl+C stops it. The server binds only to the local loopback interface and serves `docs/`, not the Git metadata or private project workspace. If 8780 is occupied, `python tools/serve.py --port 8781` uses another port; 8780 is only a local preview address; the manuscript cites the public project page.

The static page also opens directly as `docs/index.html`. It works without external fonts, analytics, a build system, or CDN scripts. Relative asset URLs are compatible with a GitHub Pages project subpath. The method figures can be switched and opened at full resolution. The downloadable ZIP retains the frozen supplementary bytes.

### Earlier 30-run simulation study

The separate [exploratory ZIP](https://roboplanner.github.io/atg-repair-planning/assets/downloads/ATG_MuJoCo_simulation_v1.zip) retains six dual-Panda recordings; [the current simulation player](https://roboplanner.github.io/atg-repair-planning/#simulation) instead shows the eight-template, 240-run study. Three constructed task templates (parallel sorting, shared station, cooperative tray transfer), five initial-position seeds and two scheduling methods give **30 executions / 15 paired conditions**. All 30 completed the declared task checks and independent trajectory/event rechecks. Serial → full task windows are 24 → 12, 40 → 28 and 22 → 17 simulated seconds. These windows use fixed skills; they are not hardware measurements or a comparison between repair heuristics.

```sh
python -m pip install -r simulation/requirements.txt
python simulation/run_experiments.py --output local_runs/mujoco_new
python simulation/verify_results.py local_runs/mujoco_new
```

Use Python 3.11 and FFmpeg on PATH; add `--record-seed -999` to omit video. The supplied models, frictional contacts, state/event logs, independent checker and documented development failures are in [simulation/README.md](simulation/README.md). The downloadable [simulation supplement](https://roboplanner.github.io/atg-repair-planning/assets/downloads/ATG_MuJoCo_simulation_v1.zip) includes the formal planning code it needs. This is a separate addition; the symbolic replays below retain their original meaning.

### Experimental animations

Open the [public planning replays](https://roboplanner.github.io/atg-repair-planning/#experiments) for three interactive replays of frozen accepted schedules: controlled drink preparation, public parallel assembly, and the ft06 resource-ordering comparison. Use pause, restart, playback speed, or the time slider to inspect task progress and L/R occupancy. Cooperative B tasks span both lanes. Each case also has a downloadable animated SVG; no video service or external script is required.

These are symbolic planning-layer replays, not robot footage or new experimental samples. The six-node controlled case is distinct from the five-node tea illustration. The ft06 comparison uses a common time axis and reports its instance-specific result; aggregate and negative results remain in the evidence section.

```sh
python tools/build_replays.py
```

This regenerates the player data and animated SVGs from the archived records after independent graph/schedule checks and, where applicable, public-source checks. It does not modify the frozen archive. See [replay provenance and verification](documentation/EXPERIMENT_REPLAYS.md).

The layout references [Nerfies](https://github.com/nerfies/nerfies.github.io) and [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template). The page implementation is original; template code, authors, media, and acceptance badges were not copied. See [template sources](documentation/TEMPLATE_SOURCES.md).

## Repository layout

```text
docs/                         Static GitHub Pages-ready website
  index.html                  Homepage
  assets/images/              Current manuscript figure exports
  assets/downloads/           Frozen supplementary ZIP and guides
  assets/data/evidence.json    Source-linked result summaries
  assets/data/replays.json     Frozen schedule data and source hashes
  assets/animations/           Standalone animated SVG replays
simulation/                   Historical exploratory study: 30 runs
simulation_expanded/          Current expanded study: 240 runs, 96 planning settings
documentation/                Code/evidence map, provenance, release steps
examples/tea_candidate.json    Illustrative nine-field input
tools/                        Preview, integrity, test and plan entry points
reproduction/                 Frozen v7.70 supplementary package
  implementation_v7_70/       Current implementation and regression tests
  implementation_v7_69/       Preserved historical implementation
  inputs/                    Frozen evaluation inputs
  results/                   Archived per-record and summary outputs
  sources/                   Public specification snapshots + licenses
  external/                  Public tool reference/candidate snapshots
  analysis_outputs/          Selected historical experiments
  dual_arm_task_experiments/  Controlled-study evidence
```

The frozen directory structure is intentionally preserved because scripts and SHA-256 records depend on it. Start at `implementation_v7_70/atomic_task/pipeline.py::run_verified_atg`; do not treat a historical implementation or low-level diagnostic helper as the formal acceptance interface.

## Evidence and limitations

| Evaluation | Finding | Interpretation |
| --- | --- | --- |
| Controlled records, 160 | Edge F1 0.9018 → 0.9813 | Four topologies × 40 duration variants |
| Same input, shared compression | Simple 0.9853 / 1.2619×; full 0.9813 / 1.2535× | Edge F1 / mean speedup; no full-method advantage on this sample |
| Six two-unit job-shop projections | Mean paired makespan reduction 25.7167% | Full vs shared-compression simple comparator; not original JSP optima |
| Public planning specifications | 41/41 accepted outputs pass source checks | 13 inputs, 52 setting records; conditional validation, not completeness |
| Constructed three-node family | Full accepts 720/736 feasible inputs | 16 feasible rejections; finite checks do not prove complete repair |
| Archived public tool candidates | Formal acceptance rises, reference edge F1 falls | Tool dependencies do not provide robot resource/B-occupancy semantics |
| 24 GPT-6 conversation candidates | All original candidates pass; zero net relation change | Same method-aware session; not an independently verifiable API benchmark |

Guarantees cover represented discrete states, capacity-one resources and unit occupancy. They do not cover omitted semantics, continuous collisions, trajectories, or hardware execution. No general optimality, significance, or natural-error repair benefit is inferred from these finite or constructed inputs.

## Integrity, licensing, and publication

The fixed archive is [ATG_reproduction_v7_70.zip](https://roboplanner.github.io/atg-repair-planning/assets/downloads/ATG_reproduction_v7_70.zip) (4.6 MiB). SHA-256:

```text
922881a57e08e3cc1a0f28e283e2837dabfb486d1c612fc282feb4575a8f0f4a
```

[MANIFEST_SHA256.json](reproduction/MANIFEST_SHA256.json) covers 269 archive files; the manifest itself is the 270th archive member. Root Git attributes preserve all archived bytes across platforms. `tools/verify_archive.py` verifies both the extracted files and ZIP hash.

Original code/documentation: [MIT](LICENSE). Website text/layout/manuscript figures: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Third-party materials retain their notices; see [LICENSES.md](LICENSES.md). The author’s EndNote library, Word drafts, account email, credentials, and local machine configuration are outside this repository.

Deployment instructions are in [GITHUB_PAGES.md](documentation/GITHUB_PAGES.md). Local verification and reproduction commands do not upload data. The project guide and evidence index are linked at the top. Paper reading links are temporarily hidden; author details and formal publication metadata remain unassigned. The repository can be used independently of the unpublished manuscript.

## Expanded physical simulation study

See [simulation_expanded/README.md](simulation_expanded/README.md) for eight task templates, 240 frozen physics runs, 96 planning settings and 20 preselected videos. Normal-condition schedules complete 80/80 runs; stress conditions complete 104/160. All failures and independent reconstructions are retained. This replaces the exploratory simulation summary in the latest manuscript without altering the earlier archive. In manuscript v7.87, Figures 9–11 and Tables 12–14 report this batch; earlier manuscript drafts used different table numbering. No hardware or natural-error generalization is claimed.
