"""Windows-only local Grafana/Loki lab. Installation and startup are explicit."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import socket
import subprocess
import time
import tarfile
import urllib.request
import zipfile
from techops.settings import load_settings,save_settings
from techops.diagnostics import probe_service

ROOT=Path(__file__).resolve().parents[1]
WINDOWS=os.name=='nt'
GRAFANA_VERSION='13.2.2'
LOKI_VERSION='3.7.8'

def install(root=ROOT):
    folder=root/'data/observability';folder.mkdir(parents=True,exist_ok=True)
    grafana=folder/'grafana'/('grafana-'+GRAFANA_VERSION)/'bin/grafana.exe'
    if not grafana.exists():
        archive=folder/'grafana.tar.gz'
        urllib.request.urlretrieve('https://dl.grafana.com/grafana/release/13.2.2/grafana_13.2.2_34846740809_windows_amd64.tar.gz',archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest()!='3372d0577aa271b7d724fba7e402bc90f49653f86827900fea4a12ad67b46da5':raise RuntimeError('Grafana checksum mismatch')
        with tarfile.open(archive) as tar:tar.extractall(folder/'grafana',filter='data')
    if not (folder/'loki/loki-windows-amd64.exe').exists():
        base='https://github.com/grafana/loki/releases/download/v'+LOKI_VERSION+'/'
        name='loki-windows-amd64.exe.zip'
        sums=urllib.request.urlopen(base+'SHA256SUMS',timeout=30).read().decode()
        expected=next(line.split()[0] for line in sums.splitlines() if line.split()[-1].lstrip('*')==name)
        archive=folder/name;urllib.request.urlretrieve(base+name,archive)
        if hashlib.sha256(archive.read_bytes()).hexdigest()!=expected:raise RuntimeError('Loki checksum mismatch')
        target=(folder/'loki').resolve()
        with zipfile.ZipFile(archive) as z:
            if any(not (target/n).resolve().is_relative_to(target) for n in z.namelist()):raise RuntimeError('Unsafe archive path')
            z.extractall(target)
    print('Official Windows binaries available under ignored data/observability.')

def prepare(root=ROOT):
    folder=root/'data/observability';folder.mkdir(parents=True,exist_ok=True)
    for name in ('grafana-data','grafana-logs','plugins','loki-data'):
        (folder/name).mkdir(parents=True,exist_ok=True)
    env_path=root/'.env'
    expected=env_path.read_bytes() if env_path.exists() else None
    values=load_settings(env_path,{})
    for key,value in [('GRAFANA_URL','http://127.0.0.1:3000'),('LOKI_URL','http://127.0.0.1:3100')]:
        if values[key] and values[key]!=value:raise ValueError('Existing service configuration differs; preserve it and configure the local lab separately')
        values[key]=value
    if not values['GRAFANA_ADMIN_PASSWORD']:values['GRAFANA_ADMIN_PASSWORD']=secrets.token_urlsafe(32)
    save_settings(env_path,values,expected)
    data=(folder/'loki-data').as_posix()
    (folder/'loki.yaml').write_text(f'''auth_enabled: false
server:
  http_listen_address: 127.0.0.1
  http_listen_port: 3100
  grpc_listen_address: 127.0.0.1
  grpc_listen_port: 9096
common:
  instance_addr: 127.0.0.1
  path_prefix: {data}
  storage:
    filesystem:
      chunks_directory: {data}/chunks
      rules_directory: {data}/rules
  replication_factor: 1
  ring:
    kvstore:
      store: inmemory
schema_config:
  configs:
    - from: 2024-01-01
      store: tsdb
      object_store: filesystem
      schema: v13
      index:
        prefix: index_
        period: 24h
analytics:
  reporting_enabled: false
''',encoding='utf-8')
    provisioning=folder/'provisioning/datasources';provisioning.mkdir(parents=True,exist_ok=True)
    (provisioning/'loki.yaml').write_text('''apiVersion: 1
datasources:
  - name: Local Loki
    uid: techops-loki
    type: loki
    access: proxy
    url: http://127.0.0.1:3100
    isDefault: true
    editable: false
''',encoding='utf-8')
    dashboards=folder/'dashboards';dashboards.mkdir(exist_ok=True)
    providers=folder/'provisioning/dashboards';providers.mkdir(exist_ok=True)
    (providers/'local.yaml').write_text(f'''apiVersion: 1
providers:
  - name: TechOpsagent lab
    type: file
    updateIntervalSeconds: 10
    options:
      path: {dashboards.as_posix()}
''',encoding='utf-8')
    dashboard={'uid':'techops-local-lab','title':'TechOpsagent synthetic evidence','schemaVersion':39,'version':1,
        'tags':['synthetic','local-lab'],'timezone':'browser','time':{'from':'now-15m','to':'now'},'refresh':'10s',
        'panels':[{'id':1,'type':'logs','title':'Synthetic checkout events - no production data',
            'gridPos':{'x':0,'y':0,'w':24,'h':15},'datasource':{'type':'loki','uid':'techops-loki'},
            'targets':[{'refId':'A','expr':'{service_name="checkout",environment="synthetic-lab"}',
                        'datasource':{'type':'loki','uid':'techops-loki'}}],
            'options':{'showTime':True,'sortOrder':'Descending','wrapLogMessage':True}}]}
    (dashboards/'techops.json').write_text(json.dumps(dashboard,indent=2),encoding='utf-8')
    (folder/'grafana.ini').write_text(f'''[server]
http_addr = 127.0.0.1
http_port = 3000
[paths]
data = {(folder/'grafana-data').as_posix()}
logs = {(folder/'grafana-logs').as_posix()}
plugins = {(folder/'plugins').as_posix()}
provisioning = {(folder/'provisioning').as_posix()}
[security]
admin_user = techops
[auth.anonymous]
enabled = true
org_role = Viewer
[users]
allow_sign_up = false
[analytics]
reporting_enabled = false
check_for_updates = false
check_for_plugin_updates = false
[news]
news_feed_enabled = false
''',encoding='utf-8')
    return values

def wait_ready(name,port,seconds=300,process=None):
    deadline=time.monotonic()+seconds
    while True:
        if process is not None and process.poll() is not None:return False
        result=probe_service(name,port)
        if result['status']=='healthy':return True
        if result['status']=='unexpected_response' or time.monotonic()>=deadline:return False
        time.sleep(min(2,max(0,deadline-time.monotonic())))

def start(root=ROOT,wait_seconds=300):
    if not WINDOWS:raise RuntimeError('This launcher requires Windows')
    folder=root/'data/observability'
    home=folder/'grafana'/('grafana-'+GRAFANA_VERSION)
    commands=[('loki',3100,[str(folder/'loki/loki-windows-amd64.exe'),'-config.file='+str(folder/'loki.yaml')]),
              ('grafana',3000,[str(home/'bin/grafana.exe'),'server','--homepath',str(home),'--config',str(folder/'grafana.ini')])]
    processes={}
    for name,port,command in commands:
        if not Path(command[0]).is_file():raise RuntimeError('Local lab binaries missing; run setup.ps1 -InstallLab first')
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex(('127.0.0.1',port))==0 and probe_service(name,port)['status'] not in {'healthy','starting'}:
                raise RuntimeError(f'Port {port} does not identify as {name}; no existing process was changed')
    values=prepare(root)
    for name,port,command in commands:
        with socket.socket() as probe:
            probe.settimeout(1)
            if probe.connect_ex(('127.0.0.1',port))==0:
                print(f'{name}: existing service detected on loopback port {port}; checking readiness.',flush=True);continue
        environment=dict(os.environ)
        if name=='grafana':environment['GF_SECURITY_ADMIN_PASSWORD']=values['GRAFANA_ADMIN_PASSWORD']
        with (folder/(name+'.log')).open('ab') as output,(folder/(name+'-error.log')).open('ab') as error:
            process=subprocess.Popen(command,cwd=root,env=environment,stdout=output,stderr=error,creationflags=subprocess.CREATE_NO_WINDOW)
            processes[name]=process
        print(f'{name}: started PID {process.pid} on loopback port {port}; waiting for readiness.',flush=True)
    for name,port,_ in commands:
        if not wait_ready(name,port,wait_seconds,processes.get(name)):
            raise RuntimeError(f'{name} is not ready within the wait limit. Check data/observability/{name}.log; first-run migrations may still be running')
        print(f'{name}: HEALTHY at http://127.0.0.1:{port}',flush=True)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install',action='store_true');parser.add_argument('--start',action='store_true');args=parser.parse_args()
    try:
        if args.install:install()
        if args.start:start()
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from None
    except (OSError,ValueError):
        raise SystemExit('Local lab setup did not complete. Check binaries, configured URLs, port ownership and ignored runtime logs. No secret values displayed.') from None
    if not (args.install or args.start):print('Dry run: local Grafana 3000 and Loki 3100. Use --install for downloads; --start for local runtime/configuration.')

if __name__=='__main__':main()
