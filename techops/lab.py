"""Disposable loopback fault lab. No caller-supplied hosts or URLs."""
from contextlib import contextmanager
from datetime import datetime, timezone
import http.client
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import socket
import threading
import time

FIXTURES = {
    '/checkout': (500, 'KeyError: TAX_REGION'),
    '/inventory': (504, 'upstream read timeout'),
    '/partner': (401, 'invalid_token: token expired'),
    '/healthy': (200, 'service healthy'),
    '/slow': (200, 'delayed response'),
    '/redirect': (302, 'redirect blocked by client'),
}
SCENARIO_PATHS = {'api_error':'/checkout','dependency_timeout':'/inventory','invalid_credential':'/partner'}

class FaultHandler(BaseHTTPRequestHandler):
    def log_message(self, *args): pass
    def do_GET(self):
        code, detail = FIXTURES.get(self.path,(404,'unknown fixture'))
        if self.path == '/slow': time.sleep(.15)
        payload=json.dumps({'detail':detail}).encode()
        try:
            self.send_response(code)
            self.send_header('Content-Type','application/json')
            self.send_header('Content-Length',str(len(payload)))
            if code == 302: self.send_header('Location','https://example.invalid/never-follow')
            self.end_headers()
            self.wfile.write(payload)
        except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError): pass

@contextmanager
def fault_lab():
    server=ThreadingHTTPServer(('127.0.0.1',0),FaultHandler)
    thread=threading.Thread(target=server.serve_forever,kwargs={'poll_interval':.01},daemon=True)
    thread.start()
    try: yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(2)

def probe(port, path, timeout=1.0):
    if path not in FIXTURES or not isinstance(port,int) or not 1 <= port <= 65535:
        raise ValueError('Only fixed lab paths and valid local ports are allowed')
    if not 0 < timeout <= 2: raise ValueError('Timeout must be at most 2 seconds')
    start=time.monotonic()
    connection=http.client.HTTPConnection('127.0.0.1',port,timeout=timeout)
    record={'source':'loopback '+path,'observed_at':datetime.now(timezone.utc).isoformat()}
    try:
        connection.request('GET',path)
        response=connection.getresponse()
        data=response.read(65537)
        if len(data)>65536: raise ValueError('Response exceeds limit')
        record.update(kind='redirect_rejected' if 300 <= response.status < 400 else 'http',
                      status=response.status,detail=json.loads(data).get('detail',''))
    except (TimeoutError,socket.timeout):
        record.update(kind='timeout',status=None,detail='Read deadline exceeded')
    except (OSError,http.client.HTTPException,ValueError):
        record.update(kind='probe_error',status=None,detail='Local probe failed')
    finally: connection.close()
    record['elapsed_ms']=round((time.monotonic()-start)*1000,2)
    return record

def collect(scenario):
    if scenario not in SCENARIO_PATHS: raise ValueError('Unknown scenario')
    with fault_lab() as port:
        observations=[probe(port,SCENARIO_PATHS[scenario]),probe(port,'/healthy')]
    try:
        answers=socket.getaddrinfo('localhost',None,family=socket.AF_INET,type=socket.SOCK_STREAM)
        addresses={item[4][0] for item in answers}
        detail='localhost resolved to loopback' if addresses == {'127.0.0.1'} else 'Unexpected localhost resolution'
    except OSError: detail='localhost lookup failed'
    observations.append({'kind':'dns','source':'local resolver','status':None,'detail':detail,
                         'observed_at':datetime.now(timezone.utc).isoformat()})
    return observations
