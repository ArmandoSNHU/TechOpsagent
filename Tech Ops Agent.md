# Tech Ops Agent — Task checklist
Author: Armando Gomez

## Goal
Build a tested local support-operations agent, progressing from a reproducible incident demo to observed evidence and optional local AI. Current implementation scope and architecture are in docs/DESIGN.md.

## Working loop
1. Select the first unchecked task whose prerequisites are complete.
2. Mark it working in STATE.md.
3. For code changes, write a meaningful regression test and observe its failure.
4. Implement the task; run its targeted tests and then the complete suite.
5. Restart the project service before browser validation.
6. Record actual commands, outputs, and screenshots in docs/VALIDATION.md.
7. Check the task only after its acceptance check passes, update STATE.md, then move to the next task.

Do not advance past a failing prerequisite. Task completion requires source, tests, and documentation to agree. STATE.md remains the only current-session status and restart file.

## Milestone 1 — verified FastAPI foundation
- [x] T01: Verify the installed environment and existing 23-test baseline. Acceptance: pip check is clean and the full suite passes under .venv.
- [x] T02: Replace the standard-library HTTP server with FastAPI/Uvicorn. Files: techops/server.py, techops/security.py, tests/test_api.py, tests/support.py. Preserve all six business API routes and their response contract. Add GET /openapi.json with an explicit request schema. Acceptance: real loopback HTTP tests pass for all routes, input errors, Host/Origin checks, body limits, report download, persistence, and static assets.
- [x] T03: Create setup.md with installation, startup, health check, tests, troubleshooting, and safe shutdown commands. Update README.md, docs/API.md, docs/DESIGN.md, and operational guidance to match FastAPI. Acceptance: documented links resolve and setup commands work in the installed environment.
- [x] T04: Restart the preview, exercise the FastAPI-backed dashboard, download a report, check mobile layout, capture Chrome screenshots/snippets, and record verification. Acceptance: live health identifies FastAPI, report returns 200, history reloads, mobile has no horizontal overflow, and screenshots exist.

## Review focus for T02
- Oversized streamed bodies must be rejected even without Content-Length.
- Wrong types and extra request fields must preserve the 400 error contract.
- Host and Origin protections must remain in effect after migration.
- A missing database record must return 404 rather than a server error.
- Documentation must enumerate the actual FastAPI route surface, including the schema endpoint.

## Following milestones and acceptance checks
These are separate deliverables, not claims of completed functionality.
- [x] T05: Controlled local fault service and bounded HTTP/DNS probes. Acceptance: tests produce real controlled 500/504/401 observations and verify timeout, redirect rejection, and target allowlisting.
- [x] T06: Structured log intake and ranked diagnoses from observed evidence. Acceptance: known failures, unknown evidence, contradictory evidence, and malicious log text have regression coverage; causes cite evidence.
- [x] T07: Disabled-by-default local-model adapter, capability probe, and prompt dry run. Acceptance: offline tests prove no runtime starts or model downloads occur and evidence identifiers are preserved.
- [x] T08: Approved local-model execution and evaluation. Requires explicit model/runtime approval. Acceptance: measured results on scenario fixtures, with unsupported claims flagged.
- [x] T09: GitHub Issues intake and Grafana/Loki adapters. Acceptance: fixture tests pass before authorized live connections; remote writes stay preview-only until approved.
- [x] T10: ServiceNow adapter with bounded read-only intake and offline incident payload preview. Verified with fixtures and local draft review; live developer-instance connection remains pending instance URL and local credentials. Remote writes are not implemented.
- [ ] T11: Authenticated phone access. Acceptance: unauthorized clients are rejected and no unauthenticated public endpoint is exposed.
- [x] T12: GitHub release. Requires repository URL and publication authorization. Acceptance: tests pass, secrets/runtime data are excluded, documentation and screenshots match shipped behavior.

## Constraints
Windows/PowerShell, Armando Gomez attribution, local-first execution, no unapproved model startup/download, no paid API calls or remote changes without approval. Preserve existing data and screenshots. Git publication is a separate approval.

## Verification ledger
| Tasks | Evidence |
|---|---|
| T01 | 23 tests OK; pip check clean |
| T02 | 28 tests OK; generated schema and real Uvicorn HTTP coverage |
| T03 | setup commands exercised; documentation links PASS |
| T04 | restarted FastAPI preview; report 200; history reopened; mobile width 390/390 |
| T05 | 34 tests OK including observed 500/504/401, timeout, redirects, and path rejection |
| T06 | 46 tests OK; Chrome live-lab and imported-log workflows verified |
| T07 | 57 tests OK; actual offline CLI dry run passed after Windows encoding fix |
| T08 | 60 tests OK; six live cases passed format/citation checks; one unsupported suggestion flagged |
| T09 | 77 tests OK; live GitHub CLI and browser read returned zero issues; Grafana/Loki fixture-tested |

See docs/VALIDATION.md for exact commands and output. T08 was explicitly approved and evaluated with no model downloads. See docs/MODEL-EVALUATION.md for timings, memory, rejected attempts, and unsupported-output findings. T11 remains unchecked. T10 live instance validation remains pending. T12 initial source publication is complete; no tagged release created. Grafana/Loki are fixture-tested and remain unconfigured.
