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
            with patch('techops.settings.ENV_PATH',p), patch('builtins.input',side_effect=['sample/project','','','','']), patch('getpass.getpass',return_value='fixture-only') as hidden, patch('sys.stdout',new_callable=io.StringIO) as output:
                main([])
                self.assertEqual(hidden.call_count,6)
                self.assertNotIn('fixture-only',output.getvalue())
            self.assertEqual(load_settings(p,{})['GITHUB_TOKEN'],'fixture-only')

    def test_edit_one_service_preserves_other_credentials_and_hides_existing(self):
        from unittest.mock import patch
        import io
        from techops.settings import main
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env';write_settings(p,{'GITHUB_REPOSITORY':'sample/project','GITHUB_TOKEN':'fixture','LOKI_URL':'http://127.0.0.1:3100'})
            with patch('techops.settings.ENV_PATH',p),patch('builtins.input',return_value='other/project'),patch('getpass.getpass',return_value=''),patch('sys.stdout',new_callable=io.StringIO) as output:
                main(['--edit','--service','github'])
                self.assertNotIn('fixture',output.getvalue());self.assertNotIn('sample/project',output.getvalue())
            values=load_settings(p,{})
            self.assertEqual(values['GITHUB_REPOSITORY'],'other/project');self.assertEqual(values['GITHUB_TOKEN'],'fixture')
            self.assertEqual(values['LOKI_URL'],'http://127.0.0.1:3100')
    def test_explicit_clear_and_invalid_edit_preserves_original(self):
        from unittest.mock import patch
        from techops.settings import main
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env';write_settings(p,{'GITHUB_REPOSITORY':'sample/project','GITHUB_TOKEN':'fixture'})
            with patch('techops.settings.ENV_PATH',p),patch('builtins.input',return_value=''),patch('getpass.getpass',return_value='-'):
                main(['--edit','--service','github'])
            self.assertEqual(load_settings(p,{})['GITHUB_TOKEN'],'')
            before=p.read_bytes()
            with patch('techops.settings.ENV_PATH',p),patch('builtins.input',return_value='bad/path/extra'),patch('getpass.getpass',return_value=''):
                with self.assertRaises(SystemExit):main(['--edit','--service','github'])
            self.assertEqual(before,p.read_bytes())
    def test_concurrent_edit_is_not_overwritten(self):
        from techops.settings import save_settings
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'.env';write_settings(p,{})
            before=p.read_bytes();p.write_text('GITHUB_REPOSITORY=other/project')
            with self.assertRaises(RuntimeError):save_settings(p,{},expected=before)
            self.assertIn('other/project',p.read_text())
