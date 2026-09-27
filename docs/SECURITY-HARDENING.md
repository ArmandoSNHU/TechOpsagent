# Security hardening and verification

Author: Armando Gomez

This is a local portfolio lab, not a production security certification. Current execution and publication status belongs in [STATE.md](../STATE.md). The runtime remains Python and browser JavaScript; rewriting these controls in C++ would add complexity without improving their trust boundaries.

## What the controls protect

| Boundary | Control | Remaining limit |
| --- | --- | --- |
| Browser to local backend | Loopback listener, actual loopback peer and endpoint checks, Host/Origin checks, JSON and body limits | No user authentication; another local process can access it. No public/LAN backend hosting. |
| Local readings to downloaded reports | Structural summaries omit raw readings, targets, notes and private ticket text | Full details remain visible locally. Screenshots and manual copying still need review. |
| Ticket triage to output | Process-local keyed pseudonyms; no raw ticket body/requester or original ID in results | Categories and urgency can still be sensitive; detection labels are not a redaction service. |
| Runbook to filesystem | Relative paths confined to the configured root; resolved symlinks checked; bounded regular-file reads | Use a trusted directory. Concurrent filesystem changes are not an OS sandbox. |
| Runbook to network | Network denied unless operator explicitly grants exact hosts; HTTP(S) only; redirects/proxies disabled | Granted hosts and their DNS are trusted; this is not a general SSRF sandbox. |
| Source to GitHub | Local publication guard, GitHub secret scanning and push protection | Pattern detection cannot guarantee absence of sensitive prose or unknown secret formats. |
| Pull request to main | Required checks tied to GitHub Actions, current-base requirement, PR requirement, resolved conversations, admin enforcement; force-push/deletion disabled | Solo-owner setup requires zero additional approving reviewers. Human review remains important. |
| Third-party packages/actions | Pinned Actions, read-only CI permissions, no retained checkout credentials; Dependabot and dependency audits | Audits detect known advisories, not every malicious package or undisclosed vulnerability. |

## Repository coverage

GitHub secret scanning, push protection, vulnerability alerts, automatic security fixes and main-branch protection were enabled and read back through the API for all five repositories. Security-update pull requests are not automatically merged.

- TechOpsagent requires `verify` and `dependency-audit`.
- The runbook, triage and cloud repositories require all three Python matrix checks.
- FDE_Dashboard requires both operating-system server/eval checks and `dependency-audit`.

Dependabot configuration tracks Python manifests and GitHub Actions weekly. TechOpsagent and both FDE lockfiles have scheduled and PR-triggered `pip-audit` checks. The other three projects declare no third-party runtime dependencies; their standard library still depends on a supported, patched Python installation.

Workflow changes in a PR do not activate default-branch scheduled runs until merged. Runtime fixes likewise remain on their review branches until merge. Repository settings take effect immediately.

## Reproduce the dependency checks

From TechOpsagent, using the installed `uv` tool:

```powershell
uvx --from pip-audit==2.10.1 pip-audit -r requirements.txt --no-deps --disable-pip --progress-spinner off
```

From each FDE project directory:

```powershell
uv export --frozen --no-emit-project --no-emit-package fde-mcp --format requirements-txt --output-file audit-requirements.txt --quiet
uvx --from pip-audit==2.10.1 pip-audit -r audit-requirements.txt --no-deps --disable-pip --progress-spinner off
```

Keep generated audit files outside commits. Only local source packages are excluded from the FDE package audit; their code is covered by repository review/tests. These commands query a public vulnerability service with package names/versions, not tickets, credentials or diagnostic readings. Tool installation may require internet access.

On 2026-09-27 all three dependency audits returned `No known vulnerabilities found`. A network or scanner failure is a failed check, not a clean result. See STATE.md for regression counts and branch status.

## Everyday use

1. Run `setup.ps1 -Check` and `setup.ps1 -Test`; start through `setup.ps1 -Run` on localhost.
2. Use synthetic tickets while learning. Keep real diagnostic details in the local workspace.
3. Download the privacy summary from a tool, investigation or incident. Read it before sharing; do not add private notes back into the public repo.
4. For a runbook, first validate with a deliberately narrow `--base-dir`. Grant `--allow-host` only for a host you control or are authorized to check.
5. Review dependency/security PRs, run checks and merge through the protected PR path. Never bypass checks to clear a warning.
6. If a credential is exposed, revoke/rotate it first. Removing a file does not remove copies or historical commits.

There was no penetration test, model download, production deployment or automatic remediation in this pass. Phone access should continue through authenticated remote access to the desktop; direct authenticated mobile backend access remains a separate task.

References: [GitHub branch protection](https://docs.github.com/en/rest/branches/branch-protection), [pip-audit behavior and limitations](https://github.com/pypa/pip-audit).
