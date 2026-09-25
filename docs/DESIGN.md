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
