# Changelog
Author: Armando Gomez

## 0.3.0 — 2026-09-24
- Migrated the server to FastAPI/Uvicorn with generated OpenAPI and bounded streamed bodies.
- Added controlled local HTTP faults, bounded probes, JSONL intake, and ranked evidence-based triage.
- Added live-lab and imported-log dashboard modes, evidence citations, and accurate report provenance.
- Added an offline AI prompt preview and explicit local-model approval gates. Subsequent approved testing of an installed 3B model is documented in docs/MODEL-EVALUATION.md.
- Added the sequential task checklist and setup guide; full verification reached 57 tests OK.

## 0.1.0 — 2026-09-24
- Created a zero-install local support-operations demo.
- Added three synthetic incident scenarios, evidence displays, suspected-cause explanations, and Markdown draft RCA export.
- Added SQLite history, input validation, secret-pattern redaction, and local browser protections.
- Added responsive dashboard, desktop/mobile screenshots, operator and API documentation, and 23 automated tests.
- Documented future live probes, log ingestion, local AI, and enterprise integrations explicitly as planned work.

## Local evaluation follow-up — 2026-09-24
- Added constrained output schemas and clarified raw JSON/evidence instructions after real model validation failures.
- Added opt-in six-case evaluation runner and measured results.
- Verification reached 60 tests OK; model outputs remain subject to review.
