import unittest
from unittest.mock import patch
from tools.seed_loki import build_payload,send_local

class LabTests(unittest.TestCase):
    def test_synthetic_payload_has_expected_label_and_signals(self):
        payload=build_payload(100000000000)
        self.assertEqual(payload['streams'][0]['stream']['service_name'],'checkout')
        self.assertEqual(len(payload['streams'][0]['values']),3)
        self.assertIn('synthetic',str(payload).lower())
    def test_send_is_fixed_loopback_and_no_redirects(self):
        with patch('tools.seed_loki.http.client.HTTPConnection') as conn:
            conn.return_value.getresponse.return_value.status=204
            send_local(build_payload(100000000000))
            conn.assert_called_once_with('127.0.0.1',3100,timeout=5)
            self.assertEqual(conn.return_value.request.call_args.args[:2],('POST','/loki/api/v1/push'))

    def test_prepare_preserves_credentials_and_keeps_them_out_of_configs(self):
        import tempfile
        from pathlib import Path
        from tools.local_lab import prepare
        from techops.settings import write_settings,load_settings
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_settings(root/'.env',{'GITHUB_TOKEN':'fixture'})
            values=prepare(root)
            self.assertEqual(load_settings(root/'.env',{})['GITHUB_TOKEN'],'fixture')
            self.assertTrue(values['GRAFANA_ADMIN_PASSWORD'])
            self.assertTrue((root/'data/observability/grafana-data').is_dir())
            self.assertTrue((root/'data/observability/dashboards/techops.json').is_file())
            self.assertNotIn(values['GRAFANA_ADMIN_PASSWORD'],(root/'data/observability/grafana.ini').read_text())
            self.assertIn('127.0.0.1',(root/'data/observability/loki.yaml').read_text())
    def test_prepare_refuses_to_replace_other_services(self):
        import tempfile
        from pathlib import Path
        from tools.local_lab import prepare
        from techops.settings import write_settings,load_settings
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);write_settings(root/'.env',{'GRAFANA_URL':'https://example.com'})
            with self.assertRaises(ValueError):prepare(root)
            self.assertEqual(load_settings(root/'.env',{})['GRAFANA_URL'],'https://example.com')
