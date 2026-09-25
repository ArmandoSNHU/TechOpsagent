# Structured evidence intake
Author: Armando Gomez

Paste JSONL (one JSON object per line) into the Imported logs mode, or send it as log_text to POST /api/analyze. Maximum: 50 nonempty lines and 12000 UTF-8 bytes, within the API request limit of 16384 bytes. No file paths, URLs, commands, or remote fetches are accepted as actions.

```json
{"kind":"http","source":"checkout","status":500,"detail":"KeyError: TAX_REGION"}
{"kind":"http","source":"inventory","status":200,"detail":"healthy"}
```

Required fields: kind, source (1–120 characters), detail (up to 2000 characters). Optional: status (integer 100–599 or null), observed_at (up to 80 characters), elapsed_ms (nonnegative number). Kinds: http, log, dns, timeout, probe_error, redirect_rejected. Extra fields and coercion of string status codes are rejected.

The rule engine assigns two points to matching HTTP status or timeout and two to a matching error phrase. Results cite evidence IDs. Multiple supported causes are explicitly reported as competing hypotheses; unknown evidence remains insufficient. Scores are not probabilities. Imported logs are unverified data and may contain misleading statements. Customer impact and severity require human assessment.

## Local fault lab
Live local lab mode starts a disposable HTTP service on an OS-assigned loopback port. It observes one deliberately failing endpoint and a healthy endpoint, then shuts the fixture server down. Requests have a one-second timeout, a 64 KiB response cap, no retries, and no redirect following. Only fixed paths and 127.0.0.1 are probed; the API accepts no host or port from a caller. Local name resolution checks localhost only. This is measured lab evidence, not a production-system health check.
