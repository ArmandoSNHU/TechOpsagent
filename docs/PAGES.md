# Interactive GitHub Pages demo
Author: Armando Gomez

Demo address: https://armandosnhu.github.io/TechOpsagent/

## Try it
1. Choose Network or Computer health from the category menu.
2. Open an available tool and choose **Run demo check**.
3. Review synthetic readings, **Explain results**, and **Save report**.
4. Use **Reports & history** to reopen a result from this browser session.
5. Open **Applications → Investigate an incident** for the original three-case investigation demo at `incidents.html`.

See the [illustrated button guide](TOOL-GUIDE.md). Every public reading is synthetic; this static site does not inspect the visitor's device. The full local application collects on-demand Windows readings and supports incident investigations, configured integrations, and optional local inference. Pages does not host those services or complete authenticated phone access to the local app.

## Files and publication boundary
| File | Purpose |
|---|---|
| `techops/static/toolkit/` | Shared category dashboard and tool panels |
| `techops/tool_catalog.py` | Public descriptions and synthetic tool readings |
| `site/index.html` | Incident demo published as incidents.html |
| `site/style.css` | Responsive layout, focus states, reduced motion |
| `site/app.js` | Case selection, evidence rendering, reset, report links |
| `techops/engine.py` | Shared synthetic fixtures and report renderer |
| `tools/build_pages.py` | Explicit artifact allowlist and deterministic generation |
| `.github/workflows/pages.yml` | Test, privacy scan, build, upload, deploy |
| `tests/test_pages.py` | Isolation, consistency, repeatability, stale-output refusal |

The builder publishes 14 files: the toolkit HTML/CSS/JS plus investigation.js, catalog.json, demo.json, the incident HTML/CSS/JS, scenarios.json, three Markdown reports, and .nojekyll. Every source is explicitly allowlisted. Only this generated directory is uploaded. It never loads operator `.env`, SQLite records, runtime logs, integration settings, or model output. It refuses existing output directories instead of merging unknown files into an artifact.

The toolkit fetches same-origin catalog and demo JSON; the incident workspace fetches its own scenario JSON. It does not contact FastAPI, Grafana, Loki, ServiceNow, or an AI provider. The demo code has no uploads, account forms, telemetry, or cookies. Browser localStorage holds only the Light/Neon Night theme preference; diagnostic results remain in tab memory. GitHub Pages itself handles ordinary hosting requests. Generated text uses `textContent`; ticket HTML is not interpreted. The content-security policy restricts scripts, styles, and connections to the site origin.

## Build and preview locally
From the repository root, after the normal Python setup:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
node --check site/app.js
node --check techops/static/toolkit/toolkit.js
.\.venv\Scripts\python.exe -m tools.build_pages --output data/pages-preview
.\.venv\Scripts\python.exe -m http.server 8770 --bind 127.0.0.1 --directory data/pages-preview
```

Open http://127.0.0.1:8770. Ctrl+C stops the preview. Use a new output directory for another build, or manually remove only the previously generated artifact after reviewing its exact path. Node is needed for the optional JavaScript syntax check; Python alone builds and serves the demo. Direct `file://` opening is unsupported because the browser fetches fixture JSON.

## Deploy and verify
Repository Settings → Pages uses **GitHub Actions**. A push to `main` or manual workflow dispatch runs **Publish interactive demo**. Tests and privacy checks must pass before upload. The deployment job alone receives Pages write and identity-token permissions. Action references are pinned to commit hashes. No operator credential is configured for deployment.

The workflow publishes only `data/pages`, never the repository root. Do not change the artifact path to `.`. Generated artifacts are Git-ignored. Maintain the synthetic-only fixture contract and visually inspect screenshots before committing them.

After deployment, check all five tools, explanations, session history, JSON exports, the three incident cases, browser console, and mobile width at the public address. Relative asset/report URLs preserve the `/TechOpsagent/` prefix. If fixtures fail to load, the page displays an unavailable state and leaves investigation disabled.
