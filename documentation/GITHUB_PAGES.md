# Future GitHub Pages publication

Current state: local preparation only. The repository has no configured remote. These are later release instructions, not executed upload steps.

1. Confirm the final GitHub repository owned by the intended account. Confirm authors, affiliations, paper status and reusable figure rights; add the verified author line and paper link to `docs/index.html`. Do not invent a DOI, arXiv ID or accepted-venue label.
2. Run `python tools/check.py` and the complete frozen reproduction command. Inspect `git status` and ensure no local outputs, credentials, Word drafts or EndNote data are included.
3. Once upload is separately requested, configure the actual remote and push the reviewed local commits. No authentication or upload helper is included in this repository.
4. In that repository's Pages settings, select deployment from the `main` branch and `/docs` folder. This static site has `.nojekyll`, no build dependency, and relative asset paths suitable for a project subpath.
5. Verify the URL actually assigned by GitHub Pages. Check all figure switches, downloads, resource links and small-screen layout. Add canonical/Open Graph absolute URLs only after that URL is confirmed. The local-only notice hides automatically on non-local hosts.
6. Replace the temporary `http://127.0.0.1:8780/` address in a **new** manuscript version. Preserve Word/EndNote fields and inspect the rendered page. Record the released Git commit and archive SHA-256. The supplementary archive version remains v7.70 unless its contents actually change.

No `.github` upload workflow, remote, CNAME, public repository link or fabricated citation is preconfigured. The local homepage can be run any time with `python tools/serve.py`.
