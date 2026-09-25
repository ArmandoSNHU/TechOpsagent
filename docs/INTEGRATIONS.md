# Read-only integrations
Author: Armando Gomez

## Configuration
Edit config/integrations.json and restart the app. github_repository uses owner/name. grafana_url and loki_url remain null until a service is available. URLs must use HTTPS except for loopback HTTP. Never embed credentials in URLs or commit tokens. Optional process environment names: GITHUB_TOKEN, GRAFANA_TOKEN, LOKI_TOKEN. Values are never returned by the status API. .env files are not automatically loaded.

## GitHub tickets
The configured repository is ArmandoSNHU/TechOpsagent, discovered through the signed-in GitHub CLI. Read GitHub tickets loads one page of up to 20 open records, excludes pull requests, redacts common secrets, and caps ticket context. Use as ticket context copies text locally; it does not claim that the ticket was diagnosed. Independently select or import evidence. The adapter never follows URLs from ticket bodies.

```powershell
.\.venv\Scripts\python.exe -m techops.connectors github --repository ArmandoSNHU/TechOpsagent
.\.venv\Scripts\python.exe -m techops.connectors github --repository ArmandoSNHU/TechOpsagent --read
```
First command previews the request offline; --read makes the request. Pages are explicit and bounded; no automatic unbounded pagination occurs. Remote comments, issue creation, and issue edits are not implemented. The live check succeeded with an empty issue list.

## Grafana and Loki
Grafana uses GET /api/health. Loki uses GET /loki/api/v1/query_range with a fixed service_name selector, a maximum one-hour window, and at most 50 log observations. No arbitrary LogQL is accepted from tickets or the browser. Structured lines with message/status fields are normalized; other lines remain untrusted text. Results use the existing evidence analyzer and local report store.

```powershell
.\.venv\Scripts\python.exe -m techops.connectors grafana --url http://127.0.0.1:3000
.\.venv\Scripts\python.exe -m techops.connectors loki --url http://127.0.0.1:3100 --label checkout
```
These are offline previews; add --read only for a configured service. No listener was found on local ports 3000 or 3100 during setup. Grafana/Loki parsing and error paths are fixture-tested; a real deployment has not been connected.

## Transport limits
Only GET requests, no redirect following, ten-second socket timeout, 1 MiB response cap, no automatic retry, and sanitized upstream errors. A 403 may indicate forbidden access or rate limiting; 429 reports rate limiting explicitly. Missing configured services return 409 locally. This is a single-user local tool; do not expose it beyond the authenticated access design.

## Protocol references
- [GitHub issues API](https://docs.github.com/en/rest/issues/issues)
- [GitHub pagination](https://docs.github.com/en/rest/using-the-rest-api/using-pagination-in-the-rest-api)
- [Loki API](https://grafana.com/docs/loki/latest/reference/loki-http-api/)
- [Grafana API](https://grafana.com/docs/grafana/latest/developer-resources/api-reference/http-api/)
