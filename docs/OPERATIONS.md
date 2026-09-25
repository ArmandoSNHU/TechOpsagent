# Operator guide
Author: Armando Gomez

## Start and stop
Run `.\.venv\Scripts\python.exe -m techops.server` from the repository root. The default address is `http://127.0.0.1:8765`. Stop a foreground process with Ctrl+C. Use `--port 8766` for a second instance; both instances use the same local database, so a separate port is not a separate dataset.

A background preview may have been started during development. Inspect its process before stopping it:
```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" | Select-Object ProcessId, CommandLine
```
Stop only the identified TechOpsagent process: `Stop-Process -Id <verified-process-id>`. Do not stop unrelated Python processes. Restart after changing Python code; refresh the browser after changing static assets.

## Data and backup
Incidents are saved to `data/incidents.sqlite3`. The history API returns the latest 100; older records remain in the database. Stop the server before copying the database for backup. Restore by stopping the server and replacing the database with the backup. There is no in-app deletion or retention policy in this release. Use synthetic data only.

## Health check
```powershell
Invoke-RestMethod http://127.0.0.1:8765/api/health
```
Expected fields: status `ok`, mode `simulated`, framework `fastapi` (version reflects the installed application).

## Troubleshooting
| Symptom | Check |
|---|---|
| Address already in use | Identify the existing process or choose `--port 8766` |
| Page cannot connect | Confirm the process is running and the browser is on the same computer |
| Port reachable but 403 | Use localhost or 127.0.0.1 with the actual port; other Host values are rejected |
| POST returns 415 | Send `Content-Type: application/json` |
| POST returns 400 | Use a documented scenario, a string ticket under 4001 characters, and no extra fields |
| History appears empty | Confirm you are running from the intended project copy and its data directory |
| File locking on Windows | Stop all app processes before backup or database replacement |

## Phone workflow
The interface adapts to a phone-sized viewport. This does not publish the server to your phone. Use your existing authenticated remote connection to control the computer, or send project instructions through the remote session already in use. A direct phone browser connection needs a separately designed, authenticated access layer; it is not enabled here.

## Dependencies and resources
FastAPI and Uvicorn run inside the project virtual environment; see ../setup.md for dependency installation. No model runtime starts with this application; the RTX 2070 is not needed for fixture mode. The dashboard uses only local endpoints. Local-lab mode briefly starts its own loopback fixture service. The optional model adapter contacts only 127.0.0.1 and requires explicit flags; ordinary app startup never starts or queries a model. Static assets use system fonts and load locally.
