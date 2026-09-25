# Validation record
Author: Armando Gomez
Date: 2026-09-24

## Automated verification
Command: `python -m unittest discover -s tests -v`

```text
Ran 23 tests in 0.838s

OK
```

Coverage includes three expected diagnoses, unknown scenarios, untrusted ticket text, common credential redaction, truthful analysis-mode labeling, report sections, persisted/reopened records, parameterized lookups, API input validation, body size, content type, Host and Origin rejection, missing records, static paths, security headers, and documented API routes.

`node --check techops/static/app.js` exited 0 with no output.
`python -m techops.demo` returned `Exported 3 synthetic incident reports to examples/`.

## Failure found and corrected
The initial engine test run failed with `ModuleNotFoundError: No module named 'techops.engine'` before implementation. The expanded suite then exposed three Windows cleanup errors due to unclosed SQLite connections. A context manager now commits/rolls back and explicitly closes each connection. The full suite passed after the fix.

## Browser validation
- Opened the running loopback dashboard.
- Ran all three scenarios through the scenario controls and investigation button.
- Confirmed three saved history records.
- Fetched the browser's report URL: HTTP 200, attachment filename incident-report.md, Armando Gomez attribution present.
- Reopened the credential investigation from history after mobile emulation refreshed the page; observed “Credential rejected”.
- Checked phone layout at 390 px: document width 390 px, no horizontal overflow.
- Captured desktop (1440 px) and mobile (390 px) screenshots from the live app.
- Browser console check returned `<no console messages found>` for errors/warnings after mobile reload.

## Limits of this evidence
Browser checks were performed through automated browser tools, not a physical phone. No real model, remote system, enterprise account, or live service failure was tested. Screenshots show synthetic data. API tests use a temporary database and local loopback server.

## Sequential task execution — 2026-09-24
T01 baseline: `Ran 23 tests in 0.695s`, `OK`; pip check clean.
T02 migration: `Ran 28 tests in 0.607s`, `OK` against a real Uvicorn loopback server.
T05 fault lab: `Ran 34 tests in 0.970s`, `OK`.
T06 observed analysis/UI: `Ran 46 tests in 1.328s`, `OK`.
T07 AI adapter and Windows CLI fix:

```text
Ran 57 tests in 1.509s

OK
```

Commands: `.\.venv\Scripts\python.exe -m unittest discover -s tests -v`, `.\.venv\Scripts\python.exe -m techops.ai --dry-run --scenario api_error`, `.\.venv\Scripts\python.exe -m pip check`. Dry run returned dry_run true, inference_enabled false, E1/E2/E3; pip check returned `No broken requirements found.` JavaScript syntax check exited 0.

The new test modules first failed on missing implementations. The actual AI CLI then exposed a cp1252 UnicodeEncodeError; a subprocess regression reproduced the failure before JSON console output was changed to escaped ASCII. The regression and full suite passed afterward.

After restarting the preview, Chrome showed observed HTTP 500/200 and local DNS evidence. Imported JSONL produced Credential rejected, marked IMPORTED · UNVERIFIED; its report returned 200 and contained evidence citations and the unverified-data limitation. History reopened after mobile reload. Viewport and document width were both 390 px. Console errors/warnings: none. Capture: screenshots/live-evidence-snippet.png.

No live model request, runtime start, model download, cloud call, or enterprise integration was executed. AI transport tests use mocks; accepted citations are not proof of factual accuracy.

## T08 — approved local model evaluation, 2026-09-24
Full suite: `Ran 60 tests in 1.591s`, `OK`. Final live run: six format/citation passes, 4.77–5.49 seconds per case, peak sampled GPU use 3432 MiB. Model: installed llama3.2:3b Q4_K_M. No model downloads. One unsupported configuration suggestion in the timeout case is explicitly flagged in MODEL-EVALUATION.md. Earlier 7B timeout and rejected 3B outputs are retained in that report. New tests observed failure before adding output-schema constraints and the opt-in evaluation runner.

