"""Local, literal .env settings. Never execute or interpolate configuration."""
import os
import argparse
import secrets
import warnings
from pathlib import Path

ENV_PATH = Path(__file__).resolve().parents[1] / '.env'
KEYS = ('GITHUB_REPOSITORY', 'GITHUB_TOKEN', 'GRAFANA_URL', 'GRAFANA_TOKEN', 'LOKI_URL', 'LOKI_TOKEN', 'SERVICENOW_URL', 'SERVICENOW_TOKEN', 'SERVICENOW_USERNAME', 'SERVICENOW_PASSWORD', 'GRAFANA_ADMIN_PASSWORD')
GROUPS = {'github':KEYS[:2], 'grafana':('GRAFANA_URL','GRAFANA_TOKEN','GRAFANA_ADMIN_PASSWORD'),
          'loki':('LOKI_URL','LOKI_TOKEN'), 'servicenow':KEYS[6:10], 'all':KEYS}

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

def save_settings(path, values, expected=None):
    """Replace only the snapshot that was edited; never keep secret backup files."""
    path=Path(path)
    if path.is_symlink(): raise ValueError('Refusing to replace a symlink')
    if expected is None:
        write_settings(path,values);return
    temporary=path.with_name('.env.'+secrets.token_hex(8))
    try:
        write_settings(temporary,values)
        if not path.exists() or path.read_bytes()!=expected:raise RuntimeError('Settings changed while editing; reload before saving')
        os.replace(temporary,path)
    finally:
        if temporary.exists():temporary.unlink()

def validate_settings(values):
    from techops.connectors.github import GitHubIssues
    from techops.connectors.http import JsonReader
    from techops.connectors.servicenow import ServiceNow
    if values.get('GITHUB_REPOSITORY'): GitHubIssues(values['GITHUB_REPOSITORY'])
    for prefix in ('GRAFANA','LOKI'):
        if values.get(prefix+'_URL'): JsonReader(values[prefix+'_URL'],token=values.get(prefix+'_TOKEN'))
    if values.get('SERVICENOW_URL'):
        ServiceNow(values['SERVICENOW_URL'],token=values.get('SERVICENOW_TOKEN'),username=values.get('SERVICENOW_USERNAME'),password=values.get('SERVICENOW_PASSWORD'))

def main(argv=None):
    from getpass import getpass,GetPassWarning
    parser=argparse.ArgumentParser(description='Private local settings; no network calls or model startup.')
    parser.add_argument('--edit',action='store_true',help='Edit an existing file; Enter keeps a value and - clears it')
    parser.add_argument('--service',choices=GROUPS,default='all')
    args=parser.parse_args(argv)
    if ENV_PATH.exists() and not args.edit:
        print('.env already exists. Use --edit --service github|grafana|loki|servicenow to change it privately.');return
    try:
        expected=ENV_PATH.read_bytes() if ENV_PATH.exists() else None
        values=load_settings(ENV_PATH,{})
        print('Local integration setup. Enter keeps existing values; - clears a field. Nothing is sent.')
        with warnings.catch_warnings():
            warnings.simplefilter('error',GetPassWarning)
            for name in GROUPS[args.service]:
                status='set' if values[name] else 'empty'
                prompt=f'{name} [{status}]: '
                value=getpass(prompt) if name.endswith(('_TOKEN','_PASSWORD')) else input(prompt).strip()
                if value=='-':values[name]=''
                elif value:values[name]=value
        validate_settings(values)
        save_settings(ENV_PATH,values,expected)
    except (EOFError,KeyboardInterrupt,GetPassWarning):
        raise SystemExit('Setup cancelled or hidden input unavailable. No settings saved; use an interactive terminal.') from None
    except (ValueError,OSError,RuntimeError):
        raise SystemExit('Settings were not saved. Check field formats/authentication choice and reload if the file changed.') from None
    print('Saved local .env. Restart the application to apply settings. Do not share this file.')

if __name__ == '__main__': main()
