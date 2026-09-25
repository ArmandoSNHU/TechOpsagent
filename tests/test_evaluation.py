import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from techops.evaluation import evaluate_cases

class EvaluationTests(unittest.TestCase):
    def test_live_run_requires_explicit_flag(self):
        with patch('techops.evaluation.LocalModelAdapter') as adapter:
            with self.assertRaises(PermissionError): evaluate_cases('local-test',allow_inference=False)
            adapter.assert_not_called()
    def test_failed_case_is_recorded_and_remaining_cases_run(self):
        with patch('techops.evaluation.LocalModelAdapter') as adapter:
            adapter.return_value.explain.side_effect=ValueError('Invalid output')
            results=evaluate_cases('local-test',allow_inference=True,measure_gpu=False)
            self.assertEqual(len(results['cases']),6)
            self.assertTrue(all(not r['passed_schema'] for r in results['cases']))
