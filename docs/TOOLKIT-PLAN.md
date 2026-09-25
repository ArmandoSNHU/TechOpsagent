# Guided toolkit implementation plan
Author: Armando Gomez

## Accepted design
Category navigation opens specific tools. Network, Computer health, Applications, Troubleshoot a problem, and Reports/history provide two paths to the same checks. A tool panel explains its purpose, runs an explicit check, displays timestamped evidence, explains limits, suggests the next tool, and exports a local report. Existing incident workflows remain available. Public Pages uses synthetic data only.

## Scope and decisions
Windows first. Implement network configuration, active TCP connections, resource/disk readings, and selected Windows service status using fixed read-only commands. No arbitrary shell, user-supplied commands, scans, packet capture, remediation, model download, or inference. DNS configuration is observed; remote reachability is explicitly not checked. Hostname/HTTPS probes and packet imports remain labeled planned. Explanation is deterministic and labeled accordingly. Real results are kept only in browser memory until explicitly exported; they never enter public artifacts.

## Tasks
- [x] 1. Add collector tests for command allowlist, unsupported platform, timeout, malformed/oversized output, empty readings, threshold boundaries and output field allowlists. Observe failure, implement collectors, verify.
- [x] 2. Add catalog/read-only run API tests and docs-as-contract coverage. Integrate explicit asset routes and entry links without changing existing incident IDs/history.
- [x] 3. Implement shared responsive category dashboard, guided shortcuts, tool details, states, deterministic explanations, session results and export. Pages receives separate synthetic fixtures; local mode is set only by its server-delivered HTML.
- [x] 4. Verify full suite, both JavaScript files, desktop/mobile interactions, real Windows collection with summarized output only, failure/loading states and synthetic screenshots. Update button guide, API docs, checklist and STATE.
- [x] 5. Review public artifact and privacy scans, commit/push under existing publication authorization, verify Pages and CI.

## Review focus
Failed or empty collection must never show healthy. Unknown tool IDs never execute commands. Backend failures must not expose raw stderr. Switching tools while a run is pending must not mislabel results. Public builds must never read local results or configuration. Exports can contain local network details and must be explicitly initiated.

## Review and verification
Read-only review found one actionable navigation race: visible session history did not refresh during a pending run. Reproduced in Chrome, fixed with active-view tracking and history refresh, and covered by tests/browser_toolkit.js. Five browser checks passed. Full suite: 140 tests OK. Added null-reading validation after observing a failing regression.

Deployment verified: Pages run 36099471457 and privacy/test run 36099471459 succeeded for 03677a9. Public desktop/mobile tools, history, report export, and original incident routes verified.
