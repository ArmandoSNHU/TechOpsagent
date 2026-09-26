# TechOpsagent design
Author: Armando Gomez
Date: 2026-09-24

## Goal and acceptance
Support a complete local investigation: select a controlled incident or import structured logs, collect evidence, rank suspected causes, save the result, and download a report. Verify each task before advancing; use Tech Ops Agent.md for acceptance checks and STATE.md for the current handoff.

## Architecture
FastAPI/Uvicorn binds to loopback and serves the static dashboard. Strict request models and ASGI middleware preserve local Host/Origin protections, request size limits, and a body-read deadline. SQLite stores records with explicit connection cleanup. The lab module starts a temporary loopback fault service, performs bounded HTTP reads, and shuts it down. The evidence module validates observations and ranks supported hypotheses. The AI module builds offline prompts and gates all service access/inference behind explicit flags. Dependencies are pinned in requirements.txt.

## Data flow
Evidence source → observations → rule-based analysis → local persistence → dashboard/report. Saved-fixture mode retains the original curated diagnosis for comparison. Imported JSONL content is never interpreted as a command or network target. Model explanations are separate, unverified outputs; they cannot alter collected evidence or execute remediation.

## Boundaries
Local fault-lab measurements are real HTTP observations of deliberately generated failures, not production diagnostics. Imported logs are unverified. Causes remain suspected; rule scores are not probabilities. Only common secret patterns are redacted; synthetic data is required for this portfolio. The installed llama3.2:3b model was evaluated after explicit approval; no model downloads occurred. See MODEL-EVALUATION.md for measured results and limitations.

## Validation
Tests cover API routes and generated schema, strict inputs, body limits including streamed requests, persistence, report truthfulness, observed failure statuses, timeout and redirect rejection, evidence ranking and ambiguity, log limits and nonfinite values, offline AI default, citation membership, cloud-model exclusion, and Windows CLI encoding. Chrome verifies the live-lab and imported-log workflows, exports, history, and mobile layout.

## Remaining integrations
Further model startup or downloads remain subject to the recorded user authorization and project approval rules. GitHub Issues, Grafana/Loki, ServiceNow, and authenticated remote phone access remain separate checklist deliverables. No automatic remediation is implemented.
## 2026-09-25 toolkit extension
The home route now serves category-based diagnostic navigation. `/incidents` preserves the original investigation workspace. `tool_catalog.py` defines public descriptions and explicit synthetic examples. `toolkit.py` runs fixed, bounded Windows read-only commands; `toolkit_routes.py` validates an enum and serializes collection with a nonblocking lock. The UI receives results only on demand and keeps up to 50 snapshots in tab memory; no diagnostic data is written to SQLite. Reports are explicit JSON downloads. Unsupported systems, failures, and empty results remain distinguishable from usable observations.

Shared toolkit HTML/CSS/JS live under `techops/static/toolkit/`. Server-rendered HTML explicitly selects local mode; the Pages builder always copies demo-mode HTML with allowlisted synthetic JSON. It does not derive mode from the hostname or fall back to demo readings after local failures. The original public incident demo is published as `incidents.html`. See TOOLKIT-PLAN.md and TOOL-GUIDE.md for accepted scope and controls.

## DNS toolkit extension
`techops/dns.py` validates a hostname and passes JSON through stdin to a fixed Windows DNS-only script. The existing toolkit API lock and loopback/Origin boundary apply. Unlike configuration snapshots, this explicit Run action may contact the configured DNS resolver. Output is schema-checked, bounded to 64 records and labeled without inferring application health. The shared UI records the target with each result; Pages uses only fixed synthetic success/failure fixtures. No new runtime dependency, model or API route is required.

## Guided operations layer
`investigation.js` contains pure runbooks, evidence assessment and Markdown rendering, tested with Node. The toolkit owns one current investigation and a latest-result map represented as a bounded array of its two or three relevant tools. Starting a new symptom clears that scope; existing tool history is independent. Context is never sent to the backend. A failed transport attempt replaces earlier evidence with unavailable. Only same-mode readings qualify, with a ten-minute local freshness heuristic. No background collection, model, persisted incident lifecycle or automatic action is added. The public builder now allowlists 14 files including this shared script.
