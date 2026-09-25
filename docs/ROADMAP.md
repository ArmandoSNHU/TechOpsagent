# Roadmap
Author: Armando Gomez

The executable task checklist is [Tech Ops Agent.md](../Tech%20Ops%20Agent.md). Current handoff and verification counts live in STATE.md.

## Implemented foundation
FastAPI backend, responsive dashboard, fixture investigations, controlled local fault probes, structured JSONL intake, evidence-based rule ranking, persisted history, draft RCA export, and an offline AI preview with an approval-gated local-model adapter.

## Completed: initial local AI evaluation
Approved installed-model testing is documented in MODEL-EVALUATION.md. The small model met the six-case format/citation checks, but review found unsupported speculation. Keep inference opt-in and outputs subject to review.

## Next: integration fixtures and connection details
T09 requires the intended GitHub repository and Grafana/Loki connection scope before live integration. Build fixture tests first; no remote writes are authorized.

## Enterprise integrations
Build GitHub Issues intake and Grafana/Loki evidence adapters with fixture tests and dry-run behavior first. ServiceNow is optional. Remote writes require an explicit preview and authorization.

## Authenticated phone access
Design authentication, transport protection, permissions, and audit events before exposing the app beyond loopback. Responsive layout is already implemented; direct remote access is not.

## Publication
Review the repository URL, license choice, tests, screenshots, and secret exclusions before the user-authorized GitHub release.
