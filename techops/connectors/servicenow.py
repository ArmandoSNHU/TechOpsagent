"""Bounded ServiceNow incident reads and offline draft payloads. No remote writes."""
import re
from urllib.parse import urlsplit,urlencode
from techops.connectors.http import JsonReader,ConnectorError
from techops.engine import redact,render_report

def incident_preview(incident):
    return {'method':'POST','path':'/api/now/table/incident','dry_run':True,'remote_write':False,
            'requires_review':True,'payload':{
                'short_description':redact('Draft: '+incident['title'])[:160],
                'description':redact(render_report(incident))[:12000]},
            'review_note':'Review evidence and remove private data before any manual submission. Impact, urgency, caller and assignment are intentionally unset.'}

class ServiceNow:
    def __init__(self,base_url,reader=None,token=None,username=None,password=None):
        parts=urlsplit(base_url)
        if parts.scheme != 'https' or parts.path not in {'','/'}:
            raise ValueError('ServiceNow requires an HTTPS instance origin')
        if token and (username or password): raise ValueError('Choose OAuth token or username/password')
        if bool(username) != bool(password): raise ValueError('Both username and password are required')
        self.base_url=JsonReader(base_url).base_url
        self.authenticated=bool(token or (username and password) or reader is not None)
        self.reader=reader or JsonReader(base_url,token=token,basic_auth=(username,password) if username else None)
    def _path(self,page):
        if type(page) is not int or not 1<=page<=100: raise ValueError('Page must be 1-100')
        return '/api/now/table/incident?'+urlencode({'sysparm_query':'active=true^ORDERBYDESCsys_updated_on',
            'sysparm_fields':'sys_id,number,short_description,description,state',
            'sysparm_limit':20,'sysparm_offset':(page-1)*20,'sysparm_exclude_reference_link':'true',
            'sysparm_display_value':'false'})
    def preview(self,page=1):
        return {'method':'GET','url':self.base_url+self._path(page),'dry_run':True,'remote_write':False}
    def list_incidents(self,page=1):
        path=self._path(page)
        if not self.authenticated: raise ValueError('ServiceNow authentication is not configured')
        value=self.reader.get(path)
        try:
            rows=value['result']
            if not isinstance(rows,list) or len(rows)>20: raise ValueError()
            result=[]
            for row in rows:
                if not isinstance(row,dict) or not re.fullmatch('[a-fA-F0-9]{32}',row.get('sys_id','')): raise ValueError()
                if not all(isinstance(row.get(k,''),str) for k in ['number','short_description','description','state']): raise ValueError()
                result.append({'id':row['sys_id'],'number':redact(row.get('number',''))[:40],
                    'title':redact(row.get('short_description',''))[:300],
                    'body':redact(row.get('description',''))[:4000],'state':row.get('state','')[:40]})
            return {'incidents':result,'page':page,'next_page':page+1 if len(rows)==20 and page<100 else None,
                    'read_only':True,'untrusted_content':True}
        except (KeyError,TypeError,ValueError):
            raise ConnectorError('invalid_response','Invalid ServiceNow incident response') from None
