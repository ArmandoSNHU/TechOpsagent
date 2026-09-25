# Read-only integrations
Author: Armando Gomez

## Configuration
Run `.\.venv\Scripts\python.exe -m techops.settings` to enter your own repository, optional service URLs, and optional tokens. Token prompts are hidden. This writes an ignored `.env` without contacting any service. Use `setup.ps1 -Configure -Service <name>` to edit an existing file privately. Alternatively copy `.env.example` to `.env` and edit locally. Restart the app after edits.

Settings: GITHUB_REPOSITORY (owner/name), GITHUB_TOKEN, GRAFANA_URL, GRAFANA_TOKEN, LOKI_URL, LOKI_TOKEN, SERVICENOW_URL, SERVICENOW_TOKEN, SERVICENOW_USERNAME, SERVICENOW_PASSWORD. GRAFANA_ADMIN_PASSWORD is used only by the optional local Grafana lab. Process environment values override `.env`, including an explicitly empty value. Values are literal: no interpolation, command execution, export syntax, or multiline values. URLs must use HTTPS except loopback HTTP; never put credentials in URLs. A fresh clone starts with all integrations disabled. The retained config/integrations.json is an empty reference, not runtime configuration. Tokens are never returned by the status API.

## GitHub tickets
Choose your own repository during local setup. Read GitHub tickets loads one page of up to 20 open records, excludes pull requests, redacts common secrets, and caps ticket context. Use as ticket context copies text locally; it does not claim that the ticket was diagnosed. Independently select or import evidence. The adapter never follows URLs from ticket bodies.

```powershell
.\.venv\Scripts\python.exe -m techops.connectors github --repository owner/repository
.\.venv\Scripts\python.exe -m techops.connectors github --repository owner/repository --read
```
First command previews the request offline; --read makes the request. Pages are explicit and bounded; no automatic unbounded pagination occurs. Remote comments, issue creation, and issue edits are not implemented. The live check succeeded with an empty issue list.

## Grafana and Loki
Grafana uses GET /api/health. Loki uses GET /loki/api/v1/query_range with a fixed service_name selector, a maximum one-hour window, and at most 50 log observations. No arbitrary LogQL is accepted from tickets or the browser. Structured lines with message/status fields are normalized; other lines remain untrusted text. Results use the existing evidence analyzer and local report store.

```powershell
.\.venv\Scripts\python.exe -m techops.connectors grafana --url http://127.0.0.1:3000
.\.venv\Scripts\python.exe -m techops.connectors loki --url http://127.0.0.1:3100 --label checkout
```
These are offline previews; add --read only for a configured service. The optional native Windows lab below supplies local Grafana and Loki. Feed synthetic events before testing the 15-minute query window.

## Transport limits
Only GET requests, no redirect following, ten-second socket timeout, 1 MiB response cap, no automatic retry, and sanitized upstream errors. A 403 may indicate forbidden access or rate limiting; 429 reports rate limiting explicitly. Missing configured services return 409 locally. This is a single-user local tool; do not expose it beyond the authenticated access design.

## Protocol references
- [GitHub issues API](https://docs.github.com/en/rest/issues/issues)
- [GitHub pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
- [Loki API](https://grafana.com/docs/loki/latest/reference/loki-http-api/)
- [Grafana API](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/)

## Native Windows observability lab
Author: Armando Gomez

Run from the repository root:
```powershell
.\.venv\Scripts\python.exe -m tools.local_lab
.\.venv\Scripts\python.exe -m tools.local_lab --install
.\.venv\Scripts\python.exe -m tools.local_lab --start
.\.venv\Scripts\python.exe -m tools.seed_loki
.\.venv\Scripts\python.exe -m tools.seed_loki --send-local
.\.venv\Scripts\python.exe -m techops.connectors grafana --read
.\.venv\Scripts\python.exe -m techops.connectors loki --label checkout --read
```
The first command previews the plan. Install explicitly downloads version-pinned official Grafana OSS 13.2.2 and Loki 3.7.8 Windows binaries and checks published SHA256 values before extraction. Everything downloaded/generated is inside ignored data/observability. Startup creates loopback-only configuration, provisions the Local Loki data source, and preserves existing settings. It refuses to replace different service URLs. It does not stop an existing listener. Occupied ports must identify as the expected service; startup waits for healthy responses. Existing processes retain their original configuration until restarted. First-run Grafana database migrations can take several minutes.

Grafana: http://127.0.0.1:3000. Loki readiness: http://127.0.0.1:3100/ready. Anonymous Grafana access is Viewer-only for this synthetic localhost lab. Admin username is techops; the generated password stays in GRAFANA_ADMIN_PASSWORD in ignored .env. Do not paste it into issues, chat, screenshots, or shell commands. Local users with filesystem access can read it. Do not expose these services to LAN/public interfaces. Usage reporting and update checks are disabled.

The seeder has an offline preview and an explicit --send-local switch. It sends exactly three generated events only to 127.0.0.1:3100, never forwards real machine logs, and cannot choose a remote target. Re-seed when events age outside the query window. Choose service checkout in the dashboard. Restart TechOpsagent after updating its .env so the connected-source buttons use the new configuration.

To stop, identify the processes by their executable paths under this project's data/observability directory and stop only those verified process IDs. Logs and databases stay in ignored data. Do not use broad process-name termination or delete database directories while running.

## ServiceNow
Use a developer/test instance, not production. Edit these names in ignored .env and restart TechOpsagent:
- SERVICENOW_URL: HTTPS instance origin, without path or embedded credentials.
- Either SERVICENOW_TOKEN for an existing OAuth bearer access token, or SERVICENOW_USERNAME plus SERVICENOW_PASSWORD for an account permitted to read incidents. Do not configure both methods.

The initial setup command prompts with hidden token/password entry. For an existing .env, use `setup.ps1 -Configure -Service servicenow`; Enter keeps a value and - clears it. Never send credentials in chat. The connector does not request/refresh OAuth tokens or change instance ACLs. Use an account restricted to the records needed for testing.

```powershell
.\.venv\Scripts\python.exe -m techops.connectors servicenow
.\.venv\Scripts\python.exe -m techops.connectors servicenow --read
```
Default is a request preview. --read queries at most 20 active incidents, with fixed fields and bounded pagination. Caller/user references are excluded. Description text can still contain personal information; this is why developer instances and synthetic records are required. Text is untrusted context and receives best-effort secret redaction. It is not automatically diagnosed.

After a local investigation, Preview ServiceNow draft builds only short_description and description from the evidence report. It does not send anything or set caller, assignment, impact, or urgency. No remote create/update implementation exists. Review the draft before any manual submission. ServiceNow live validation remains pending until an instance and local authentication are supplied.

References: [ServiceNow Table API](https://www.servicenow.com/docs/r/api-reference/rest-apis/c_TableAPI.html), [Grafana Windows downloads](https://grafana.com/grafana/download/13.2.2?edition=oss&platform=windows), [Loki release assets](https://github.com/grafana/loki/releases/tag/v3.7.8).