## 2026-09-24 - read-only integrations
Author: Armando Gomez

- `.\.venv\Scripts\python.exe -m unittest discover -s tests` returned `Ran 77 tests in 1.599s`, `OK`.
- `node --check techops/static/app.js` exited 0.
- CLI and dashboard read of ArmandoSNHU/TechOpsagent returned zero open issues. No remote changes.
- Grafana/Loki: bounded requests and fixture coverage; no configured URLs or local listeners on 3000/3100, so no live validation claimed.
- Updated preview started on 127.0.0.1:8766 after automatic approval review blocked stopping the existing preview. Port 8765 was left untouched.
- Chrome verified successful GitHub response, disabled unconfigured Grafana control, and desktop width 1269 at viewport 1284. Actual screenshot: screenshots/integrations-snippet.png. Console had one resource 404; no JavaScript exception reported.

## 2026-09-24 - private configuration and publication guard
- Full suite: `Ran 93 tests in 2.357s`, `OK`. Includes literal .env parsing, environment precedence, no-overwrite setup, hidden token prompts, unconfigured fresh install, token-free API status, HTTP 404 for private files, force-added private artifact detection, and detection of removed secrets in Git history.
- `pip check`: `No broken requirements found.` JavaScript syntax and Markdown links passed.
- Pre-change history audit: 63 file versions checked, zero findings after narrow classification of the pre-existing synthetic redaction fixture. Published screenshots were reviewed in the preceding privacy audit; no real keys/customer data were found.
- New process on loopback port 8767 uses an empty settings profile and disposable local database. Chrome confirmed all integrations disabled and local setup guidance shown. Actual screenshot: screenshots/private-setup-snippet.png. This process intentionally differs from the operator's local .env profile.
- Git hook enabled locally using core.hooksPath=.githooks. Workflow repeats checks on GitHub; manual image/content review remains required.

## 2026-09-24 - live observability and ServiceNow adapter
- `Ran 104 tests in 2.731s`, `OK`. Pip check: `No broken requirements found.` JavaScript syntax and documentation links passed.
- Docker Desktop startup failed in its inference-manager socket initialization. Native official Windows builds used instead; Grafana OSS 13.2.2 and Loki 3.7.8 archives passed their official SHA256 checks. No model download occurred.
- Loki readiness HTTP 200. Synthetic seeder dry-run checked, then --send-local returned HTTP 204 for three events. Live read returned three observations.
- Grafana /api/health HTTP 200, database ok, version 13.2.2. Data source uid techops-loki and dashboard uid techops-local-lab verified through local APIs. Chrome showed all three real ingested synthetic events; screenshot saved.
- The actual Loki route handler read the live service, saved an investigation, and returned cause Unhandled application exception with three observations. The actual ServiceNow preview handler produced a dry-run payload with short_description and description; remote_write false. ServiceNow transport/parsing/auth uses fixtures; no live instance has been configured.
- Grafana's first attempt failed because its database directory was missing. A failing regression test preceded the directory-creation fix; subsequent startup completed its first-run migrations.
- Automatic approval review rejected starting an updated TechOpsagent preview on port 8768 with reason blocked by policy. No fresh full-dashboard browser validation is claimed. Route HTTP tests use fresh disposable servers; live Grafana browser validation succeeded. Existing app previews may serve older Python code and must be restarted manually before testing new buttons.

