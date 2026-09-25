"""Fail closed on common secret formats and private artifacts; never print values."""
import argparse
import json
from pathlib import PurePosixPath
import re
import subprocess

SECRET = re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----|\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16}|xox[baprs]-[A-Za-z0-9-]{20,})')
EMAIL = re.compile(r'[A-Za-z0-9._%+-]+@([A-Za-z0-9.-]+\.[A-Za-z]{2,})')
ASSIGNMENT = re.compile(r'''(?i)\b(?:[a-z0-9_]*(?:api_?key|password|secret|token))\s*["']?\s*[:=]\s*["']([A-Za-z0-9_./+=-]{12,})["']''')

def inspect_file(path, data):
    p = PurePosixPath(path); name = p.name.lower()
    issues = []
    private = ((name == '.env' or name.startswith('.env.')) and name != '.env.example')
    private |= path.startswith(('data/', '.venv/', 'uploads/', 'exports/', 'backups/')) and path != 'data/.gitkeep'
    private |= p.suffix.lower() in {'.pem', '.key', '.p12', '.pfx', '.sqlite', '.sqlite3', '.db', '.log', '.dump', '.bak'}
    private |= '.local.' in name or name in {'id_rsa', 'id_ed25519', 'credentials.json'}
    if private: issues.append('private artifact')
    if data.startswith((b'\x89PNG', b'\xff\xd8')): return issues  # Requires separate visual review.
    try: text = data.decode('utf-8-sig')
    except UnicodeDecodeError: return issues + ['unreviewed binary artifact']
    if SECRET.search(text): issues.append('credential signature')
    assignments = list(ASSIGNMENT.finditer(text))
    if any(not (path == 'tests/test_connectors.py' and match.group(1) == 'privatevalue') for match in assignments):
        issues.append('credential-like assignment')
    if any(m.group(1).lower() not in {'example.com', 'example.org', 'example.invalid', 'users.noreply.github.com'} for m in EMAIL.finditer(text)):
        issues.append('personal email')
    if name == '.env.example':
        for line in text.splitlines():
            if line.strip() and not line.lstrip().startswith('#'):
                key, sep, value = line.partition('=')
                if not sep or value.strip(): issues.append('populated environment template'); break
    if path == 'config/integrations.json':
        try:
            if any(json.loads(text).values()): issues.append('operator configuration')
        except (ValueError, AttributeError): issues.append('invalid configuration')
    return issues

def git(*args):
    return subprocess.check_output(['git', *args], stderr=subprocess.PIPE)

def scan(staged=False, history=False):
    findings = []; checked = 0
    entries = [(None, p) for p in git('ls-files', '-z').decode().split('\0') if p]
    if history:
        # Inspect every committed tree, including removed files; deduplicate blobs by path.
        entries = []
        seen = set()
        for commit in git('rev-list', '--all').decode().splitlines():
            for entry in git('ls-tree', '-r', '-z', commit).split(b'\0'):
                if not entry: continue
                metadata, path = entry.split(b'\t', 1)
                mode, kind, oid = metadata.decode().split()
                path = path.decode()
                if kind != 'blob':
                    findings.append((path, ['unreviewed submodule'])); continue
                key = (oid, path)
                if key not in seen: entries.append((oid, path)); seen.add(key)
    for oid, path in entries:
        data = git('cat-file', 'blob', oid) if oid else (git('show', ':' + path) if staged else __import__('pathlib').Path(path).read_bytes())
        issues = inspect_file(path, data); checked += 1
        # Historical public repository identity is not a credential; new snapshots must be neutral.
        if history and path == 'config/integrations.json':
            try:
                if json.loads(data) == {'github_repository':'ArmandoSNHU/TechOpsagent','grafana_url':None,'loki_url':None}:
                    issues = [i for i in issues if i != 'operator configuration']
            except ValueError: pass
        if issues: findings.append((path, issues))
    for path, issues in findings: print(path + ': ' + ', '.join(issues))
    print(f'Publication guard: {checked} file versions checked; {len(findings)} findings')
    return bool(findings)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--history', action='store_true')
    args = parser.parse_args()
    try: raise SystemExit(scan(args.staged, args.history))
    except (OSError, subprocess.CalledProcessError):
        raise SystemExit('Publication guard could not complete; publication blocked') from None

if __name__ == '__main__': main()
