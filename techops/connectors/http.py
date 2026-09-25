"""Bounded JSON GET transport; no redirects, writes, or credential logging."""
import http.client
import json
import base64
from urllib.parse import urlsplit

class ConnectorError(RuntimeError):
    def __init__(self, code, message):
        super().__init__(message)
        self.code=code

class JsonReader:
    def __init__(self, base_url, token=None, timeout=10, basic_auth=None):
        parts=urlsplit(base_url)
        if parts.scheme not in {'https','http'} or not parts.hostname or parts.username or parts.password or parts.query or parts.fragment:
            raise ValueError('Expected an origin URL without embedded credentials or query')
        if parts.scheme=='http' and parts.hostname not in {'127.0.0.1','localhost','::1'}:
            raise ValueError('Cleartext HTTP is permitted only for loopback services')
        if '..' in parts.path or any(c in base_url for c in '\r\n'): raise ValueError('Invalid base path')
        if token and any(c in token for c in '\r\n'): raise ValueError('Invalid token')
        if basic_auth is not None:
            if token or parts.scheme != 'https' or len(basic_auth) != 2 or not all(isinstance(v,str) and v and not any(c in v for c in '\r\n') for v in basic_auth) or ':' in basic_auth[0]:
                raise ValueError('Basic authentication requires HTTPS and one valid credential pair')
        if not 0 < timeout <= 30: raise ValueError('Invalid timeout')
        self.base_url=base_url.rstrip('/')
        self.parts=parts
        self.token=token
        self.basic_auth=basic_auth
        self.timeout=timeout

    def get(self, path):
        if not path.startswith('/') or path.startswith('//') or any(c in path for c in '\r\n'):
            raise ValueError('Expected a relative API path')
        constructor=http.client.HTTPSConnection if self.parts.scheme=='https' else http.client.HTTPConnection
        connection=constructor(self.parts.hostname,self.parts.port,timeout=self.timeout)
        headers={'Accept':'application/json','User-Agent':'TechOpsagent/0.3'}
        if self.token: headers['Authorization']='Bearer '+self.token
        elif self.basic_auth: headers['Authorization']='Basic '+base64.b64encode(':'.join(self.basic_auth).encode()).decode('ascii')
        try:
            connection.request('GET',self.parts.path.rstrip('/')+path,headers=headers)
            response=connection.getresponse()
            if response.status in (403,429): raise ConnectorError('rate_limited_or_forbidden' if response.status==403 else 'rate_limited','Service denied the request or rate limit was reached')
            if response.status==401: raise ConnectorError('unauthorized','Service rejected authentication')
            if 300 <= response.status < 400: raise ConnectorError('redirect_rejected','Redirects are not followed')
            if response.status!=200: raise ConnectorError('upstream_error','Service returned HTTP '+str(response.status))
            raw=response.read(1048577)
            if len(raw)>1048576: raise ConnectorError('response_too_large','Response exceeds 1 MiB')
            result=json.loads(raw)
            if not isinstance(result,(dict,list)): raise ValueError('Unexpected JSON type')
            return result
        except ConnectorError: raise
        except (OSError,http.client.HTTPException): raise ConnectorError('unavailable','Service is unavailable or timed out') from None
        except (ValueError,UnicodeError): raise ConnectorError('invalid_response','Service returned invalid JSON') from None
        finally: connection.close()
