import unittest
from unittest.mock import Mock,patch
from urllib.parse import parse_qs,urlsplit
from techops.connectors.servicenow import ServiceNow,incident_preview
from techops.connectors.http import ConnectorError,JsonReader
from techops.engine import investigate

class ServiceNowTests(unittest.TestCase):
    def test_preview_has_no_network_or_person_fields(self):
        result=incident_preview(investigate('api_error','password=secretvalue'))
        self.assertTrue(result['dry_run']);self.assertFalse(result['remote_write'])
        self.assertNotIn('secretvalue',str(result))
        self.assertEqual(set(result['payload']),{'short_description','description'})
    def test_read_is_bounded_and_redacted(self):
        reader=Mock();reader.get.return_value={'result':[{'sys_id':'a'*32,'number':'INC000001','short_description':'Synthetic','description':'password=secretvalue','state':'1'}]}
        result=ServiceNow('https://example.service-now.com',reader=reader).list_incidents()
        self.assertNotIn('secretvalue',str(result));self.assertEqual(len(result['incidents']),1)
        query=parse_qs(urlsplit(reader.get.call_args.args[0]).query)
        self.assertEqual(query['sysparm_limit'],['20']);self.assertNotIn('caller_id',query['sysparm_fields'][0])
    def test_bad_instance_and_auth_rejected(self):
        for url in ['http://example.com','https://user:pass@example.com','https://example.com/path','https://example.com?x=1']:
            with self.assertRaises(ValueError):ServiceNow(url)
        with self.assertRaises(ValueError):ServiceNow('https://example.com',token='fixture',username='demo',password='fixture')
    def test_no_auth_read_fails_before_network(self):
        with patch('http.client.HTTPSConnection') as conn:
            with self.assertRaises(ValueError):ServiceNow('https://example.com').list_incidents()
            conn.assert_not_called()
    def test_malformed_and_unbounded_responses_rejected(self):
        reader=Mock();adapter=ServiceNow('https://example.com',reader=reader)
        for result in [{'result':{}},{'result':[{'sys_id':'bad'}]}]:
            reader.get.return_value=result
            with self.assertRaises(ConnectorError):adapter.list_incidents()
        with self.assertRaises(ValueError):adapter.list_incidents(page=0)
    def test_basic_auth_is_https_only_and_never_in_preview(self):
        with self.assertRaises(ValueError):JsonReader('http://127.0.0.1',basic_auth=('demo','fixture'))
        result=ServiceNow('https://example.com',username='demo',password='fixture').preview()
        self.assertNotIn('fixture',str(result));self.assertNotIn('Authorization',str(result))
