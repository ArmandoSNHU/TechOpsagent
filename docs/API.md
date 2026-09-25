# HTTP API
Author: Armando Gomez

Base URL: `http://127.0.0.1:8765`. JSON uses UTF-8. Bind address is loopback only.

| Route | Result |
|---|---|
| GET /api/integrations | 200: configuration status, no credentials |
| GET /api/integrations/github/preview | 200: offline GET preview |
| POST /api/integrations/github/read | 200: read-only ticket page; optional page integer |
| GET /api/integrations/grafana/health | 200: configured Grafana health |
| POST /api/integrations/loki/analyze | 201: saved log investigation; service and minutes fields |
| GET /api/health | 200: status, mode, version, framework |
| GET /openapi.json | 200: generated OpenAPI schema |
| GET /api/scenarios | 200: three scenario summaries |
| GET /api/incidents | 200: latest 100 complete records, newest first |
| GET /api/incidents/{id} | 200: record; 404 if absent |
| GET /api/incidents/{id}/ai-preview | 200: offline model prompt preview; 404 if absent |
| GET /api/incidents/{id}/report | 200: downloadable Markdown; 404 if absent |
| POST /api/investigate | 201: newly persisted fixture investigation |
| POST /api/lab/investigate | 201: observed loopback fault investigation |
| POST /api/analyze | 201: structured JSONL analysis |

## Create an investigation
```powershell
$body = @{scenario='api_error'; ticket='Checkout fails after deployment.'} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8765/api/investigate -Method Post -ContentType 'application/json' -Body $body
```

Valid scenarios: `api_error`, `dependency_timeout`, `invalid_credential`. Optional ticket must be a string of at most 4000 characters. Request body limit: 16384 bytes. Extra fields are rejected.

Returned fields: id (UUID hex), scenario, created_at (UTC ISO timestamp), title, service, severity, description, cause, impact, evidence (source/signal/detail/state), next_steps, prevention, ticket (redacted), status (`suspected`), analysis_mode (`deterministic`), environment (`simulated`), author.

## Errors
Errors are JSON objects with `error`. 400: malformed input; 403: invalid Host or cross-origin write; 404: missing route/record; 408: request-body timeout; 413: body size; 415: content type; 503: local storage unavailable. Browser assets are served only from explicit paths. No CORS permissions are emitted.

## Boundaries
No authentication is provided; this is a single-user loopback demo. Do not expose the port publicly or bind to a LAN interface. For phone access, use your existing authenticated remote-desktop connection. Mobile layout screenshots do not imply remote access has been configured.

## FastAPI schema
`GET /openapi.json` returns the generated schema, including the scenario enum and the 4000-character ticket constraint. Interactive documentation pages are disabled to keep all app assets local. The health endpoint reports `framework: fastapi`.

The lab endpoint accepts the same scenario/ticket payload as fixture investigation. The analyze endpoint accepts `log_text` and optional `ticket`; see LOGS.md. Its analysis_mode is rule_based. Both save the resulting record locally. Rule scores rank supporting signals; they are not probabilities.

Observed analysis records additionally include `certainty` and `hypotheses` (cause, scenario, rule score, evidence_ids). Evidence includes IDs, optional observation timestamps, and measured latency. The default P3 on observed records is a provisional triage label; assess actual impact manually. The legacy health `mode: simulated` denotes the controlled demo environment; per-record `environment` distinguishes simulated, local_fault_lab, and imported_logs.

Integration routes return 409 for a missing configured service, 502 for sanitized upstream failures, and 404 for an empty Loki window. Remote targets come only from local .env settings or the process environment. GitHub reads one page of up to 20 items and excludes pull requests. Tokens remain server-side and are never returned.
