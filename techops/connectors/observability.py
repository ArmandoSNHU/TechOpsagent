"""Read-only Grafana health and bounded Loki log queries."""
from datetime import datetime,timezone
import json
import re
from urllib.parse import urlencode
from techops.engine import redact
from techops.connectors.http import JsonReader, ConnectorError

class Grafana:
    def __init__(self, base_url, reader=None, token=None):
        self.reader=reader or JsonReader(base_url,token=token)
        self.base_url=JsonReader(base_url).base_url
    def preview(self):
        return {'method':'GET','url':self.base_url+'/api/health','dry_run':True,'remote_write':False}
    def health(self):
        value=self.reader.get('/api/health')
        if not isinstance(value,dict) or value.get('database') not in {'ok','failing'}:
            raise ConnectorError('invalid_response','Invalid Grafana health response')
        return {'database':value['database'],'version':str(value.get('version','unknown'))[:100],'read_only':True}

class Loki:
    def __init__(self, base_url, reader=None, token=None):
        self.reader=reader or JsonReader(base_url,token=token)
        self.base_url=JsonReader(base_url).base_url
    def _path(self,service,start,end,limit):
        if not isinstance(service,str) or not re.fullmatch(r'[A-Za-z0-9_.:-]{1,100}',service): raise ValueError('Invalid service label')
        if type(start) is not int or type(end) is not int or start<0 or not 0 < end-start <= 3600:
            raise ValueError('Query window must be positive and at most one hour')
        if type(limit) is not int or not 1 <= limit <= 50: raise ValueError('Limit must be 1–50')
        query={'query':'{service_name="'+service+'"}','start':str(start*1000000000),
               'end':str(end*1000000000),'limit':limit,'direction':'forward'}
        return '/loki/api/v1/query_range?'+urlencode(query)
    def preview(self,service,start,end,limit=50):
        return {'method':'GET','url':self.base_url+self._path(service,start,end,limit),'dry_run':True,'remote_write':False}
    def query(self,service,start,end,limit=50):
        payload=self.reader.get(self._path(service,start,end,limit))
        try:
            if payload['status']!='success' or payload['data']['resultType']!='streams': raise ValueError()
            streams=payload['data']['result']
            if not isinstance(streams,list): raise ValueError()
            rows=[]
            for stream in streams:
                for timestamp,line,*rest in stream['values']:
                    if not isinstance(timestamp,str) or not timestamp.isdigit() or not isinstance(line,str): raise ValueError()
                    observed=datetime.fromtimestamp(int(timestamp)/1000000000,tz=timezone.utc).isoformat()
                    detail=line
                    status=None
                    try:
                        structured=json.loads(line)
                        if isinstance(structured,dict):
                            if isinstance(structured.get('message'),str): detail=structured['message']
                            if type(structured.get('status')) is int and 100<=structured['status']<=599: status=structured['status']
                    except ValueError: pass
                    rows.append({'kind':'http' if status is not None else 'log','source':'loki:'+service,
                                 'detail':redact(detail[:2000]),'status':status,'observed_at':observed})
                    if len(rows)>limit: return {'observations':rows[:limit],'truncated':True,'read_only':True}
            return {'observations':rows,'truncated':len(rows)==limit,'read_only':True}
        except (KeyError,TypeError,ValueError,OverflowError,OSError):
            raise ConnectorError('invalid_response','Invalid Loki stream response') from None
