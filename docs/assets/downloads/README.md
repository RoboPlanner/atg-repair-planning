# ATG Repair — Verifiable Dual-Unit Planning

**Deterministic relation repair, joint auditing, and strict list scheduling for atomic task graphs.**

[中文说明](README.zh-CN.md) · [Project-page HTML](docs/index.html) · [Code & experiment map](documentation/CODE_AND_EVIDENCE.md) · [Reproduction protocol](reproduction/external_discrete_protocol.md)

Research materials for *Verifiable Atomic Task Graph Relation Repair and Planning-Layer Parallel Planning for Dual Execution Units* (Chinese manuscript experimental snapshot v7.70). The later v7.71 manuscript edit adds a local project-page link; it does not change the experimental snapshot. This is a local Git release preparation; no public repository, DOI, or venue acceptance is asserted.

`L` and `R` are two abstract base execution units. Cooperative mode `B` occupies **both units simultaneously**. Candidates may originate from a language model, rules, or a user. A fixed deterministic pipeline performs state closure → sync pairing → resource orientation → conservative order compression. Six joint graph checks and actual schedule validation gate accepted outputs. Failed checks return diagnostics; rejection does not establish infeasibility.

## Quick start

Use **Python 3.11+**. The current implementation and three current evaluation suites use the standard library only. No API key, model endpoint, GPU, or robot connection is needed. Commands below run from the repository root unless a `cd` is shown.

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

Open **http://127.0.0.1:8765/**. Keep the process running; Ctrl+C stops it. The server binds only to the local loopback interface and serves `docs/`, not the Git metadata or private project workspace. If 8765 is occupied, `python tools/serve.py --port 8766` uses another port; the temporary manuscript link specifically uses 8765.

The static page also opens directly as `docs/index.html`. It works without external fonts, analytics, a build system, or CDN scripts. Relative asset URLs are compatible with a GitHub Pages project subpath. The method figures can be switched and opened at full resolution. The downloadable ZIP retains the frozen supplementary bytes.

The layout references [Nerfies](https://github.com/nerfies/nerfies.github.io) and [Academic Project Page Template](https://github.com/eliahuhorwitz/Academic-project-page-template). The page implementation is original; template code, authors, media, and acceptance badges were not copied. See [template sources](documentation/TEMPLATE_SOURCES.md).

## Repository layout

```text
docs/                         Static GitHub Pages-ready website
  index.html                  Homepage
  assets/images/              Current manuscript figure exports
  assets/downloads/           Frozen supplementary ZIP and guides
  assets/data/evidence.json    Source-linked result summaries
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

The fixed archive is [ATG_reproduction_v7_70.zip](docs/assets/downloads/ATG_reproduction_v7_70.zip). SHA-256:

```text
922881a57e08e3cc1a0f28e283e2837dabfb486d1c612fc282feb4575a8f0f4a
```

[MANIFEST_SHA256.json](reproduction/MANIFEST_SHA256.json) covers 269 archive files; the manifest itself is the 270th archive member. Root Git attributes preserve all archived bytes across platforms. `tools/verify_archive.py` verifies both the extracted files and ZIP hash.

Original code/documentation: [MIT](LICENSE). Website text/layout/manuscript figures: [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Third-party materials retain their notices; see [LICENSES.md](LICENSES.md). The author’s EndNote library, Word drafts, account email, credentials, and local machine configuration are outside this repository.

For future publication, see [GITHUB_PAGES.md](documentation/GITHUB_PAGES.md). **No upload or deployment is performed by any local preparation command.** Add verified authors, affiliations, paper URL and citation metadata before the public release. Replace the manuscript’s local address only after the public page is live and checked.