## 2026-09-24 - guided setup and diagnostics
- `.\setup.ps1 -Test`: `Ran 120 tests in 7.952s`, `OK`. Coverage includes preserving unrelated credentials, explicit clearing, failed edits, concurrent edits, secret-free diagnostics, redirects, wrong listeners, stale fingerprints, fresh-server health, missing binaries, exited processes, and bounded readiness waits.
- `.\setup.ps1 -Check`: Core environment READY, configuration valid. Optional ServiceNow remains unconfigured. No values/private URLs displayed.
- `.\setup.ps1 -Check -Live -Port 8766`: intentionally exited 1, correctly reported the old app as stale and Grafana/Loki healthy. `.\setup.ps1 -Run -Port 8766` refused the occupied port before launching anything.
- `.\setup.ps1 -StartLab`: reused both existing local services, verified actual readiness, printed HEALTHY for both; no existing process terminated.
- Clean Windows installation in an isolated ignored folder with spaces: setup.ps1 -Install -Check exited 0, created a new .venv, reported READY, and left all integrations optional/unconfigured. No .env was created or operator credential copied. Bootstrap log retained only under ignored data.
- PowerShell help/missing-environment behavior exercised from an isolated folder. Pip check: No broken requirements found. Documentation links and git diff --check passed.
- No fresh long-running app preview was launched in this task. Fresh disposable HTTP tests validate the health fingerprint; existing stale previews remain available for deliberate manual shutdown/restart.
# 2026-09-24 — GitHub Pages demo, local validation

Author: Armando Gomez

The new artifact tests first failed with `ModuleNotFoundError: No module named 'tools.build_pages'`. After implementation, `Ran 4 tests in 0.158s`, `OK`. Full suite: `Ran 124 tests in 4.846s`, `OK`. `node --check site/app.js` and `git diff --cached --check` exited 0.

Chrome preview at loopback port 8770 used only the generated public artifact. All three cases selected/reset correctly, each rendered three observations, and each report returned 200 with the matching cause and draft limitation. Reset returned focus to Investigate. Desktop 1440px and mobile 390px had no horizontal overflow; mobile measured 390/390 for all cases. No console warnings/errors were found. A simulated fixture-fetch failure displayed the unavailable state. Live deployment verification and screenshots are recorded below when complete.
## Live Pages verification — 2026-09-24
Final suite after documentation changes: `Ran 124 tests in 8.078s`, `OK`. Staged privacy scan: 91 file versions, zero findings; history scan: 146 file versions, zero findings. Direct public requests for `.env`, `config/integrations.json`, `data/incidents.db`, and `techops/server.py` all returned 404.

