# What a technical operations agent needs to do
Author: Armando Gomez
Research and implementation review: 2026-09-26

## Purpose
A useful technical operations agent helps an operator restore a user's service, collect defensible evidence, coordinate the response, and prevent recurrence. For this project, the intended audience is an individual Windows user or support technician. Enterprise incident command, continuous monitoring and autonomous remediation are future capabilities, not claims about the current toolkit.

## Findings from primary sources
Google's [monitoring guidance](https://sre.google/sre-book/monitoring-distributed-systems/) distinguishes user-visible symptoms from causes and emphasizes latency, traffic, errors and saturation. A configured adapter or established TCP socket cannot substitute for an end-user availability check. Our snapshots cover portions of configuration and resource saturation; they do not measure those four service signals continuously.

Google's [incident management guidance](https://sre.google/sre-book/managing-incidents/) emphasizes coordination, explicit responsibility, communication and a maintained incident record. A useful handoff therefore needs impact, evidence, outstanding questions, an owner and a next update—not just a command result.

[ServiceNow's incident-management overview](https://www.servicenow.com/products/itsm/what-is-incident-management.html) centers restoring service and reducing business disruption. Root-cause investigation and recurrence prevention are related follow-up work. This project should never turn a suspected cause into a confirmed RCA merely because a report was generated.

Google's [AI engineering for reliable operations](https://sre.google/resources/practices-and-processes/ai-engineering-reliable-operations/) describes operational assistance grounded in monitoring, logs, playbooks and incident context, including read-only investigation. Our inference from this is that better evidence and workflows should precede adding a chat box. A local model can later explain cited observations, but must not invent measurements or execute changes based on untrusted logs.

## Capability review
| Responsibility | Current evidence | Gap and next improvement |
|---|---|---|
| Understand the problem | Four guided symptoms; impact and recent-change notes | Service inventory, owner and explicit impact/urgency policy |
| Collect relevant observations | Five on-demand Windows tools; log/lab incident workspace | Safe configured-target HTTPS/TLS checks; per-process pressure |
| Explain evidence | Deterministic summaries, timestamps and limitations | Cross-source correlation with service identity and time alignment |
| Guide troubleshooting | Ordered checks and explicit evidence gaps implemented in T18 | Richer runbooks for printing, VPN, authentication and disk pressure |
| Coordinate a response | Markdown support handoff with evidence references and recovery checklist | Assignable incident lifecycle, update timeline and authenticated ticket workflow |
| Verify recovery | Explicit reminder to repeat the original user task; remains unverified | Before/after comparison and recorded user confirmation |
| Monitor services | Grafana/Loki synthetic lab and read-only connectors | Real service-level metrics, history, SLOs and actionable alerts |
| Learn from incidents | Draft incident reports and prevention suggestions | Reviewed runbooks and linked recurring problems/change records |
| Use AI responsibly | Opt-in local adapter evaluated separately | Cited local chat, uncertainty and prompt-injection evaluation |
| Protect operator data | Loopback binding, ignored .env, publication guards, synthetic Pages | Consent-aware redacted evidence bundles and access control for multi-user use |

## Implemented now: guided investigations
The four existing symptom shortcuts now start a scoped investigation. Each shows relevant checks and why they matter, an operations brief, missing or stale evidence, and manual impact/change notes. Only checks run after starting the investigation contribute. A later result replaces the previous result for that tool, including failed requests. The summary never declares root cause or recovery.

Local timestamps older than ten minutes, invalid timestamps and future timestamps are marked stale. This ten-minute threshold is an explicit product heuristic, not an industry standard or proof that newer evidence still describes the user's situation. Refresh evidence age or reopen the brief to recalculate; there is no background monitoring. Synthetic examples are labeled and do not expire.

The Markdown handoff includes evidence identifiers, collection times, DNS target where applicable, gaps and escalation/recovery reminders. Raw tables are excluded. Notes and summaries may still contain private details and are not automatically redacted. It neither creates a ServiceNow ticket nor sends a message.

## Prioritized roadmap
1. Configured-target HTTPS/TLS diagnostics with strict target controls, bounded reads and no credential forwarding. This tests a service more directly than DNS alone.
2. Incident lifecycle: service/owner, impact and urgency, investigation timeline, change record and explicit recovery verification.
3. Time-series service readouts: error rate, request volume, latency and saturation from configured sources. Distinguish unavailable telemetry from healthy values.
4. Read-only per-process resource investigation and optional local packet-file analysis. Live packet capture is specialized, potentially sensitive, and not necessary for every incident.
5. Optional local chat grounded in current evidence and reviewed runbooks, with references and no autonomous command execution.

These are separate future tasks. T18 adds a guided decision and handoff layer over current tools; it does not complete the entire roadmap.
