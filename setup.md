# TechOpsagent setup
Author: Armando Gomez

## First run
Use Windows 11, PowerShell, Git, and Python 3.12+ (3.13 is verified). Open PowerShell in the cloned repository. No model or cloud account is needed.

```powershell
.\setup.ps1 -Install -Check -Test -EnableHook
.\setup.ps1 -Run
```

The first command creates/reuses .venv, installs pinned dependencies, checks settings, runs tests, and enables the privacy hook. It stops on failure. Only installation needs internet; no models or observability binaries are downloaded by Install. Existing settings and data are preserved. To select Python, add `-Python "C:\path\to\python.exe"`.

Run starts the app in this terminal at http://127.0.0.1:8765. Keep it open; Ctrl+C stops the app. Setup refuses occupied ports and never stops existing processes. Select another port explicitly with `-Run -Port 8768` if appropriate.

In a second terminal:
```powershell
.\setup.ps1 -Check -Live
```

Live checks contact only fixed localhost endpoints, reject redirects, and verify service-specific responses. The app's startup source fingerprint detects older code still running. Exit 1 means a prerequisite or checked service needs attention. Optional unconfigured integrations do not fail setup. External service URLs are never probed here.

With no flags, setup.ps1 displays help and changes nothing. No activation or permanent execution-policy change is needed. If local policy restricts scripts, use the Python alternatives below in accordance with that policy.

## Private configuration
```powershell
.\setup.ps1 -Configure -Service github
.\setup.ps1 -Configure -Service servicenow
```

Choices: all, github, grafana, loki, servicenow. Prompts show set/empty, never existing values. Tokens/passwords use hidden input. Enter keeps a value; a single "-" clears it. Other services are preserved. Invalid input, cancellation, or a detected concurrent edit leaves the original unchanged. Saving normalizes comments/formatting.

Only ignored .env stores settings. Process environment overrides this file, including empty overrides. Restart the app after every settings change: the source fingerprint does not detect configuration changes. Never put credentials in arguments, screenshots, issues, or chat.

For ServiceNow, provide an HTTPS origin and either OAuth bearer token or username/password. Clear the old method when switching. A URL alone is incomplete. Use synthetic records in a developer instance; remote writes are not implemented. See [integration details](docs/INTEGRATIONS.md#servicenow).

## Optional local Grafana and Loki
```powershell
.\setup.ps1 -InstallLab -StartLab -SeedLab
```

InstallLab explicitly downloads version-pinned official Windows builds and verifies checksums. StartLab checks binaries and occupied ports, launches hidden local services, and waits for healthy responses. First-run Grafana migrations can take minutes. Each service has a bounded wait; a timeout leaves the process available for inspection. Logs are in ignored data/observability.

SeedLab sends three generated events only to local Loki. It never forwards machine logs. On later runs:
```powershell
.\setup.ps1 -StartLab -SeedLab
```

Open [the synthetic dashboard](http://127.0.0.1:3000/d/techops-local-lab). Anonymous access is Viewer-only on localhost. The generated admin password stays in .env. Restart TechOpsagent after configuring the endpoints, then analyze checkout logs. Re-seed when events age beyond the 15-minute window.

Different configured service URLs and unrecognized listeners are preserved; setup stops for conflict resolution. It never resets existing credentials or terminates services. See [the lab guide](docs/INTEGRATIONS.md#native-windows-observability-lab).

## Everyday commands
| Action | Command |
|---|---|
| Offline check | `.\setup.ps1 -Check` |
| Check running services | `.\setup.ps1 -Check -Live -Port 8765` |
| Run tests | `.\setup.ps1 -Test` |
| Start app | `.\setup.ps1 -Run -Port 8765` |
| Configure one service | `.\setup.ps1 -Configure -Service github` |
| Enable privacy hook | `.\setup.ps1 -EnableHook` |

Order: install environment, configure, install/start/seed lab, check, test, enable hook, run. Do not combine Run and Live; use a second terminal for Live after startup. A custom Git hooksPath is preserved; merge hooks manually if needed.

## Direct Python alternatives
Run from the repository root with the explicit project interpreter:
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -m techops.settings --edit --service github
.\.venv\Scripts\python.exe -m techops.diagnostics
.\.venv\Scripts\python.exe -m techops.diagnostics --live --port 8765 --json
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe -m techops.server --port 8765
```

Diagnostics uses the standard library and can report missing packages before app dependencies are installed. JSON contains statuses/package names, not secret values or private service URLs. The native lab launcher requires Windows.

## Verification
- [ ] Offline check reports READY and tests end with OK.
- [ ] Fresh app passes Live; configured local lab services are healthy.
- [ ] Investigate a synthetic incident, export its report, and reopen history.
- [ ] Seed fresh Loki events and analyze checkout if using the lab.
- [ ] Preview a ServiceNow draft: dry_run true, remote_write false.
- [ ] Before publication, check staged content, history, and screenshots.

```powershell
.\.venv\Scripts\python.exe -m tools.publish_guard --staged
.\.venv\Scripts\python.exe -m tools.publish_guard --history
```

Actual counts are in [STATE.md](STATE.md) and [validation](docs/VALIDATION.md). Development tasks are in [the checklist](Tech%20Ops%20Agent.md).

## Troubleshooting
- Stale/occupied preview: Ctrl+C in its terminal, or verify the exact background process identity before stopping it. Never stop all Python processes.
- Missing lab binaries: InstallLab. Initialization pending: inspect ignored logs, allow migrations to finish, and check again.
- Invalid settings: use private Configure prompts. Never paste .env into a diagnostic report.
- Missing/mismatched packages: rerun Install. Setup does not delete an existing incompatible .venv.
- Direct phone access remains separate work; use the existing authenticated remote session. Never expose these unauthenticated localhost services publicly.

Offline AI preview remains available via `.\.venv\Scripts\python.exe -m techops.ai --dry-run --scenario api_error`. Setup never downloads or starts models. See [model evaluation](docs/MODEL-EVALUATION.md).
