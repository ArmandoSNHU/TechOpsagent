import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from techops.diagnostics import inspect_setup,probe_service
from techops.runtime import build_id

class SetupTests(unittest.TestCase):
    def test_offline_report_never_connects_or_exposes_values(self):
        from techops.settings import write_settings
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_settings(root/'.env',{'GITHUB_TOKEN':'fixture','SERVICENOW_URL':'https://private.example.com'})
            with patch('http.client.HTTPConnection') as conn:
                report=inspect_setup(root,live=False)
                conn.assert_not_called()
            self.assertNotIn('private.example.com',str(report));self.assertNotIn('fixture',str(report))
            self.assertEqual(report['integrations']['servicenow'],'incomplete')
    def test_fingerprint_changes_with_source_not_private_env(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'techops').mkdir();p=root/'techops/server.py';p.write_text('first')
            first=build_id(root);(root/'.env').write_text('private');self.assertEqual(first,build_id(root))
            p.write_text('second');self.assertNotEqual(first,build_id(root))
    def test_probe_does_not_follow_redirects(self):
        with patch('techops.diagnostics.http.client.HTTPConnection') as conn:
            conn.return_value.getresponse.return_value.status=302
            self.assertEqual(probe_service('app',8765)['status'],'unexpected_response')
            conn.return_value.request.assert_called_once()
    def test_stale_app_is_reported(self):
        with patch('techops.diagnostics.http.client.HTTPConnection') as conn:
            response=conn.return_value.getresponse.return_value;response.status=200
            response.read.return_value=b'{"status":"ok","framework":"fastapi","build_id":"old"}'
            self.assertEqual(probe_service('app',8765,expected_build='new')['status'],'stale')
    def test_readiness_rejects_wrong_service(self):
        with patch('techops.diagnostics.http.client.HTTPConnection') as conn:
            response=conn.return_value.getresponse.return_value;response.status=200;response.read.return_value=b'{"status":"ok"}'
            self.assertEqual(probe_service('grafana',3000)['status'],'unexpected_response')

    def test_fresh_server_has_matching_build(self):
        from tests.support import LiveServer
        with tempfile.TemporaryDirectory() as d:
            server=LiveServer(Path(d)/'db.sqlite3',settings={});server.start()
            try:self.assertEqual(probe_service('app',server.port,expected_build=build_id())['status'],'healthy')
            finally:server.close()
    def test_powershell_help_and_missing_environment_are_safe(self):
        import shutil,subprocess
        shell=shutil.which('pwsh') or shutil.which('powershell')
        if not shell:self.skipTest('PowerShell not installed')
        source=Path(__file__).resolve().parents[1]/'setup.ps1'
        with tempfile.TemporaryDirectory(prefix='techops setup ') as d:
            script=Path(d)/'setup.ps1';shutil.copyfile(source,script)
            help_run=subprocess.run([shell,'-NoProfile','-File',str(script),'-Help'],capture_output=True,text=True,timeout=20)
            self.assertEqual(help_run.returncode,0);self.assertIn('TechOpsagent setup',help_run.stdout)
            self.assertFalse((Path(d)/'.venv').exists());self.assertFalse((Path(d)/'.env').exists())
            missing=subprocess.run([shell,'-NoProfile','-File',str(script),'-Check'],capture_output=True,text=True,timeout=20)
            self.assertEqual(missing.returncode,1);self.assertIn('No project .venv',missing.stdout)
