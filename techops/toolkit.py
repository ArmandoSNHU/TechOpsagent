"""Bounded, read-only Windows snapshots. No targets or commands from input."""
from datetime import datetime, timezone
import json
import math
import os
from pathlib import Path
import subprocess
import sys

SCRIPTS = {
    'network': """Get-NetIPConfiguration | Where-Object {$_.NetAdapter.Status -eq 'Up'} | Select-Object -First 32 | ForEach-Object {
        [pscustomobject]@{adapter=$_.InterfaceAlias; ipv4=@($_.IPv4Address.IPAddress); gateway=@($_.IPv4DefaultGateway.NextHop); dns=@($_.DNSServer.ServerAddresses)}
    }""",
    'connections': """Get-NetTCPConnection | Select-Object -First 201 | ForEach-Object {
        $p=Get-Process -Id $_.OwningProcess -ErrorAction SilentlyContinue
        [pscustomobject]@{process=if($p){$p.ProcessName}else{'unavailable'}; local=('{0}:{1}' -f $_.LocalAddress,$_.LocalPort); remote=('{0}:{1}' -f $_.RemoteAddress,$_.RemotePort); state=[string]$_.State}
    }""",
    'health': """$os=Get-CimInstance Win32_OperatingSystem
        [pscustomobject]@{metric='Memory used %'; value=[math]::Round(100*(1-$os.FreePhysicalMemory/$os.TotalVisibleMemorySize),1); scope='System'}
        $cpu=Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average
        if($null -ne $cpu.Average){[pscustomobject]@{metric='CPU load %'; value=[math]::Round($cpu.Average,1); scope='System'}}
        Get-CimInstance Win32_LogicalDisk -Filter 'DriveType=3' | Where-Object {$_.Size -gt 0} | Select-Object -First 32 | ForEach-Object {
          [pscustomobject]@{metric='Disk free %'; value=[math]::Round(100*$_.FreeSpace/$_.Size,1); scope=$_.DeviceID}
        }""",
    'services': """Get-CimInstance Win32_Service -Filter \"Name='Dnscache' OR Name='Dhcp' OR Name='Spooler' OR Name='W32Time'\" | ForEach-Object {
        [pscustomobject]@{service=$_.Name; state=$_.State; start=$_.StartMode}
    }""",
}
FIELDS = {
    'network': ('adapter', 'ipv4', 'gateway', 'dns'),
    'connections': ('process', 'local', 'remote', 'state'),
    'health': ('metric', 'value', 'scope'),
    'services': ('service', 'state', 'start'),
}


def summarize(tool, readings):
    if not readings:
        return 'not_checked', 'No usable readings returned. This is not a healthy result.'
    if tool == 'network':
        return 'observed', 'Active adapter configuration collected. Internet access, gateway reachability and DNS resolution were not tested.'
    if tool == 'connections':
        return 'observed', 'TCP connection snapshot collected. A connection or listening port alone does not indicate a threat. UDP and traffic volume are not measured.'
    if tool == 'services':
        return 'observed', 'Selected service states collected. A stopped service is not necessarily a fault; manual and trigger-start services may be idle.'
    for reading in readings:
        value = reading.get('value')
        if isinstance(value, (int, float)):
            if (reading.get('metric') == 'Disk free %' and value < 10) or (reading.get('metric') in ('CPU load %', 'Memory used %') and value > 90):
                return 'issue', 'A snapshot crossed the advisory threshold: less than 10% disk free or over 90% CPU/memory use. Repeat the check before concluding a persistent problem.'
    return 'observed', 'Available resource readings did not cross the advisory thresholds. This snapshot does not prove the computer is healthy.'


def clean_rows(tool, data):
    if isinstance(data, dict):
        data = [data]
    if not isinstance(data, list):
        raise ValueError('Invalid collection shape')
    cleaned = []
    for row in data[:200]:
        if not isinstance(row, dict) or not all(field in row for field in FIELDS[tool]):
            continue
        identity = row[FIELDS[tool][0]]
        if not isinstance(identity, str) or not identity.strip():
            continue
        item = {}
        for field in FIELDS[tool]:
            value = row[field]
            if isinstance(value, list):
                value = [str(v)[:256] for v in value[:16] if isinstance(v, (str, int))]
            elif isinstance(value, str):
                value = value[:256]
            elif type(value) in (int, float):
                if not math.isfinite(value):
                    raise ValueError('Nonfinite reading')
            elif value is not None:
                raise ValueError('Invalid field')
            item[field] = value
        if tool == 'health' and (type(item['value']) not in (float, int) or not 0 <= item['value'] <= 100):
            continue
        cleaned.append(item)
    return cleaned, len(data) > 200


def collect(tool, *, runner=None, platform=None):
    if tool not in SCRIPTS:
        raise ValueError('Unknown diagnostic tool')
    result = {'tool': tool, 'mode': 'local', 'collected_at': datetime.now(timezone.utc).isoformat(),
              'status': 'unavailable', 'summary': 'This tool currently requires Windows.', 'readings': [], 'truncated': False}
    if (platform or sys.platform) != 'win32':
        return result
    executable = Path(os.environ.get('SystemRoot', r'C:\Windows')) / 'System32/WindowsPowerShell/v1.0/powershell.exe'
    script = "$ErrorActionPreference='Stop'; [Console]::OutputEncoding=[System.Text.UTF8Encoding]::new(); $rows=@(& {" + SCRIPTS[tool] + "}); ConvertTo-Json -InputObject $rows -Depth 5 -Compress"
    try:
        completed = (runner or subprocess.run)(
            [str(executable), '-NoProfile', '-NonInteractive', '-Command', script],
            shell=False, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=12,
            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        if completed.returncode or len(completed.stdout) > 262144:
            raise ValueError('Collection unavailable')
        result['readings'], result['truncated'] = clean_rows(tool, json.loads(completed.stdout))
        result['status'], result['summary'] = summarize(tool, result['readings'])
    except (OSError, subprocess.SubprocessError, ValueError, TypeError):
        result['summary'] = 'Collection unavailable. Windows permissions, a missing component, or the 12-second time limit may prevent this check. No repair was performed.'
    return result
