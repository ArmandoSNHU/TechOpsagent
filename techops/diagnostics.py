"""Secret-free setup checks. Optional live checks contact fixed loopback services only."""
import argparse
import http.client
from importlib import metadata
import json
from pathlib import Path
import subprocess
import sys
from techops.settings import load_settings,validate_settings
from techops.runtime import build_id,ROOT

def probe_service(name,port,expected_build=None):
    if name not in {'app','grafana','loki'} or type(port) is not int or not 1<=port<=65535:raise ValueError('Invalid local service probe')
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=2)
    path='/ready' if name=='loki' else '/api/health'
    try:
        connection.request('GET',path)
        response=connection.getresponse()
        if response.status==503:return {'status':'starting','action':'Wait for first-run initialization, then check again.'}
        if response.status!=200:return {'status':'unexpected_response','action':'Check which process owns the port; no redirect was followed.'}
        raw=response.read(4097)
        if len(raw)>4096:raise ValueError()
        if name=='loki':valid=raw.strip()==b'ready'
        else:
            value=json.loads(raw)
            valid=isinstance(value,dict) and (value.get('database')=='ok' and isinstance(value.get('version'),str) if name=='grafana' else value.get('status')=='ok' and value.get('framework')=='fastapi')
            if valid and name=='app' and expected_build and value.get('build_id')!=expected_build:
                return {'status':'stale','action':'Stop the verified old preview and run setup.ps1 -Run again.'}
        return {'status':'healthy' if valid else 'unexpected_response'}
    except (OSError,http.client.HTTPException):return {'status':'unavailable','action':'Start the service, or inspect its local log if startup failed.'}
    except (ValueError,UnicodeError):return {'status':'unexpected_response','action':'The listener did not return the expected health response.'}
    finally:connection.close()

def inspect_setup(root=ROOT,live=False,port=8765):
    report={'python':{'version':'.'.join(map(str,sys.version_info[:3])),'supported':sys.version_info>=(3,12)},
            'environment_file':(root/'.env').exists(),'dependencies':{},'integrations':{},'services':{}}
    manifest=root/'requirements.txt'
    if manifest.exists():
        for line in manifest.read_text(encoding='utf-8').splitlines():
            if '==' not in line:continue
            name,expected=line.strip().split('==',1)
            try:actual=metadata.version(name)
            except metadata.PackageNotFoundError:actual=None
            report['dependencies'][name]='ok' if actual==expected else ('missing' if actual is None else 'version_mismatch')
    else:report['dependencies']['requirements.txt']='missing'
    try:
        values=load_settings(root/'.env');validate_settings(values);report['configuration']='valid'
    except (ValueError,OSError):
        values={};report['configuration']='invalid (values hidden; use private setup to correct .env)'
    for name in ('github','grafana','loki','servicenow'):
        prefix=name.upper();required=prefix+('_REPOSITORY' if name=='github' else '_URL')
        present=bool(values.get(required));related=any(v for k,v in values.items() if k.startswith(prefix+'_'))
        if name=='servicenow':present=present and bool(values.get('SERVICENOW_TOKEN') or (values.get('SERVICENOW_USERNAME') and values.get('SERVICENOW_PASSWORD')))
        report['integrations'][name]='configured' if present else ('incomplete' if related else 'optional_not_configured')
    try:
        result=subprocess.run(['git','config','--get','core.hooksPath'],cwd=root,capture_output=True,text=True,timeout=3)
        report['publication_hook']='enabled' if result.stdout.strip()=='.githooks' else 'not_enabled'
    except (OSError,subprocess.SubprocessError):report['publication_hook']='git_unavailable'
    if live:
        report['services']['app']=probe_service('app',port,expected_build=build_id(root))
        for name,service_port in [('grafana',3000),('loki',3100)]:
            url=values.get(name.upper()+'_URL','').rstrip('/')
            if url in {f'http://127.0.0.1:{service_port}',f'http://localhost:{service_port}'}:
                report['services'][name]=probe_service(name,service_port)
            else:report['services'][name]={'status':'not_probed','action':'No configured standard loopback endpoint; no external request made.'}
    report['core_ready']=report['python']['supported'] and report['configuration']=='valid' and all(v=='ok' for v in report['dependencies'].values())
    return report

def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--live',action='store_true');parser.add_argument('--json',action='store_true');parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args(argv)
    if not 1<=args.port<=65535:parser.error('Port must be 1-65535')
    report=inspect_setup(live=args.live,port=args.port)
    if args.json:print(json.dumps(report,indent=2))
    else:
        print('TechOpsagent setup check')
        print('Core environment: '+('READY' if report['core_ready'] else 'NEEDS ATTENTION'))
        print('Python: '+report['python']['version']+' | .env: '+('present' if report['environment_file'] else 'absent (optional)'))
        print('Configuration: '+report['configuration'])
        for name,status in report['dependencies'].items():
            if status!='ok':print('Dependency '+name+': '+status+'; run setup.ps1 -Install')
        for name,status in report['integrations'].items():print(name+': '+status)
        for name,value in report['services'].items():print(name+' runtime: '+value['status']+(' - '+value['action'] if 'action' in value else ''))
        print('Pre-push hook: '+report['publication_hook'])
        print('Next: setup.ps1 -Configure -Service <name>, -Check -Live, or -Run. No secret values were displayed.')
    if not report['core_ready'] or any(value['status'] not in {'healthy','not_probed'} for value in report['services'].values()):raise SystemExit(1)

if __name__=='__main__':main()
