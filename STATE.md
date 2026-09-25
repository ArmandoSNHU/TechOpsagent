# State
Author: Armando Gomez

## 2026-09-24 — release 0.1 implemented and verified
The approved first workflow is implemented as a deterministic, synthetic fixture demo. No model was installed or started. No remote services were modified. Documentation and interface use Armando Gomez attribution.

Verification: `python -m unittest discover -s tests -v` → `Ran 23 tests in 0.838s`, `OK`. JavaScript syntax check exited 0. Three example reports exported. Browser exercised all scenarios, report response, persisted history, and 390 px mobile layout without horizontal overflow. Actual screenshots are in docs/screenshots; details in docs/VALIDATION.md.

During validation a hidden preview server was started on 127.0.0.1:8765 (process 27496 at that time). Verify current process identity before stopping it; this is historical startup information, not proof it is still running.

## 2026-09-24 — FastAPI environment installed
User authorized FastAPI installation. Created `.venv`, installed FastAPI 0.141.1 and Uvicorn 0.53.0, and pinned the complete dependency set in requirements.txt. `pip check` returned `No broken requirements found.` FastAPI import and OpenAPI schema generation passed. Tests under the virtual environment returned `Ran 23 tests in 0.857s`, `OK`. The existing server has not been migrated to FastAPI.

## 2026-09-24 — focused Chrome screenshot
Captured the saved dependency investigation directly from Chrome as docs/screenshots/investigation-snippet.png and added it to the progress gallery. PNG signature and saved bytes verified. No application code changed; previous 23-test result remains the latest test run.

## 2026-09-24 — working through the task checklist
Created Tech Ops Agent.md. T01 passed: 23 tests OK and pip check clean. T02 passed: 28 tests OK against FastAPI/Uvicorn. T03 and T04 complete: setup verified, server restarted, browser investigation/report/history/mobile checks passed. T05 complete: 34 tests OK. T06 complete: 46 tests OK and browser live-lab, imported-log, report and mobile checks passed. Current task: T07 offline local-model adapter and dry-run support. User requested sequential execution with verification before advancing.

## 2026-09-24 — tasks T01–T07 verified
Task checklist: Tech Ops Agent.md. Reproducible commands: setup.md. FastAPI migration, controlled local probes, structured JSONL analysis, responsive UI modes, and offline AI preview are implemented. Latest full suite: `Ran 57 tests in 1.509s`, `OK`. Pip check: `No broken requirements found.` Actual CLI dry run passed after the tested Windows encoding correction. Detailed evidence is in docs/VALIDATION.md.

## 2026-09-24 — T08 working
User explicitly approved inspection and testing of an installed local model, including runtime startup if needed, with no downloads. Checking inventory and GPU capacity before scenario evaluation.

## 2026-09-24 — T08 complete with documented limitations
User approved installed-local-model testing and runtime startup, no downloads. Ollama started via its installed launcher. qwen2.5-coder:7b timed out at 30 seconds despite fitting sampled GPU memory. llama3.2:3b Q4_K_M was selected for the prototype. Real output failures led to schema constraints and clearer instructions; regression tests preceded fixes.

Final live evaluation: six format/citation passes, 4.77–5.49 seconds each, 3432 MiB peak sampled total GPU use. Review flagged an unsupported application-configuration suggestion in the timeout summary. Results are draft explanations requiring review, not authoritative diagnoses. Full report and synthetic outputs: docs/MODEL-EVALUATION.md and docs/local-model-evaluation.json.

Latest suite: `Ran 60 tests in 1.591s`, `OK`. No model was downloaded. Model requests specify keep_alive 0. Final ollama ps showed no loaded models; GPU memory returned to 893 MiB used / 7097 MiB free. Web UI remains rule-based; model inference is opt-in through CLI/adapter.

## 2026-09-24 — T09 working
User granted full execution permissions and requested no routine approval prompts. Discovered public repository ArmandoSNHU/TechOpsagent through the authenticated GitHub CLI. No local listeners on ports 3000/3100 were found. Building read-only connectors with offline fixtures first. Existing no-model-download preference remains in force.

## 2026-09-24 - T09 verified
Read-only GitHub/Grafana/Loki connectors, configuration, CLI previews, dashboard controls, and instructions are implemented. GitHub returned zero open issues in CLI and browser. Grafana/Loki have fixture validation only; URLs are not configured. Latest suite: `Ran 77 tests in 1.599s`, `OK`. JavaScript syntax check exited 0. Actual Chrome snippet: docs/screenshots/integrations-snippet.png.

Updated preview launched on 127.0.0.1:8766 (launcher PID 14492 at launch) because automatic approval review blocked stopping the prior preview. Port 8765 may serve older code. Verify process identities before shutdown.

## 2026-09-24 - pre-publication privacy review
Inspected the 61 Git-eligible files, including six screenshots and image metadata. Pattern scan found no recognizable live API keys/private keys; credential-like values reviewed in tests are synthetic fixtures. No commits or tracked files exist yet. Ignore probes confirmed .env variants, virtual environment, runtime database, raw evaluation output, and logs are excluded. Publishable content includes intended Armando Gomez attribution, public GitHub identity/repository, local project paths, and GPU/model details. Screenshot review showed demo/local-lab evidence, not real customer records; no EXIF/GPS fields were present. This is a bounded review, not a guarantee against every secret format. Recheck the staged diff before eventual publication. No push performed.

## 2026-09-24 - initial publication preparation
User supplied the public repository URL following the privacy review and prior full-permissions instruction. Connected origin to ArmandoSNHU/TechOpsagent; remote was empty. Re-ran suite: `Ran 77 tests in 1.580s`, `OK`; pip check: `No broken requirements found.` Repository-local author email uses GitHub no-reply to avoid publishing the personal email from global Git configuration. Preparing the reviewed prototype for initial publication; T10/T11 remain future work.

