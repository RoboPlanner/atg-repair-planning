# Local preparation validation

Checked on 2026-09-21 against the unchanged v7.70 supplementary snapshot.

- 269 manifest-listed files and the supplementary ZIP match their frozen SHA-256 values. The 270th archive member is the manifest itself.
- All 58 current implementation regression tests and 8 independent public-source checker tests pass.
- `reproduce_all.py` was run from this repository in a fresh directory. All three suites matched the archived stable outputs exactly. Machine timings were not compared.
- The illustrative tea candidate passes both the formal interface and the independent graph/schedule checker. Tasks t1/t2 run at [0,2), t3 occupies both units at [2,5), then t4 at [5,7) and t5 at [7,9). These are demonstration values, not additional experimental measurements.
- The command-line wrapper rejects missing initial-state context and refuses to overwrite an existing output.
- Local HTML links and assets respond with HTTP 200 and match their on-disk bytes. HTML IDs are unique and images have alternative text.
- Desktop and 390-pixel viewport previews were inspected. The page has no horizontal document overflow at the tested mobile width. Method-figure switches and command-copy feedback work; no browser error or warning was observed during those checks.
- No remote was configured, no GitHub upload was performed, and no Pages deployment was enabled during this preparation.

Local generated runs and preview logs are ignored by Git. Follow the root README to repeat the checks on a different machine.
