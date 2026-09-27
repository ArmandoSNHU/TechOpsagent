import asyncio
import unittest
from techops.security import LocalOnlyMiddleware
from techops.engine import investigate

class ExportPrivacyTests(unittest.TestCase):
    def test_incident_download_omits_all_freeform_fields(self):
        from techops.engine import render_shared_report
        record = investigate('api_error')
        marker = 'PRIVATE_SENTINEL 10.4.5.6 host.internal C:\\Users\\Person\\notes'
        for key in ('title','id','created_at','severity','environment','analysis_mode','impact','cause','prevention','ticket','limitations'):
            record[key] = marker
        record['evidence'] = [{'source':marker,'signal':marker,'detail':marker}]
        record['next_steps'] = [marker]
        record['hypotheses'] = [{'cause':marker,'score':2,'evidence_ids':[marker]}]
        out = render_shared_report(record)
        self.assertNotIn('PRIVATE_SENTINEL',out)
        self.assertIn('Evidence records: 1',out)
        self.assertIn('omitted',out)

class PeerBoundaryTests(unittest.TestCase):
    def check_scope(self, client, server):
        messages=[]
        async def app(scope,receive,send):
            await send({'type':'http.response.start','status':204,'headers':[]})
        async def receive(): return {'type':'http.request','body':b''}
        async def send(message): messages.append(message)
        scope={'type':'http','method':'GET','headers':[(b'host',b'127.0.0.1:8765')], 'client':client,'server':server}
        asyncio.run(LocalOnlyMiddleware(app)(scope,receive,send))
        return messages[0]['status']
    def test_remote_peer_cannot_spoof_local_host(self):
        for client in [('192.0.2.1',123),None,('invalid',123)]:
            self.assertEqual(self.check_scope(client,('127.0.0.1',8765)),403)
    def test_nonlocal_listener_rejected_even_with_local_peer(self):
        for server in [('0.0.0.0',8765),('192.0.2.2',8765),None]:
            self.assertEqual(self.check_scope(('127.0.0.1',123),server),403)
    def test_loopback_peer_and_endpoint_allowed(self):
        self.assertEqual(self.check_scope(('127.0.0.1',123),('127.0.0.1',8765)),204)
