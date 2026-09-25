"""Explicit DNS-only lookup with bounded process lifetime and data-only input."""
from datetime import datetime, timezone
import ipaddress
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys

SCRIPT = r"""
$ErrorActionPreference='Stop'
[Console]::InputEncoding=[System.Text.UTF8Encoding]::new()
[Console]::OutputEncoding=[System.Text.UTF8Encoding]::new()
$request=[Console]::In.ReadToEnd() | ConvertFrom-Json
$null=Get-Command Resolve-DnsName -ErrorAction Stop
$timer=[System.Diagnostics.Stopwatch]::StartNew()
try {
    $rows=@(Resolve-DnsName -Name $request.hostname -Type A_AAAA -DnsOnly -NoHostsFile -QuickTimeout -ErrorAction Stop |
      Where-Object { [string]$_.Type -in @('A','AAAA','CNAME') } | Select-Object -First 65 | ForEach-Object {
        [pscustomobject]@{name=$_.Name; type=[string]$_.Type; answer=if($_.IPAddress){$_.IPAddress}else{$_.NameHost}; ttl_seconds=[long]$_.TTL}
      })
    $outcome='ok'
} catch { $rows=@(); $outcome='failed' }
$timer.Stop()
[pscustomobject]@{outcome=$outcome; elapsed_ms=$timer.ElapsedMilliseconds; readings=$rows} | ConvertTo-Json -Depth 5 -Compress
"""


def normalize_hostname(value):
    if not isinstance(value, str) or any(ord(c) < 32 for c in value):
        raise ValueError('Enter a hostname, not a URL, IP address, or command')
    value = value.strip().lower()
    if value.endswith('.'):
        value = value[:-1]
    if not 1 <= len(value) <= 253 or not re.search('[a-z]', value):
        raise ValueError('Enter a hostname of at most 253 ASCII characters')
    if any(not re.fullmatch(r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?', label) for label in value.split('.')):
        raise ValueError('Enter a hostname without URL paths, spaces or ports')
    try:
        ipaddress.ip_address(value)
    except ValueError:
        return value
    raise ValueError('Enter a hostname rather than an IP address')


def validate_response(data):
    if not isinstance(data, dict) or data.get('outcome') not in ('ok', 'failed'):
        raise ValueError('Invalid DNS response')
    elapsed = data.get('elapsed_ms')
    if type(elapsed) not in (int, float) or not math.isfinite(elapsed) or not 0 <= elapsed <= 12000:
        raise ValueError('Invalid timing')
    rows = data.get('readings')
    if not isinstance(rows, list):
        raise ValueError('Invalid records')
    cleaned = []
    for row in rows[:64]:
        if not isinstance(row, dict):
            raise ValueError('Invalid record')
        kind = row.get('type')
        name = normalize_hostname(row.get('name'))
        answer = row.get('answer')
        if not isinstance(answer, str) or not 1 <= len(answer) <= 254:
            raise ValueError('Invalid answer')
        ttl = row.get('ttl_seconds')
        if type(ttl) is not int or not 0 <= ttl <= 4294967295:
            raise ValueError('Invalid TTL')
        if kind in ('A', 'AAAA'):
            address = ipaddress.ip_address(answer)
            if address.version != (4 if kind == 'A' else 6):
                raise ValueError('Address type mismatch')
            answer = str(address)
        elif kind == 'CNAME':
            answer = normalize_hostname(answer)
        else:
            raise ValueError('Unexpected record type')
        cleaned.append({'name': name, 'type': kind, 'answer': answer, 'ttl_seconds': ttl})
    if data['outcome'] == 'failed' and cleaned:
        raise ValueError('Inconsistent failed result')
    return cleaned, elapsed, len(rows) > 64


def collect_dns(hostname, *, runner=None, platform=None):
    hostname = normalize_hostname(hostname)
    result = {'tool': 'dns', 'mode': 'local', 'hostname': hostname, 'elapsed_ms': None,
              'collected_at': datetime.now(timezone.utc).isoformat(), 'status': 'unavailable',
              'summary': 'DNS lookup currently requires Windows.', 'readings': [], 'truncated': False}
    if (platform or sys.platform) != 'win32':
        return result
    executable = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    try:
        completed = (runner or subprocess.run)([str(executable), '-NoProfile', '-NonInteractive', '-Command', SCRIPT],
            input=json.dumps({'hostname': hostname}), shell=False, capture_output=True, text=True,
            encoding='utf-8', errors='replace', timeout=12, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if completed.returncode or len(completed.stdout) > 262144:
            raise ValueError('DNS command unavailable')
        data = json.loads(completed.stdout)
        rows, elapsed, truncated = validate_response(data)
        result.update(readings=rows, elapsed_ms=elapsed, truncated=truncated)
        if data['outcome'] == 'failed':
            result.update(status='issue', summary='The DNS lookup failed. The name may not exist, DNS may be unreachable, or a resolver policy may have blocked it. The cause is not established.')
        elif not any(row['type'] in ('A', 'AAAA') for row in rows):
            result.update(status='not_checked', summary='The query returned no usable address records. This does not prove that the hostname or application is unavailable.')
        else:
            result.update(status='observed', summary='DNS returned address records. This does not test TCP connectivity, HTTPS, or application health. Cached responses may contribute; elapsed time is not a network latency measurement.')
    except subprocess.TimeoutExpired:
        result['summary'] = 'The DNS process exceeded its 12-second limit. No complete result was recorded; the cause of the delay is unknown.'
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        result['summary'] = 'DNS collection unavailable or response invalid. Check Windows DNS Client availability and permissions, then retry. Raw system errors are not exposed.'
    return result
