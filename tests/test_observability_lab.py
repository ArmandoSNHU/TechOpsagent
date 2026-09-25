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

    def test_start_missing_binaries_does_not_change_env(self):
        import tempfile
        from pathlib import Path
        from tools.local_lab import start
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with patch('tools.local_lab.WINDOWS',True):
                with self.assertRaisesRegex(RuntimeError,'binaries missing'):start(root,wait_seconds=0)
            self.assertFalse((root/'.env').exists())
    def test_readiness_wait_has_bounded_timeout(self):
        from tools.local_lab import wait_ready
        with patch('tools.local_lab.probe_service',return_value={'status':'starting'}),patch('tools.local_lab.time.monotonic',side_effect=[0,1,2]):
            self.assertFalse(wait_ready('grafana',3000,1))
    def test_readiness_wait_succeeds_on_correct_service(self):
        from tools.local_lab import wait_ready
        with patch('tools.local_lab.probe_service',return_value={'status':'healthy'}):
            self.assertTrue(wait_ready('loki',3100,1))

    def test_occupied_wrong_service_leaves_configuration_untouched(self):
        import tempfile
        from pathlib import Path
        from tools.local_lab import start,GRAFANA_VERSION
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for relative in ['data/observability/loki/loki-windows-amd64.exe','data/observability/grafana/grafana-'+GRAFANA_VERSION+'/bin/grafana.exe']:
                p=root/relative;p.parent.mkdir(parents=True,exist_ok=True);p.touch()
            with patch('tools.local_lab.WINDOWS',True),patch('tools.local_lab.socket.socket') as sock,patch('tools.local_lab.probe_service',return_value={'status':'unexpected_response'}):
                sock.return_value.__enter__.return_value.connect_ex.return_value=0
                with self.assertRaisesRegex(RuntimeError,'does not identify'):start(root,wait_seconds=0)
            self.assertFalse((root/'.env').exists())
    def test_readiness_detects_process_exit(self):
        from tools.local_lab import wait_ready
        from unittest.mock import Mock
        process=Mock();process.poll.return_value=1
        with patch('tools.local_lab.probe_service') as probe:
            self.assertFalse(wait_ready('grafana',3000,300,process=process))
            probe.assert_not_called()
