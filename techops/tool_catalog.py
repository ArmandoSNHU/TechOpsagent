"""Public tool descriptions and synthetic examples; never operator data."""
from techops.toolkit import summarize

CATALOG = {
    'categories': [
        {'id': 'network', 'title': 'Network', 'description': 'Adapters, connection paths, and network evidence.', 'icon': '↗', 'tools': ['network', 'connections', 'dns', 'website', 'capture']},
        {'id': 'computer', 'title': 'Computer health', 'description': 'Resource pressure and selected Windows services.', 'icon': '▤', 'tools': ['health', 'services', 'processes']},
        {'id': 'applications', 'title': 'Applications', 'description': 'Investigate application failures and dependencies.', 'icon': '◇', 'tools': ['incidents', 'api', 'certificate', 'logs']},
        {'id': 'troubleshoot', 'title': 'Troubleshoot a problem', 'description': 'Start with a symptom and follow the evidence.', 'icon': '◎', 'tools': ['network', 'health', 'services', 'connections']},
        {'id': 'reports', 'title': 'Reports & history', 'description': 'Reopen this session or visit saved investigations.', 'icon': '≡', 'tools': ['history']},
    ],
    'tools': {
        'network': {'title': 'Check my network', 'description': 'Read active adapters, IPv4 addresses, configured gateways, and DNS servers.', 'availability': 'ready', 'next': 'connections', 'limit': 'Configuration only. This does not test internet access, Wi-Fi signal, DNS resolution, or gateway reachability.', 'help': 'Look for the adapter you expect to use. Multiple adapters may represent VPNs or virtual networks. A configured gateway does not prove it is reachable.'},
        'connections': {'title': 'Show active connections', 'description': 'Read up to 200 TCP endpoints with their owning process and connection state.', 'availability': 'ready', 'next': 'services', 'limit': 'A point-in-time TCP snapshot, not a packet capture. No UDP, traffic volume, or threat classification. Process names may be unavailable.', 'help': 'Established means a TCP connection exists. Listen means a process is waiting for connections. Neither state alone indicates malicious activity.'},
        'health': {'title': 'Check computer health', 'description': 'Read available CPU load, memory use, and free space on fixed disks.', 'availability': 'ready', 'next': 'services', 'limit': 'One snapshot. Advisory thresholds: CPU/memory over 90%, disk free below 10%. Missing measurements are not inferred.', 'help': 'Repeat a high reading to see whether it persists. Low disk space is a reason to review storage; this tool never deletes files or stops a process.'},
        'services': {'title': 'Check Windows services', 'description': 'Read DNS Client, DHCP Client, Print Spooler, and Windows Time service states.', 'availability': 'ready', 'next': 'network', 'limit': 'Only four named services are queried. A stopped or manual service is not automatically an error.', 'help': 'Compare the service state with the feature you need. A manually started or trigger-started service can be stopped during normal operation.'},
        'dns': {'title': 'Test DNS resolution', 'availability': 'planned', 'description': 'A future hostname lookup tool with explicit target selection.'},
        'website': {'title': 'Test a website or server', 'availability': 'planned', 'description': 'A future bounded connection and HTTPS check for a user-selected target.'},
        'capture': {'title': 'Analyze a packet capture', 'availability': 'planned', 'description': 'A future local capture-file analysis tool. No packet capture runs in this release.'},
        'processes': {'title': 'Find busy processes', 'availability': 'planned', 'description': 'A future per-process resource view. Current health checks provide system totals.'},
        'api': {'title': 'Test an API', 'availability': 'planned', 'description': 'A future configured-target API diagnostic. Use incident investigations for the existing controlled lab.'},
        'certificate': {'title': 'Check a certificate', 'availability': 'planned', 'description': 'A future TLS expiry and certificate validation tool.'},
        'logs': {'title': 'Review application errors', 'availability': 'link', 'description': 'Open the incident workspace; the local version supports imported structured logs.'},
        'incidents': {'title': 'Investigate an incident', 'availability': 'link', 'description': 'Open evidence, suspected causes, troubleshooting steps, and draft RCA reports.'},
        'history': {'title': 'Saved investigations', 'availability': 'link', 'description': 'Open the incident workspace history. Public demo investigations are synthetic and are not persisted.'},
    },
    'shortcuts': [
        {'title': 'Internet is not working', 'tool': 'network'},
        {'title': 'Computer is slow', 'tool': 'health'},
        {'title': 'Application will not open', 'tool': 'services'},
        {'title': 'Connection keeps dropping', 'tool': 'connections'},
    ],
}

_READINGS = {
    'network': [{'adapter': 'Demo Ethernet', 'ipv4': ['192.0.2.10'], 'gateway': ['192.0.2.1'], 'dns': ['192.0.2.53']}],
    'connections': [{'process': 'demo-browser', 'local': '192.0.2.10:50123', 'remote': '198.51.100.20:443', 'state': 'Established'}, {'process': 'demo-service', 'local': '127.0.0.1:8080', 'remote': '0.0.0.0:0', 'state': 'Listen'}],
    'health': [{'metric': 'CPU load %', 'value': 28, 'scope': 'System'}, {'metric': 'Memory used %', 'value': 64, 'scope': 'System'}, {'metric': 'Disk free %', 'value': 8, 'scope': 'Demo C:'}],
    'services': [{'service': 'Dnscache', 'state': 'Running', 'start': 'Auto'}, {'service': 'Dhcp', 'state': 'Running', 'start': 'Auto'}, {'service': 'Spooler', 'state': 'Stopped', 'start': 'Manual'}, {'service': 'W32Time', 'state': 'Stopped', 'start': 'Manual'}],
}
DEMO = {key: {'tool': key, 'mode': 'demo', 'collected_at': 'Synthetic example — not collected from your device',
              'readings': rows, 'status': summarize(key, rows)[0], 'summary': summarize(key, rows)[1], 'truncated': False}
        for key, rows in _READINGS.items()}
