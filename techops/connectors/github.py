"""Read-only, bounded GitHub issue intake. Ticket text is never executed."""
import re
from urllib.parse import urlencode
from techops.engine import redact
from techops.connectors.http import JsonReader, ConnectorError

class GitHubIssues:
    def __init__(self, repository, reader=None, token=None):
        parts=repository.split('/')
        if len(parts)!=2 or any(not re.fullmatch(r'[A-Za-z0-9_.-]+',p) or p in {'.','..'} for p in parts):
            raise ValueError('Repository must be owner/name')
        self.repository=repository
        self.reader=reader or JsonReader('https://api.github.com',token=token)

    def _path(self,page,per_page):
        if type(page) is not int or type(per_page) is not int or not 1 <= page <= 1000 or not 1 <= per_page <= 100:
            raise ValueError('Page or per_page outside supported bounds')
        return '/repos/'+self.repository+'/issues?'+urlencode({'state':'open','per_page':per_page,'page':page,'sort':'updated','direction':'desc'})

    def preview(self,page=1,per_page=20):
        return {'method':'GET','url':'https://api.github.com'+self._path(page,per_page),'remote_write':False,'dry_run':True}

    def list_issues(self,page=1,per_page=20):
        payload=self.reader.get(self._path(page,per_page))
        if not isinstance(payload,list) or len(payload)>per_page: raise ConnectorError('invalid_response','Invalid issue list')
        tickets=[]
        for issue in payload:
            if not isinstance(issue,dict): raise ConnectorError('invalid_response','Invalid issue record')
            if 'pull_request' in issue: continue
            number=issue.get('number');title=issue.get('title');body=issue.get('body') or ''
            if type(number) is not int or number<1 or not isinstance(title,str) or not isinstance(body,str):
                raise ConnectorError('invalid_response','Invalid issue fields')
            labels=issue.get('labels') or []
            if not isinstance(labels,list): raise ConnectorError('invalid_response','Invalid issue labels')
            tickets.append({'number':number,'title':redact(title[:300]),'body':redact(body[:4000]),
                            'body_truncated':len(body)>4000,'state':'open',
                            'labels':[redact(label['name'][:100]) for label in labels if isinstance(label,dict) and isinstance(label.get('name'),str)],
                            'url':f'https://github.com/{self.repository}/issues/{number}','source':'github'})
        return {'repository':self.repository,'page':page,'tickets':tickets,
                'next_page':page+1 if len(payload)==per_page and page<1000 else None,
                'read_only':True,'untrusted_content':True}
