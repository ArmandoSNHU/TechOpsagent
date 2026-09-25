import json
import subprocess
import unittest
from unittest.mock import Mock
from techops.dns import collect_dns, normalize_hostname


class DnsTests(unittest.TestCase):
    def run_fixture(self, data, host='example.com'):
        runner = Mock(return_value=subprocess.CompletedProcess([], 0, json.dumps(data), ''))
        return collect_dns(host, runner=runner, platform='win32'), runner

    def test_normalize_hostname(self):
        for raw, expected in [(' Example.COM. ', 'example.com'), ('intranet', 'intranet'), ('xn--bcher-kva.example', 'xn--bcher-kva.example')]:
            self.assertEqual(normalize_hostname(raw), expected)

    def test_rejects_non_hostnames_without_executing(self):
        runner=Mock()
        for value in ['', 'https://example.com', 'example.com/path', 'example.com:443', 'user@example.com', '-server', 'example.com;whoami', '$(whoami)', 'a..b', 'x'*64+'.com', '127.0.0.1', '::1', '*.example.com', 'a\nb', 'example.com..', 'bücher.example', 'a.'*127+'com']:
            with self.subTest(value=value), self.assertRaises(ValueError):
                collect_dns(value, runner=runner, platform='win32')
        runner.assert_not_called()

    def test_success_has_safe_command_and_query_metadata(self):
        row={'name':'example.com','type':'A','answer':'192.0.2.10','ttl_seconds':60}
        result, runner=self.run_fixture({'outcome':'ok','elapsed_ms':12,'readings':[row]})
        self.assertEqual(result['status'], 'observed')
        self.assertEqual(result['hostname'], 'example.com')
        self.assertEqual(result['elapsed_ms'],12)
        self.assertEqual(result['readings'],[row])
        args, kwargs=runner.call_args
        self.assertNotIn('example.com', ' '.join(args[0]))
        self.assertEqual(json.loads(kwargs['input']), {'hostname':'example.com'})
        self.assertEqual(kwargs['timeout'],12)
        self.assertFalse(kwargs['shell'])
        self.assertIn('-DnsOnly',args[0][-1])
        self.assertIn('-NoHostsFile',args[0][-1])

    def test_query_failure_and_empty_answers_are_not_success(self):
        for payload,outcome in [({'outcome':'failed','elapsed_ms':3,'readings':[]},'issue'), ({'outcome':'ok','elapsed_ms':3,'readings':[]},'not_checked')]:
            result,_=self.run_fixture(payload)
            self.assertEqual(result['status'],outcome)
        result,_=self.run_fixture({'outcome':'ok','elapsed_ms':3,'readings':[{'name':'example.com','type':'CNAME','answer':'alias.example.com','ttl_seconds':1}]})
        self.assertEqual(result['status'],'not_checked')

    def test_untrusted_or_malformed_output_is_unavailable(self):
        for payload in [None,[],{'outcome':'other'}, {'outcome':'ok','elapsed_ms':float('nan'),'readings':[]}, {'outcome':'ok','elapsed_ms':-1,'readings':[]}, {'outcome':'ok','elapsed_ms':1,'readings':[{'name':'example.com','type':'A','answer':'not-an-ip','ttl_seconds':60}]}]:
            result,_=self.run_fixture(payload)
            self.assertEqual(result['status'],'unavailable')
            self.assertEqual(result['readings'],[])

    def test_numeric_answers_are_not_treated_as_ip_addresses(self):
        result,_=self.run_fixture({'outcome':'ok','elapsed_ms':1,'readings':[{'name':'example.com','type':'A','answer':1,'ttl_seconds':60}]})
        self.assertEqual(result['status'],'unavailable')

    def test_non_json_and_oversized_output_are_unavailable(self):
        for output in ['not json', 'x'*262145]:
            runner=Mock(return_value=subprocess.CompletedProcess([],0,output,''))
            result=collect_dns('example.com',runner=runner,platform='win32')
            self.assertEqual(result['status'],'unavailable')
            self.assertEqual(result['readings'],[])

    def test_limits_rows_and_discards_extra_fields(self):
        row={'name':'example.com','type':'AAAA','answer':'2001:db8::1','ttl_seconds':60,'private':'synthetic'}
        result,_=self.run_fixture({'outcome':'ok','elapsed_ms':1,'readings':[row]*65,'stderr':'synthetic'})
        self.assertEqual(len(result['readings']),64)
        self.assertTrue(result['truncated'])
        self.assertNotIn('private',json.dumps(result))

    def test_timeout_and_process_error_do_not_leak_details(self):
        for runner in [Mock(side_effect=subprocess.TimeoutExpired('synthetic detail',12)),Mock(return_value=subprocess.CompletedProcess([],1,'','private detail'))]:
            result=collect_dns('example.com',runner=runner,platform='win32')
            self.assertEqual(result['status'],'unavailable')
            self.assertNotIn('private detail',json.dumps(result))

    def test_unsupported_platform_does_not_run(self):
        runner=Mock()
        self.assertEqual(collect_dns('example.com',runner=runner,platform='linux')['status'],'unavailable')
        runner.assert_not_called()
