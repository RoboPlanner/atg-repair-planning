# GitHub repository and project-page deployment

- Repository: [https://github.com/RoboPlanner/atg-repair-planning](https://github.com/RoboPlanner/atg-repair-planning)
- Project page: [https://roboplanner.github.io/atg-repair-planning/](https://roboplanner.github.io/atg-repair-planning/)
- Deployment source: `main` branch, `/docs` directory.
- The static page includes symbolic schedule animations, actual MuJoCo simulation recordings, and frozen code/data downloads. It does not report hardware execution.

## Updating the page

Edit the static files under `docs/`, verify local links and assets, then commit and push to `main`. GitHub Pages builds the `/docs` directory. Check the Pages deployment status before describing an update as live. The site has `.nojekyll`, relative asset links, and no external build dependency.

Before publishing code or data changes, run `python tools/check.py`. Keep frozen archive bytes and their SHA-256 manifests unchanged. New experimental runs must use new output directories and be identified separately from archived results. Local checks and reproduction commands do not upload data.

Author names, affiliations, a paper URL and formal citation metadata remain to be confirmed. Code availability does not imply journal acceptance. When updating the manuscript's temporary local link, save a new version and check the current Word/EndNote fields before and after editing.

Local preview remains available through `python tools/serve.py` at `http://127.0.0.1:8780/`.
