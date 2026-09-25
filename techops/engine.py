"""Evidence-driven demo analysis. Never executes ticket contents."""
from datetime import datetime, timezone
import re
from uuid import uuid4

SCENARIOS = {
    'api_error': {
        'title': 'Checkout API failure', 'service': 'checkout-api', 'severity': 'P2',
        'description': 'Checkout requests return HTTP 500 after a deployment.',
        'cause': 'Unhandled application exception',
        'impact': 'Simulated customers cannot complete checkout; payment impact is unverified.',
        'evidence': [
            {'source': 'HTTP fixture', 'signal': 'GET /checkout → 500', 'detail': 'The application responds, but the request fails inside the service.', 'state': 'failed'},
            {'source': 'Application log', 'signal': 'KeyError: TAX_REGION', 'detail': 'checkout.py:42 reads a missing configuration entry.', 'state': 'failed'},
            {'source': 'Dependency fixture', 'signal': 'Inventory API → 200 · 28 ms', 'detail': 'The sampled inventory dependency responds successfully.', 'state': 'passed'}],
        'next_steps': ['Compare required configuration with the previous release.', 'Reproduce the exception in a test environment with a missing TAX_REGION.', 'Request approval for a configuration correction or rollback, then repeat the checkout smoke test.'],
        'prevention': 'Validate required configuration at startup and include checkout smoke tests in deployment checks.'},
    'dependency_timeout': {
        'title': 'Inventory dependency timeout', 'service': 'inventory-gateway', 'severity': 'P2',
        'description': 'Product requests stall while waiting for the inventory service.',
        'cause': 'Dependency timeout',
        'impact': 'Simulated product availability requests exceed the response-time budget.',
        'evidence': [
            {'source': 'HTTP fixture', 'signal': 'GET /availability → 504', 'detail': 'The gateway exceeded its upstream response deadline.', 'state': 'failed'},
            {'source': 'Application log', 'signal': 'inventory read timeout · 3000 ms', 'detail': 'Three fixture requests waited for the same upstream service.', 'state': 'failed'},
            {'source': 'DNS fixture', 'signal': 'inventory.internal → resolved', 'detail': 'Successful name resolution narrows this sample beyond a DNS lookup failure.', 'state': 'passed'}],
        'next_steps': ['Compare upstream latency and error rates during the incident window.', 'Inspect inventory saturation, connection pools, and recent changes.', 'Request approval for mitigation; verify recovery with repeated availability checks.'],
        'prevention': 'Add upstream latency alerts, bounded retries, circuit breaking, and load tests.'},
    'invalid_credential': {
        'title': 'Integration credential rejected', 'service': 'partner-sync', 'severity': 'P3',
        'description': 'A partner integration rejects authentication while its health endpoint responds.',
        'cause': 'Credential rejected',
        'impact': 'Simulated partner synchronization is blocked; data-loss impact is unknown.',
        'evidence': [
            {'source': 'HTTP fixture', 'signal': 'GET /partner/orders → 401', 'detail': 'The protected endpoint rejects the supplied credential.', 'state': 'failed'},
            {'source': 'Application log', 'signal': 'invalid_token: token expired', 'detail': 'The fixture records expiry; no credential value is included.', 'state': 'failed'},
            {'source': 'Health fixture', 'signal': 'GET /health → 200 · 19 ms', 'detail': 'The sampled service is reachable independently of authentication.', 'state': 'passed'}],
        'next_steps': ['Check credential expiry and secret references without displaying secret values.', 'Confirm the intended account, permissions, and environment.', 'Request approval to rotate the credential; retry a read-only authenticated request.'],
        'prevention': 'Monitor credential expiry and document a tested rotation procedure.'}
}

def redact(text):
    text = re.sub(r'(?i)(bearer\s+)\S+', r'\1[REDACTED]', text)
    return re.sub(r'(?i)((?:api[_-]?key|password|token|secret)\s*[:=]\s*)[^\s,;]+', r'\1[REDACTED]', text)

def investigate(scenario, ticket=''):
    if scenario not in SCENARIOS:
        raise ValueError('Unknown scenario')
    if not isinstance(ticket, str) or len(ticket) > 4000:
        raise ValueError('Ticket must be text of at most 4000 characters')
    import copy
    result = copy.deepcopy(SCENARIOS[scenario])
    result.update(id=uuid4().hex, scenario=scenario, created_at=datetime.now(timezone.utc).isoformat(),
                  ticket=redact(ticket), status='suspected', analysis_mode='deterministic',
                  environment='simulated', author='Armando Gomez')
    return result

def render_report(r):
    lines = ['# Incident report: ' + r['title'], '', 'Author: Armando Gomez',
             'Incident ID: ' + r['id'], 'Created (UTC): ' + r['created_at'],
             'Severity: ' + r['severity'], 'Status: suspected — not verified',
             'Environment: ' + r['environment'] + ' | Analysis: ' + r['analysis_mode'], '',
             '## Impact', r['impact'], '', '## Suspected cause', r['cause'], '', '## Evidence']
    lines += ['- ' + e['source'] + ': ' + e['signal'] + '. ' + e['detail'] for e in r['evidence']]
    if r.get('hypotheses'):
        lines += ['', '## Ranked hypotheses (rule scores, not probabilities)']
        lines += ['- ' + h['cause'] + ': score ' + str(h['score']) + '; evidence ' + ', '.join(h['evidence_ids']) for h in r['hypotheses']]
    lines += ['', '## Next steps'] + [str(i) + '. ' + s for i, s in enumerate(r['next_steps'], 1)]
    lines += ['', '## Prevention', r['prevention'], '', '## Limitations',
              r.get('limitations', 'This is a draft RCA based on synthetic fixtures, not a confirmed production root cause. No live probes, model inference, remediation, or remote writes occurred.'),
              '', '## Ticket context (untrusted, redacted)']
    lines += ['> ' + line for line in (r['ticket'] or 'No additional ticket context.').splitlines()]
    return '\n'.join(lines) + '\n'
