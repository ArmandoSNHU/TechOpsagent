import asyncio
import tempfile
import unittest
from pathlib import Path
from fastapi import FastAPI
from techops.server import create_app

class FastApiTests(unittest.TestCase):
    def test_factory_and_schema(self):
        with tempfile.TemporaryDirectory() as folder:
            app = create_app(Path(folder)/'db.sqlite3', settings={})
            self.assertIsInstance(app, FastAPI)
            schema = app.openapi()
            self.assertIn('/api/investigate', schema['paths'])
            request = schema['components']['schemas']['InvestigationRequest']
            self.assertFalse(request['additionalProperties'])
            self.assertEqual(request['properties']['ticket']['maxLength'], 4000)
    def test_chunked_body_limit(self):
        with tempfile.TemporaryDirectory() as folder:
            app = create_app(Path(folder)/'db.sqlite3', settings={})
            messages = []
            chunks = iter([{'type':'http.request','body':b'x'*9000,'more_body':True},
                           {'type':'http.request','body':b'x'*9000,'more_body':False}])
            async def receive(): return next(chunks)
            async def send(message): messages.append(message)
            scope = {'type':'http','asgi':{'version':'3.0'},'http_version':'1.1','method':'POST',
                     'scheme':'http','path':'/api/investigate','raw_path':b'/api/investigate',
                     'query_string':b'', 'root_path':'','server':('127.0.0.1',8765),'client':('127.0.0.1',1),
                     'headers':[(b'host',b'127.0.0.1:8765'),(b'content-type',b'application/json')]}
            asyncio.run(app(scope,receive,send))
            self.assertEqual(messages[0]['status'],413)
