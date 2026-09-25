# Interactive GitHub Pages demo
Author: Armando Gomez

Demo address: https://armandosnhu.github.io/TechOpsagent/

## Try it
1. Select Checkout API failure, Inventory timeout, or Credential rejected.
2. Choose **Investigate this incident**.
3. Review evidence, suspected cause, impact, next steps, and prevention.
4. Choose **Download draft RCA** for the selected case's Markdown report.
5. Select another incident or use **Reset case** to start again.

This static browser-only fixture viewer works on desktop and phone without installation, login, an API key, or a running local computer. Every case is synthetic. Diagnoses are predefined fixture explanations, not live AI inference or confirmed production root causes.

The full local FastAPI application provides live loopback checks, imported logs, saved history, optional local inference, and configured integrations. GitHub Pages does not host those services. See [setup.md](../setup.md). Public demo access does not complete authenticated phone access to the local application.

## Files and publication boundary
| File | Purpose |
|---|---|
| `site/index.html` | Semantic page structure and content-security policy |
| `site/style.css` | Responsive layout, focus states, reduced motion |
| `site/app.js` | Case selection, evidence rendering, reset, report links |
| `techops/engine.py` | Shared synthetic fixtures and report renderer |
| `tools/build_pages.py` | Explicit artifact allowlist and deterministic generation |
| `.github/workflows/pages.yml` | Test, privacy scan, build, upload, deploy |
| `tests/test_pages.py` | Isolation, consistency, repeatability, stale-output refusal |

The builder copies exactly three site files, writes `scenarios.json`, creates three synthetic Markdown reports, and adds `.nojekyll`. Only this generated directory is uploaded. It never loads operator `.env`, SQLite records, runtime logs, integration settings, or model output. It refuses existing output directories instead of merging unknown files into an artifact.

The browser fetches one same-origin JSON fixture. It does not contact FastAPI, Grafana, Loki, ServiceNow, or an AI provider. The demo code has no uploads, account forms, telemetry, cookies, or browser storage. GitHub Pages itself handles ordinary hosting requests. Generated text uses `textContent`; ticket HTML is not interpreted. The content-security policy restricts scripts, styles, and connections to the site origin.

## Build and preview locally
From the repository root, after the normal Python setup:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
node --check site/app.js
.\.venv\Scripts\python.exe -m tools.build_pages --output data/pages-preview
.\.venv\Scripts\python.exe -m http.server 8770 --bind 127.0.0.1 --directory data/pages-preview
```

Open http://127.0.0.1:8770. Ctrl+C stops the preview. Use a new output directory for another build, or manually remove only the previously generated artifact after reviewing its exact path. Node is needed for the optional JavaScript syntax check; Python alone builds and serves the demo. Direct `file://` opening is unsupported because the browser fetches fixture JSON.

## Deploy and verify
Repository Settings → Pages uses **GitHub Actions**. A push to `main` or manual workflow dispatch runs **Publish interactive demo**. Tests and privacy checks must pass before upload. The deployment job alone receives Pages write and identity-token permissions. Action references are pinned to commit hashes. No operator credential is configured for deployment.

The workflow publishes only `data/pages`, never the repository root. Do not change the artifact path to `.`. Generated artifacts are Git-ignored. Maintain the synthetic-only fixture contract and visually inspect screenshots before committing them.

After deployment, check all three cases, reset, report downloads, browser console, and mobile width at the public address. Relative asset/report URLs preserve the `/TechOpsagent/` prefix. If fixtures fail to load, the page displays an unavailable state and leaves investigation disabled.
