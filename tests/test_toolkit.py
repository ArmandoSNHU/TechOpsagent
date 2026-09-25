import json
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock

from techops.toolkit import collect, summarize


class ToolkitTests(unittest.TestCase):
    def run_fixture(self, tool, data):
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(data), ''))
        return collect(tool, runner=runner, platform='win32'), runner

    def test_unknown_tool_never_executes(self):
        runner = Mock()
        with self.assertRaises(ValueError):
            collect('network;whoami', runner=runner, platform='win32')
        runner.assert_not_called()

    def test_unsupported_platform_never_executes(self):
        runner = Mock()
        result = collect('network', runner=runner, platform='linux')
        self.assertEqual(result['status'], 'unavailable')
        runner.assert_not_called()

    def test_fixed_command_and_no_shell(self):
        result, runner = self.run_fixture('network', [{'adapter': 'Example', 'ipv4': ['192.0.2.10'], 'gateway': ['192.0.2.1'], 'dns': ['192.0.2.53']}])
        args, options = runner.call_args
        self.assertIn('-NonInteractive', args[0])
        self.assertFalse(options['shell'])
        self.assertEqual(options['timeout'], 12)
        self.assertEqual(result['mode'], 'local')
        self.assertEqual(result['status'], 'observed')
        self.assertIn('not tested', result['summary'].lower())

    def test_empty_is_not_healthy(self):
        for tool in ('network', 'connections', 'health', 'services'):
            result, _ = self.run_fixture(tool, [])
            self.assertEqual(result['status'], 'not_checked')

    def test_all_null_fields_are_not_usable_readings(self):
        result, _ = self.run_fixture('network', [{'adapter': None, 'ipv4': None, 'gateway': None, 'dns': None}])
        self.assertEqual(result['status'], 'not_checked')
        self.assertEqual(result['readings'], [])

    def test_failure_does_not_leak_stderr(self):
        runner = Mock(return_value=subprocess.CompletedProcess([], 1, '', 'private detail'))
        result = collect('network', runner=runner, platform='win32')
        self.assertEqual(result['status'], 'unavailable')
        self.assertNotIn('private detail', json.dumps(result))

    def test_timeout_is_not_success(self):
        runner = Mock(side_effect=subprocess.TimeoutExpired('powershell', 12))
        self.assertEqual(collect('network', runner=runner, platform='win32')['status'], 'unavailable')

    def test_invalid_or_oversized_output(self):
        for output in ('not json', 'x' * 262145, '{"password":"synthetic"}', 'null', '42'):
            runner = Mock(return_value=subprocess.CompletedProcess([], 0, output, ''))
            result = collect('network', runner=runner, platform='win32')
            self.assertIn(result['status'], ('unavailable', 'not_checked'))
            self.assertEqual(result['readings'], [])

    def test_fields_are_allowlisted_and_rows_bounded(self):
        result, _ = self.run_fixture('connections', [{'process': 'sample', 'local': '192.0.2.10:80', 'remote': '198.51.100.3:443', 'state': 'Established', 'password': 'synthetic'}] * 205)
        self.assertEqual(len(result['readings']), 200)
        self.assertNotIn('password', json.dumps(result))
        self.assertTrue(result['truncated'])

    def test_resource_thresholds(self):
        self.assertEqual(summarize('health', [{'metric': 'Disk free %', 'value': 9}])[0], 'issue')
        self.assertEqual(summarize('health', [{'metric': 'Disk free %', 'value': 10}])[0], 'observed')
        self.assertEqual(summarize('health', [{'metric': 'Memory used %', 'value': 91}])[0], 'issue')

    def test_stopped_service_does_not_claim_broken(self):
        result, _ = self.run_fixture('services', [{'service': 'Spooler', 'state': 'Stopped', 'start': 'Manual'}])
        self.assertEqual(result['status'], 'observed')
        self.assertIn('not necessarily', result['summary'])
