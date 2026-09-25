# Incident report: Integration credential rejected

Author: Armando Gomez
Incident ID: 59e0f7c5215448998d7b7f74d16fb763
Created (UTC): 2026-09-24T22:54:38.378004+00:00
Severity: P3
Status: suspected — not verified
Environment: simulated lab | Analysis: deterministic

## Impact
Simulated partner synchronization is blocked; data-loss impact is unknown.

## Suspected cause
Credential rejected

## Evidence
- HTTP fixture: GET /partner/orders → 401. The protected endpoint rejects the supplied credential.
- Application log: invalid_token: token expired. The fixture records expiry; no credential value is included.
- Health fixture: GET /health → 200 · 19 ms. The sampled service is reachable independently of authentication.

## Next steps
1. Check credential expiry and secret references without displaying secret values.
2. Confirm the intended account, permissions, and environment.
3. Request approval to rotate the credential; retry a read-only authenticated request.

## Prevention
Monitor credential expiry and document a tested rotation procedure.

## Limitations
This is a draft RCA based on synthetic fixtures, not a confirmed production root cause. No live probes, model inference, remediation, or remote writes occurred.

## Ticket context (untrusted, redacted)
> No additional ticket context.
