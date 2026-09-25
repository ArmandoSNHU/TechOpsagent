# TechOpsagent
**Support operations lab · Armando Gomez**

**[Open the interactive demo](https://armandosnhu.github.io/TechOpsagent/)** — a category-based diagnostic toolkit, synthetic readings, and incident investigations. Works on desktop and phone; no installation or sign-in. [Demo build and deployment guide](docs/PAGES.md).

A local incident-investigation workspace that turns controlled local failures and imported structured observations into evidence trails, troubleshooting steps, and downloadable incident reports.

![Diagnostic toolkit overview](docs/screenshots/toolkit-overview.jpg)

## Start on Windows
Requires Python 3.12+ and PowerShell. From the cloned repository:

```powershell
.\setup.ps1 -Install -Check -Test -EnableHook
.\setup.ps1 -Run
```
Open **http://127.0.0.1:8765**. Choose Network or Computer health to run an on-demand Windows check. Applications opens the existing incident workspace. The [button guide](docs/TOOL-GUIDE.md) explains each control, reading, and limitation. Ctrl+C stops the foreground app. No account, API key, or model is needed for this workflow.

Use `.\setup.ps1 -Check -Live` in a second terminal to detect unhealthy services and stale previews. Configure private accounts with `-Configure -Service github` or `servicenow`. The full [setup guide](setup.md) covers optional Grafana/Loki installation, startup checks, local credentials, and port conflicts.

## What works today
- Category dashboard with guided symptom shortcuts and an illustrated [button guide](docs/TOOL-GUIDE.md).
- Four on-demand Windows checks: network configuration, TCP connections, resource readings, and selected services. Results stay in tab memory unless explicitly exported.
- FastAPI/Uvicorn backend with strict request models and generated OpenAPI.
- Three evidence modes: **Live local lab**, **Saved fixtures**, and **Imported JSONL logs**.
- Real loopback HTTP checks against disposable controlled 500/504/401 endpoints, a healthy endpoint, and local name-resolution observations.
- Rule-based ranked hypotheses with evidence IDs, explicit competing causes, and insufficient-evidence handling.
- SQLite history, redaction, and downloadable Markdown draft RCA reports.
- Responsive dashboard and actual desktop/mobile screenshots.
- Offline AI prompt preview plus a disabled-by-default local-model adapter.

Local lab failures are intentionally generated. Imported logs are unverified user data. Rule scores are not probabilities; results remain suspected until independently verified. The installed llama3.2:3b model was evaluated locally with approval and no downloads. Six outputs passed format/citation checks, but the review flagged unsupported speculation; explanations remain drafts requiring review. GitHub intake and the local Grafana/Loki lab are verified. The ServiceNow adapter and draft preview are implemented; its live instance connection and authenticated direct phone access remain pending.

## Repeatable verification
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m techops.demo
```
The second command writes three synthetic reports in `examples/`. JavaScript syntax can additionally be checked with `node --check techops/static/app.js` when Node.js is installed; Node is not required to run the app.

## Documentation
| Guide | Contents |
|---|---|
| [Task checklist](Tech%20Ops%20Agent.md) | Sequential tasks and acceptance gates |
| [Setup](setup.md) | Reproducible installation and live checks |
| [Design](docs/DESIGN.md) | Scope, architecture, data flow, design decisions |
| [Structured logs](docs/LOGS.md) | Input format, rule scoring, local fault lab |
| [Local AI](docs/AI.md) | Offline preview and approval-gated adapter |
| [Model evaluation](docs/MODEL-EVALUATION.md) | Measured latency, memory, outputs, and limitations |
| [API reference](docs/API.md) | Routes, requests, response fields, errors |
| [Operator guide](docs/OPERATIONS.md) | Run, stop, backup, troubleshooting, phone access |
| [Demo walkthrough](docs/DEMO.md) | A five-minute portfolio presentation |
| [Security](SECURITY.md) | Trust boundaries and known limitations |
| [Roadmap](docs/ROADMAP.md) | Staged plan for live checks and AI integration |
| [Validation](docs/VALIDATION.md) | Test and browser evidence |
| [Progress gallery](docs/PROGRESS.md) | Actual desktop and mobile screenshots |
| [State](STATE.md) | Current handoff and restart point |

## Project map
```text
techops/
  engine.py        Fixture data, redaction, report rendering
  evidence.py      Structured observations and ranked rule-based triage
  lab.py           Disposable loopback failures and probes
  ai.py            Offline prompt preview and gated local-model adapter
  store.py         SQLite storage with explicit connection cleanup
  server.py        FastAPI application and Uvicorn launcher
  security.py      Local Host/Origin checks and request limits
  demo.py          Synthetic Markdown report export
  static/          HTML, CSS, and JavaScript dashboard
 tests/            Engine, API, persistence, and docs-contract tests
 examples/         Three safe sample incident reports
 docs/             Guides, validation record, screenshots
 data/             Ignored local database and runtime logs
```

## GitHub publishing
Create an empty repository named `TechOpsagent`. Review the files and the included `.gitignore` before the first commit; local databases and `.env` files must remain excluded. The folder is prepared as a local Git repository, but no remote publication is performed automatically. Choose a license before publishing if you want to grant reuse rights.

Suggested description: **Local-first support operations lab with evidence-based incident investigations and draft RCA reports.**

For an interview, demonstrate the local fault checks, imported evidence analysis, report exports, and offline AI preview. Distinguish these verified features from limited six-case model evaluation and planned enterprise integrations.


## Read-only integrations
See [integration setup](docs/INTEGRATIONS.md) for GitHub Issues, Grafana health, Loki log intake, configuration, and offline previews.

## Your local settings
Run `.\.venv\Scripts\python.exe -m techops.settings` to enter your integration settings locally. Tokens use hidden prompts. The ignored `.env` is never published; `.env.example` contains only blank fields. The app works as an offline lab without any tokens. Restart after configuration changes.

Before publishing, enable the local guard once with `git config core.hooksPath .githooks`. Run `.\.venv\Scripts\python.exe -m tools.publish_guard --staged` after staging and `.\.venv\Scripts\python.exe -m tools.publish_guard --history`. Review staged screenshots and data manually as well. See [security guidance](SECURITY.md).
