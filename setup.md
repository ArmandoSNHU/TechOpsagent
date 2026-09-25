# TechOpsagent setup
Author: Armando Gomez

## Requirements
Windows 11, PowerShell, Python 3.10 or newer, and a modern browser. Python 3.13 is the verified local interpreter. Internet access is needed only when installing dependencies. No model or cloud account is required.

## Installation checklist
- [ ] Open PowerShell in the repository root.
```powershell
Set-Location D:\TechOpsagent
python --version
```
- [ ] Create the isolated environment if it does not already exist.
```powershell
if (-not (Test-Path .venv\Scripts\python.exe)) { python -m venv .venv }
```
- [ ] Install the pinned dependencies and check them.
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
```
Expected check: `No broken requirements found.` Explicit interpreter paths avoid PowerShell activation-policy problems.

## Verification checklist
- [ ] Run every automated test; stop and fix failures before proceeding.
```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```
The latest verified count is recorded in STATE.md and docs/VALIDATION.md. The run must end in `OK`.
- [ ] Start the server in this terminal.
```powershell
.\.venv\Scripts\python.exe -m techops.server
```
- [ ] In a second terminal, check health and the generated API schema.
```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
Invoke-RestMethod http://127.0.0.1:8765/openapi.json | Select-Object openapi
```
Health must report `status: ok` and `framework: fastapi`.
- [ ] Open http://127.0.0.1:8765, select an incident, and click Investigate incident.
- [ ] Confirm evidence appears, history adds a record, and Download report returns Markdown.
- [ ] Refresh and reopen the saved record from history.
- [ ] Verify the 390 px mobile layout with Chrome device emulation and capture a full screenshot plus a focused investigation-panel snippet. See docs/PROGRESS.md.

## Export sample reports
```powershell
.\.venv\Scripts\python.exe -m techops.demo
```
Expected: `Exported 3 synthetic incident reports to examples/`.

## Stop and restart
Press Ctrl+C in the server terminal. Restart after Python changes before live validation. If an older preview was started in the background, identify its exact command before stopping it:
```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Select-Object ProcessId, CommandLine
```
Only stop the verified TechOpsagent process: `Stop-Process -Id <verified-process-id>`. Never stop unrelated Python processes.

## Troubleshooting
- Port busy: identify the existing preview, or start with `--port 8766` and use that port in all browser and health URLs.
- FastAPI import fails: use `.\.venv\Scripts\python.exe`, then reinstall requirements if needed.
- HTTP 403: use localhost or 127.0.0.1 with the actual port. The app deliberately rejects other Host values and cross-origin writes.
- API documentation: `/openapi.json` is available offline. Hosted Swagger assets are not required or enabled.
- Unexpected test failure: record the failing output in STATE.md, fix it, then rerun the complete suite before checking a task off.

## Data and access
Local incidents are stored in data/incidents.sqlite3 and excluded from Git. Use synthetic tickets only. Stop the server before backing up the database. The service is loopback-only: a responsive phone layout does not make the server accessible from a phone browser. Use the existing authenticated remote session. Direct remote access is a separate checklist task.

## Task execution
Follow [Tech Ops Agent.md](Tech%20Ops%20Agent.md) in order. Setup checkboxes above are a reusable operator checklist; completed development tasks and acceptance criteria live in that task document. Current handoff status lives only in STATE.md.

## Verify observed evidence and offline AI
Use Live local lab in the dashboard to collect a real controlled failure. Switch to Imported JSONL logs and paste the examples from docs/LOGS.md. Both modes must save a result and produce an evidence-citing report.

```powershell
.\.venv\Scripts\python.exe -m techops.ai --dry-run --scenario api_error
```
Expected JSON: dry_run true, inference_enabled false, and evidence IDs E1–E3. This command does not contact a model service. Live model testing is a separate explicit approval.

## Approved local-model evaluation
The recorded local run used the already installed llama3.2:3b model. See [MODEL-EVALUATION.md](docs/MODEL-EVALUATION.md) for results and reproduction commands. The dashboard still uses rule-based analysis; the model does not start with the web app.

## Read-only integrations
See [integration setup](docs/INTEGRATIONS.md) for GitHub Issues, Grafana health, Loki log intake, configuration, and offline previews.

## Your local settings
Run `.\.venv\Scripts\python.exe -m techops.settings` to enter your integration settings locally. Tokens use hidden prompts. The ignored `.env` is never published; `.env.example` contains only blank fields. The app works as an offline lab without any tokens. Restart after configuration changes.

Before publishing, enable the local guard once with `git config core.hooksPath .githooks`. Run `.\.venv\Scripts\python.exe -m tools.publish_guard --staged` after staging and `.\.venv\Scripts\python.exe -m tools.publish_guard --history`. Review staged screenshots and data manually as well. See [security guidance](SECURITY.md).
