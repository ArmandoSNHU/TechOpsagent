import http.client
import json
from pathlib import Path
import tempfile
import threading
import unittest
from techops.server import create_app, ROUTES
from tests.support import LiveServer
from techops.store import Store
from techops.engine import investigate

class ApiTests(unittest.TestCase):
    def test_dns_validated_target_is_passed_as_data(self):
        from unittest.mock import patch
        with patch('techops.toolkit_routes.collect_dns', return_value={'tool':'dns','hostname':'example.com','readings':[]}) as run:
            status, _, body = self.request('POST','/api/tools/run',json.dumps({'tool':'dns','hostname':'Example.COM.'}),{'Content-Type':'application/json'})
            self.assertEqual(status,200)
            run.assert_called_once_with('example.com')

    def test_dns_rejects_missing_or_unsafe_targets(self):
        from unittest.mock import patch
        with patch('techops.toolkit_routes.collect_dns') as run:
            for value in [{'tool':'dns'}, {'tool':'dns','hostname':'https://example.com'}, {'tool':'dns','hostname':'example.com;whoami'}, {'tool':'dns','hostname':42}, {'tool':'network','hostname':'example.com'}, {'tool':'dns','hostname':'example.com','server':'192.0.2.53'}]:
                self.assertEqual(self.request('POST','/api/tools/run',json.dumps(value),{'Content-Type':'application/json'})[0],400)
            run.assert_not_called()

    def test_toolkit_catalog_and_explicit_assets(self):
        status, _, body = self.request('GET', '/api/tools/catalog')
        self.assertEqual(status, 200)
        self.assertEqual(len(json.loads(body)['categories']), 5)
        for route in ['/toolkit.js', '/investigation.js', '/toolkit.css', '/incidents']:
            self.assertEqual(self.request('GET', route)[0], 200)
        self.assertIn('data-mode="local"', self.request('GET', '/')[2].decode())

    def test_toolkit_run_uses_fixed_tool_and_keeps_readings_private(self):
        from unittest.mock import patch
        with patch('techops.toolkit_routes.collect', return_value={'tool': 'network', 'mode': 'local', 'readings': []}) as run:
            status, headers, body = self.request('POST', '/api/tools/run', '{"tool":"network"}', {'Content-Type': 'application/json'})
            self.assertEqual(status, 200)
            run.assert_called_once_with('network')
            self.assertIn('no-store', headers['cache-control'])

    def test_toolkit_rejects_unimplemented_and_injected_tools(self):
        from unittest.mock import patch
        with patch('techops.toolkit_routes.collect') as run:
            for body in [{'tool': 'dns'}, {'tool': 'network;whoami'}, {'tool': 'network', 'command': 'anything'}]:
                self.assertEqual(self.request('POST', '/api/tools/run', json.dumps(body), {'Content-Type': 'application/json'})[0], 400)
            run.assert_not_called()

    def test_toolkit_busy_does_not_start_second_collector(self):
        from unittest.mock import patch
        with patch('techops.toolkit_routes._collection_lock') as lock, patch('techops.toolkit_routes.collect') as run:
            lock.acquire.return_value = False
            self.assertEqual(self.request('POST', '/api/tools/run', '{"tool":"network"}', {'Content-Type': 'application/json'})[0], 409)
            run.assert_not_called()
            lock.release.assert_not_called()

    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.temp.name)/'test.sqlite3'
        cls.server = LiveServer(cls.db)
        cls.server.start()
    @classmethod
    def tearDownClass(cls):
        cls.server.close(); cls.temp.cleanup()
    def request(self, method, path, body=None, headers=None):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.port, timeout=3)
        connection.request(method, path, body, headers or {})
        response = connection.getresponse()
        result = (response.status, response.headers, response.read())
        connection.close()
        return result
    def post(self, value, **headers):
        return self.request('POST','/api/investigate',json.dumps(value),{'Content-Type':'application/json',**headers})
    def test_integration_status_has_no_tokens(self):
        status,_,body=self.request('GET','/api/integrations')
        self.assertEqual(status,200)
        self.assertEqual(json.loads(body)['github']['repository'],'sample/project')
        self.assertNotIn('token',body.decode().lower())
        self.assertNotIn('fixture',body.decode())
    def test_private_files_are_not_served(self):
        for path in ['/.env','/.env.example','/config/integrations.json','/data/incidents.sqlite3']:
            with self.subTest(path=path):self.assertEqual(self.request('GET',path)[0],404)
    def test_github_read_uses_configured_repository(self):
        from unittest.mock import patch
        with patch('techops.integration_routes.GitHubIssues.list_issues',return_value={'tickets':[],'read_only':True}) as read:
            status,_,body=self.request('POST','/api/integrations/github/read','{"page":1}',{'Content-Type':'application/json'})
            self.assertEqual(status,200)
            self.assertTrue(json.loads(body)['read_only'])
            read.assert_called_once_with(page=1,per_page=20)
    def test_servicenow_unconfigured_and_draft_preview(self):
        self.assertEqual(self.request('POST','/api/integrations/servicenow/read','{}',{'Content-Type':'application/json'})[0],409)
        status,_,body=self.post({'scenario':'api_error'})
        record=json.loads(body)
        status,_,body=self.request('GET','/api/incidents/'+record['id']+'/servicenow-preview')
        self.assertEqual(status,200);self.assertTrue(json.loads(body)['dry_run'])
        self.assertFalse(json.loads(body)['remote_write'])
        self.assertEqual(self.request('GET','/api/incidents/missing/servicenow-preview')[0],404)
    def test_unconfigured_loki_is_explicit(self):
        status,_,body=self.request('POST','/api/integrations/loki/analyze','{"service":"checkout","minutes":15}',{'Content-Type':'application/json'})
        self.assertEqual(status,409)
        self.assertIn('not configured',json.loads(body)['error'])
    def test_health(self):
        status,_,body=self.request('GET','/api/health')
        self.assertEqual(status,200); self.assertEqual(json.loads(body)['mode'],'simulated')
    def test_ai_preview_is_offline(self):
        record=json.loads(self.post({'scenario':'api_error'})[2])
        status,_,body=self.request('GET','/api/incidents/'+record['id']+'/ai-preview')
        self.assertEqual(status,200)
        self.assertTrue(json.loads(body)['dry_run'])
        self.assertFalse(json.loads(body)['inference_enabled'])
    def test_live_lab_api(self):
        status,_,body=self.request('POST','/api/lab/investigate',json.dumps({'scenario':'dependency_timeout'}),{'Content-Type':'application/json'})
        self.assertEqual(status,201)
        self.assertEqual(json.loads(body)['cause'],'Dependency timeout')
        self.assertEqual(json.loads(body)['environment'],'local_fault_lab')
    def test_log_intake_api(self):
        log=json.dumps({'kind':'http','source':'partner','status':401,'detail':'token expired'})
        status,_,body=self.request('POST','/api/analyze',json.dumps({'log_text':log}),{'Content-Type':'application/json'})
        self.assertEqual(status,201)
        self.assertEqual(json.loads(body)['cause'],'Credential rejected')
    def test_bad_log_intake(self):
        status,_,_=self.request('POST','/api/analyze',json.dumps({'log_text':'not JSON'}),{'Content-Type':'application/json'})
        self.assertEqual(status,400)
    def test_health_identifies_started_source(self):
        from techops.runtime import build_id
        value=json.loads(self.request('GET','/api/health')[2])
        self.assertEqual(value['build_id'],build_id())
    def test_fastapi_health_and_openapi(self):
        self.assertEqual(json.loads(self.request('GET','/api/health')[2])['framework'],'fastapi')
        status,_,body=self.request('GET','/openapi.json')
        self.assertEqual(status,200)
        self.assertIn('/api/investigate',json.loads(body)['paths'])
    def test_security_headers_on_errors(self):
        status,headers,_=self.post({'scenario':'invalid'})
        self.assertEqual(status,400)
        self.assertEqual(headers['X-Content-Type-Options'],'nosniff')
    def test_same_origin_accepted(self):
        self.assertEqual(self.post({'scenario':'api_error'},Origin=f'http://127.0.0.1:{self.server.port}')[0],201)
    def test_scenarios(self):
        self.assertEqual(len(json.loads(self.request('GET','/api/scenarios')[2])),3)
    def test_investigate_persist_and_download(self):
        status,_,body=self.post({'scenario':'api_error','ticket':'password=secretvalue'})
        self.assertEqual(status,201)
        record=json.loads(body)
        self.assertNotIn('secretvalue',str(Store(self.db).get(record['id'])))
        status,headers,report=self.request('GET','/api/incidents/'+record['id']+'/report')
        self.assertEqual(status,200); self.assertIn('attachment',headers['Content-Disposition'])
        self.assertIn(b'Armando Gomez',report)
        self.assertEqual(json.loads(self.request('GET','/api/incidents/'+record['id'])[2])['id'],record['id'])
        self.assertTrue(any(r['id']==record['id'] for r in json.loads(self.request('GET','/api/incidents')[2])))
    def test_invalid_scenario(self):
        self.assertEqual(self.post({'scenario':'bad'})[0],400)
    def test_invalid_types(self):
        for body in [[],{'scenario':[]},{'scenario':'api_error','ticket':{}},{'scenario':'api_error','ticket':'x'*4001}]:
            with self.subTest(body=str(body)[:80]): self.assertEqual(self.post(body)[0],400)
    def test_extra_fields_rejected(self):
        self.assertEqual(self.post({'scenario':'api_error','url':'https://example.com'})[0],400)
    def test_malformed_json(self):
        self.assertEqual(self.request('POST','/api/investigate','{',{'Content-Type':'application/json'})[0],400)
    def test_body_limit(self):
        self.assertEqual(self.request('POST','/api/investigate','x'*17000,{'Content-Type':'application/json'})[0],413)
    def test_cross_origin_rejected(self):
        self.assertEqual(self.post({'scenario':'api_error'},Origin='https://evil.invalid')[0],403)
    def test_untrusted_host_rejected(self):
        self.assertEqual(self.request('GET','/api/health',headers={'Host':'evil.invalid'})[0],403)
    def test_form_post_rejected(self):
        self.assertEqual(self.request('POST','/api/investigate','scenario=api_error',{'Content-Type':'text/plain'})[0],415)
    def test_missing_record(self):
        self.assertEqual(self.request('GET','/api/incidents/missing')[0],404)
    def test_path_traversal_rejected(self):
        self.assertEqual(self.request('GET','/../AGENTS.md')[0],404)
    def test_static_and_security_headers(self):
        for route in ['/','/style.css','/app.js']:
            status,headers,body=self.request('GET',route)
            self.assertEqual(status,200); self.assertTrue(body)
            self.assertIn("frame-ancestors 'none'", headers['Content-Security-Policy'])
    def test_documented_routes(self):
        doc=(Path(__file__).resolve().parents[1]/'docs/API.md').read_text(encoding='utf-8')
        for route in ROUTES: self.assertIn(route, doc)
        schema=create_app(self.db, settings={}).openapi()
        actual={method.upper()+' '+path for path,operations in schema['paths'].items()
                for method in operations if method in {'get','post','put','patch','delete'} and path.startswith('/api/')}
        self.assertEqual(actual | {'GET /openapi.json'},set(ROUTES))

class PersistenceTests(unittest.TestCase):
    def test_reopen_database(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'db.sqlite3'
            incident=investigate('invalid_credential'); Store(path).save(incident)
            self.assertEqual(Store(path).get(incident['id']),incident)
    def test_parameterized_lookup(self):
        with tempfile.TemporaryDirectory() as folder:
            store=Store(Path(folder)/'db.sqlite3'); store.save(investigate('api_error'))
            self.assertIsNone(store.get("' OR 1=1 --"))