Deployment [36083523427](https://github.com/ArmandoSNHU/TechOpsagent/actions/runs/36083523427) succeeded for b3815e1; companion Privacy and tests run 36083523370 succeeded. HTTPS enforced. Public Chrome verification loaded all three cases, each with three observations and a matching synthetic draft report returning HTTP 200. The Download draft RCA control was clicked successfully. Desktop had no horizontal overflow; mobile viewport/content measured 390/390. Console warnings/errors: none. Resource observations contained only same-origin CSS, JavaScript, fixture JSON, and the three report URLs.

Actual deployed screenshots: [desktop](screenshots/pages-desktop.jpg), [mobile](screenshots/pages-mobile.jpg), [diagnosis snippet](screenshots/pages-snippet.png). Visually reviewed: synthetic incident evidence only. The artifact contains **8 files**: three page assets, fixture JSON, three reports, and `.nojekyll`. Only the explicit generated artifact is uploaded; the repository and operator `.env` are not served.
## Guided toolkit — 2026-09-25
New collector tests first failed on the missing module; API tests failed on absent routes, and artifact tests failed on missing assets. An all-null network record regression first reported observed incorrectly; the identity-field validation corrected it. Final suite: `Ran 140 tests in 8.297s`, `OK`. JavaScript syntax checks passed for toolkit.js and the saved browser regression function.

Real Windows collection returned network observed/3 rows; connections observed/200 rows with truncated true; health observed/4 rows; services observed/4 rows. Only counts/statuses were recorded, not actual addresses or process inventories. A fresh local Uvicorn preview displayed a timestamped network result with 3 rows. No elevation, repairs, remote scans, model startup, or downloads occurred.

Independent review found stale visible history when a check completed during navigation. Browser reproduction showed history before=1/after=1. After correction, `tests/browser_toolkit.js` reported **5 checks passed**: result/text-only rendering/explanation/focus; matching JSON export; history refresh while another view is open; protection against wrong-tool results; visible background failure. Run this async function via browser evaluation in a freshly loaded local-mode tab after its catalog loads. It mocks diagnostic responses and never invokes collectors. Local console after restart: no warnings/errors. The small data-URI favicon is explicitly permitted by the image CSP.

Synthetic demo checks: four tools produced 1/2/3/4 expected rows, health showed Review needed for 8% free disk, explanations opened, session history contained four results, and the original incident assets remained available. Desktop 1440px had no page overflow; mobile content/viewport measured 390/390. Actual Chrome screenshots and element snippet are linked from TOOL-GUIDE.md and PROGRESS.md. Live deployment validation follows after publication.

## T15 deployment verification — 2026-09-25
Source 03677a9: Pages run 36099471457 succeeded; privacy/test run 36099471459 succeeded. Public HTTPS catalog loaded all four tools; network/connections/health/services rendered 1/2/3/4 synthetic rows with explanations and four session history records. Desktop had no horizontal overflow. Mobile measured 390/390; health showed Review needed and its JSON export button was exercised. Original incidents.html and report URL returned 200. Console had no warnings/errors. The browser check waits for the asynchronous catalog before interacting.

After final source restart, local health build_id matched current source. All four POST /api/tools/run requests returned HTTP 200 with observed readings (3 network rows, 200 connection rows, 4 health rows, 4 service rows). These private readings were not written to public artifacts. Staged scan before publication checked 105 file versions with zero findings; the pre-push history scan checked 183 file versions with zero findings.

## Neon Night — 2026-09-25
Four theme behavior tests first failed, then passed with `node --test tests/theme.test.cjs`: 4 tests, 4 pass, 0 fail. Coverage: saved preference, invalid preference fallback, switching both ways, blocked storage. Full Python suite: `Ran 140 tests in 8.255s`, `OK`. Both CI workflows now run the theme tests.

Chrome verified desktop overview, category navigation, health readings, explanations, saved theme restoration after reload, and returning to Light. Mobile content/viewport measured 390/390. Console warnings/errors: none. Sampled Neon Night contrast ratios: primary button 13.81:1, review badge 8.23:1, guide paragraph 7.65:1, timestamp 8.33:1, active navigation 10.25:1. This is a targeted contrast check, not a complete accessibility audit. Screenshots contain only the synthetic public artifact: neon-desktop.jpg and neon-mobile.jpg.

Neon Night live verification: source 339a225, Pages run 36101611164 and privacy/test run 36101611276 succeeded. Public selector switched to neon, persisted after reload, and rendered at mobile width 390/390 without console warnings/errors.

## 2026-09-25 — DNS resolution
Observed failing collector/API tests before implementation; numeric-address validation also failed before its type check was added. Final full suite: `Ran 152 tests in 8.374s`, `OK`. Node theme suite: 4 tests, 4 pass, 0 fail. Tests cover hostname/command separation, malformed records, bounded output, failure/empty results, timeouts, unsupported OS and strict API fields.

Live Windows lookups: example.com returned observed with 4 rows (126 ms); a reserved .invalid name returned issue with 0 rows (102 ms). Only counts/status/timing are recorded here. A freshly restarted local server also returned four address rows through the browser. Five mocked local browser checks passed using tests/browser_dns.js: invalid input, normalization, in-flight target editing, JSON export identity, and history restoration.

Independent review found no material security blocker and identified demo history/selector mismatch; corrected and verified with tests/browser_dns_demo.js. Desktop 1440px and mobile 390px had no page overflow, both themes switched, synthetic success/failure rendered correctly, and the console had no warnings/errors. Reviewed screenshots contain only synthetic fixtures. DNS query success is not an application-health test. No model download/startup occurred.

Public verification: commit 563acf0 deployed through successful Pages run 36132722248; privacy/test run 36132722190 also succeeded. Live desktop/mobile DNS examples and history regression passed, with no console warnings/errors. Final suite after documentation edits: `Ran 152 tests in 8.397s`, `OK`; four theme tests passed.
