"""Real loopback Uvicorn fixture without external test-client packages."""
import socket
import threading
import time
import uvicorn
from techops.server import create_app

class LiveServer:
    def __init__(self, database):
        self.socket = socket.socket()
        self.socket.bind(('127.0.0.1',0))
        self.port = self.socket.getsockname()[1]
        self.server = uvicorn.Server(uvicorn.Config(create_app(database),host='127.0.0.1',port=self.port,
                    log_level='error',access_log=False,proxy_headers=False,ws='none'))
        self.thread = threading.Thread(target=self.server.run,kwargs={'sockets':[self.socket]},daemon=True)
    def start(self):
        self.thread.start()
        deadline=time.monotonic()+5
        while not self.server.started:
            if not self.thread.is_alive() or time.monotonic()>deadline:
                self.close()
                raise RuntimeError('Test server did not start')
            time.sleep(.01)
    def close(self):
        self.server.should_exit=True
        self.thread.join(5)
        self.socket.close()
        if self.thread.is_alive(): raise RuntimeError('Test server did not stop')
