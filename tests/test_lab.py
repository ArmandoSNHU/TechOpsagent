import unittest
from unittest.mock import patch
from techops.lab import fault_lab, probe, collect

class LabTests(unittest.TestCase):
    def test_observed_failure_statuses(self):
        with fault_lab() as port:
            for path,code in [('/checkout',500),('/inventory',504),('/partner',401),('/healthy',200)]:
                with self.subTest(path=path):
                    r=probe(port,path)
                    self.assertEqual(r['status'],code)
                    self.assertEqual(r['kind'],'http')
    def test_timeout_is_reported(self):
        with fault_lab() as port:
            self.assertEqual(probe(port,'/slow',timeout=.02)['kind'],'timeout')
    def test_redirect_is_not_followed(self):
        with fault_lab() as port:
            r=probe(port,'/redirect')
            self.assertEqual(r['status'],302)
            self.assertEqual(r['kind'],'redirect_rejected')
    def test_unknown_path_is_rejected_before_connection(self):
        with patch('techops.lab.http.client.HTTPConnection') as connection:
            with self.assertRaises(ValueError): probe(8765,'https://example.com')
            connection.assert_not_called()
    def test_collect_is_local_and_has_observed_evidence(self):
        r=collect('api_error')
        self.assertTrue(any(x.get('status')==500 for x in r))
        self.assertTrue(any(x['kind']=='dns' for x in r))
    def test_unknown_scenario_rejected(self):
        with self.assertRaises(ValueError): collect('unknown')