## 2026-09-24 - initial prototype published
Initial commit 5f2053b successfully pushed to origin/main. Staged privacy review covered 61 files with zero blocked findings. GitHub no-reply commit email used. Documentation and screenshots are published; this is a source prototype publication, not a hosted service or tagged release.

## 2026-09-24 - privacy hardening working
Moving operator configuration into ignored .env, adding local setup prompts and publication guards. Rechecking published history; no live keys found so far.

## 2026-09-24 - privacy hardening verified
Private integration settings now load from ignored .env with process-environment precedence. Blank .env.example plus hidden-token setup CLI supports each user's own accounts. Public config defaults are empty. Local repository configuration was preserved without copying/creating any API key. No API key or customer data found in the published history audit; prior attribution/public repository references are not credentials and history was not rewritten.

Verified `Ran 93 tests in 2.357s`, `OK`; pip check clean, JavaScript syntax and documentation links passed. Clean-profile Chrome preview on 8767 showed disabled integrations; screenshot saved. Pre-push checks and CI cover common credential formats, sensitive artifacts, and removed historical files, with documented limitations. Hook enabled locally. The .env is plaintext local storage, protected from Git and HTTP serving; it is not a secrets vault.

## 2026-09-24 - integration wiring working
User requested live Grafana/Loki and ServiceNow wiring. Starting installed Docker for a loopback-only synthetic observability lab. ServiceNow instance information pending; implement read-only intake and offline draft preview without remote writes.

## 2026-09-24 - observability wired; ServiceNow live connection pending
Grafana OSS 13.2.2 and Loki 3.7.8 official native Windows archives installed under ignored data/observability after checksum verification. Docker Desktop failed startup with an inference-manager socket error; its installation/settings were not repaired or removed. Local lab launcher provisions localhost-only listeners, Loki source, synthetic dashboard, and a random Grafana admin password only in ignored .env. Anonymous Grafana access is Viewer-only for synthetic local data.

Loki /ready 200, synthetic push 204, live read three observations. Grafana health 200/database ok; datasource and dashboard verified via API and Chrome. Screenshot: docs/screenshots/grafana-loki-snippet.png. Live Loki analysis route handler produced an investigation and ServiceNow preview handler produced a draft without sending. ServiceNow requires user-supplied instance URL and locally entered credentials; no live call or remote write was made.

Full suite: `Ran 104 tests in 2.731s`, `OK`. Pip check clean; JS syntax and doc links passed. ServiceNow supports OAuth bearer or HTTPS basic authentication, fixed incident fields, bounded pages, and draft preview. CLI and dashboard controls added. Automatic approval review blocked new app-preview launch (8768), reason blocked by policy; no workaround launch attempted. Existing app previews may serve stale Python and need manual restart before new UI validation. Grafana running process 31180 and Loki 13596 are historical identities only; verify before shutdown.

## 2026-09-24 - setup improvements working
Improving the existing setup path: one PowerShell entry point, private per-service configuration editing, offline/loopback diagnostics, readiness checks, and stale-preview detection. No automatic model downloads, remote writes, or process termination.

## 2026-09-24 - setup improvements verified
One Windows entry point now supports install, private per-service configuration editing, offline/live diagnostics, tests, native lab install/start/seed, privacy-hook enablement, and foreground app startup. Existing settings are preserved; hidden entry and atomic snapshot-checked updates prevent accidental overwrite. Diagnostics disclose only statuses, never private URLs or secrets. App health exposes a startup public-source fingerprint; it detects stale source but configuration changes still require restart.

Verification: `Ran 120 tests in 7.952s`, `OK`; pip check clean, doc links and diff check passed. Actual clean Windows bootstrap in an isolated path containing spaces exited 0 and reported READY with no .env and no accounts configured. Existing Grafana/Loki were reused and verified HEALTHY. Existing app on 8766 correctly reported stale; occupied-port run refused to launch or kill anything. No new persistent preview/model was started.

## Restart Point
T14 local verification: `Ran 124 tests in 4.846s`, `OK`; four new artifact tests cover isolation, matching fixtures/reports, deterministic output, and refusal to merge existing directories. Chrome desktop/mobile checks passed for three cases and report URLs. Pages configured for Actions; deployment pending this commit. No operator configuration is read by the builder.

Current task: T14 working. User explicitly authorized a clickable GitHub Pages deployment. Building a separate static, synthetic-only demo with an allowlisted artifact; no backend services or credentials are published.

1. Read Git status and reproduce 120 tests using `.\.venv\Scripts\python.exe -m unittest discover -s tests`.
2. Local Grafana http://127.0.0.1:3000/d/techops-local-lab and Loki http://127.0.0.1:3100/ready were verified. Check live health before reuse. Run tools.seed_loki --send-local for fresh synthetic events. See docs/INTEGRATIONS.md for install/start commands and hidden local credentials.
3. ServiceNow adapter/draft implementation is done; live validation is blocked on the developer-instance URL and credentials entered only in local .env. Do not paste secrets into chat or tracked docs. T11 authenticated direct phone access remains outstanding.
4. Preferred setup: setup.ps1 -Check, -Configure -Service name, -StartLab, -Test, and foreground -Run. Use -Check -Live to identify stale previews. Older 8765/8766/8767 processes may serve old code; verify identity before manual shutdown. A fresh server test verifies build_id. No new persistent preview was launched during setup improvement.
5. User granted full permissions/no routine prompts; no-model-download restriction persists. No model downloads or remote incident writes occurred.
6. Run tools.publish_guard --staged and --history before every push. Keep .env, downloaded binaries, generated runtime configs, databases and logs excluded. Track only synthetic examples/screenshots and blank .env.example.
