"""Local, literal .env settings. Never execute or interpolate configuration."""
import os
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / '.env'
KEYS = ('GITHUB_REPOSITORY', 'GITHUB_TOKEN', 'GRAFANA_URL', 'GRAFANA_TOKEN', 'LOKI_URL', 'LOKI_TOKEN')

def load_settings(path=None, environ=None):
    path = ENV_PATH if path is None else Path(path)
    values = dict.fromkeys(KEYS, '')
    if path.exists():
        for number, line in enumerate(path.read_text(encoding='utf-8-sig').splitlines(), 1):
            line = line.strip()
            if not line or line.startswith('#'): continue
            name, separator, value = line.partition('=')
            name = name.strip(); value = value.strip()
            if not separator or name not in KEYS:
                raise ValueError(f'Invalid .env setting at line {number}; see .env.example')
            if value.startswith(('"', "'")):
                if len(value) < 2 or value[-1] != value[0]:
                    raise ValueError(f'Invalid .env quoting at line {number}')
                value = value[1:-1]
            values[name] = value
    environment = os.environ if environ is None else environ
    for name in KEYS:
        if name in environment: values[name] = environment[name]
    return values

def write_settings(path, values):
    lines = []
    for name in KEYS:
        value = values.get(name, '')
        if any(c in value for c in '\r\n\x00') or value != value.strip() or value.startswith(('"', "'")):
            raise ValueError('Unsupported setting characters; no file written')
        lines.append(name + '=' + value)
    # Exclusive creation prevents accidentally overwriting existing credentials.
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(descriptor, 'w', encoding='utf-8') as handle:
        handle.write('\n'.join(lines) + '\n')

def main():
    from getpass import getpass
    if ENV_PATH.exists():
        print('.env already exists. Edit it locally; its contents will not be displayed.')
        return
    values = {}
    print('Local integration setup. Leave optional fields blank. No network requests are made.')
    for name in KEYS:
        values[name] = getpass(name + ' (hidden): ') if name.endswith('_TOKEN') else input(name + ': ').strip()
    try:
        from techops.connectors.github import GitHubIssues
        from techops.connectors.http import JsonReader
        if values['GITHUB_REPOSITORY']: GitHubIssues(values['GITHUB_REPOSITORY'])
        for name in ('GRAFANA_URL', 'LOKI_URL'):
            if values[name]: JsonReader(values[name])
        write_settings(ENV_PATH, values)
    except ValueError:
        raise SystemExit('Invalid settings. No .env written; use owner/repository and URLs without credentials.') from None
    print('Saved local .env. Restart the application to apply settings. Do not share this file.')

if __name__ == '__main__': main()
