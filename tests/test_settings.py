import tempfile
import unittest
from pathlib import Path
from techops.settings import load_settings, write_settings

class SettingsTests(unittest.TestCase):
    def test_clean_install_is_unconfigured(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(all(not v for v in load_settings(Path(d)/'.env',{}).values()))
    def test_literal_env_and_environment_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env'
            p.write_text('GITHUB_REPOSITORY=sample/project\nGITHUB_TOKEN="literal-$VALUE"\n',encoding='utf-8')
            values=load_settings(p,{'GITHUB_REPOSITORY':'other/project'})
            self.assertEqual(values['GITHUB_REPOSITORY'],'other/project')
            self.assertEqual(values['GITHUB_TOKEN'],'literal-$VALUE')
    def test_invalid_env_does_not_echo_secret(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env';p.write_text('secret-value-without-equals',encoding='utf-8')
            with self.assertRaises(ValueError) as error:load_settings(p,{})
            self.assertNotIn('secret-value',str(error.exception))
    def test_writer_refuses_overwrite_and_newline(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env'
            with self.assertRaises(ValueError):write_settings(p,{'GITHUB_TOKEN':'a\nb'})
            self.assertFalse(p.exists())
            write_settings(p,{'GITHUB_REPOSITORY':'sample/project'})
            with self.assertRaises(FileExistsError):write_settings(p,{})
    def test_example_contains_only_empty_values(self):
        values=load_settings(Path(__file__).resolve().parents[1]/'.env.example',{})
        self.assertTrue(all(not v for v in values.values()))

    def test_fresh_install_api_disables_integrations(self):
        import http.client, json
        from tests.support import LiveServer
        with tempfile.TemporaryDirectory() as d:
            server=LiveServer(Path(d)/'test.sqlite3', settings={});server.start()
            try:
                conn=http.client.HTTPConnection('127.0.0.1',server.port)
                conn.request('GET','/api/integrations');response=conn.getresponse();body=json.loads(response.read())
                self.assertEqual(response.status,200)
                self.assertFalse(any(body[k]['configured'] for k in ['github','grafana','loki']))
                conn.request('GET','/api/integrations/github/preview');response=conn.getresponse();response.read()
                self.assertEqual(response.status,409);conn.close()
            finally:server.close()
    def test_setup_hides_tokens_and_never_prints_them(self):
        from unittest.mock import patch
        import io
        from techops.settings import main
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env'
            with patch('techops.settings.ENV_PATH',p), patch('builtins.input',side_effect=['sample/project','','']), patch('getpass.getpass',return_value='fixture-only') as hidden, patch('sys.stdout',new_callable=io.StringIO) as output:
                main()
                self.assertEqual(hidden.call_count,3)
                self.assertNotIn('fixture-only',output.getvalue())
            self.assertEqual(load_settings(p,{})['GITHUB_TOKEN'],'fixture-only')
