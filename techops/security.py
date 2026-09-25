"""Local-only ASGI request boundaries, independent of route implementation."""
import asyncio
from starlette.responses import JSONResponse

MAX_BODY = 16384
HEADERS = {
    'x-content-type-options': 'nosniff',
    'cache-control': 'no-store',
    'content-security-policy': "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'",
}

class LocalOnlyMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        headers = dict(scope.get('headers', []))
        host = headers.get(b'host', b'').decode('latin-1')
        port = scope['server'][1]
        allowed = {f'127.0.0.1:{port}', f'localhost:{port}'}
        async def secured_send(message):
            if message['type'] == 'http.response.start':
                message = dict(message)
                message['headers'] = list(message.get('headers', [])) + [(k.encode(),v.encode()) for k,v in HEADERS.items()]
            await send(message)
        async def reject(code, reason):
            await JSONResponse({'error':reason}, status_code=code)(scope, receive, secured_send)
        if host not in allowed:
            return await reject(403, 'Invalid host')
        if scope['method'] in {'POST','PUT','PATCH','DELETE'}:
            origin = headers.get(b'origin', b'').decode('latin-1')
            if origin and origin != 'http://' + host:
                return await reject(403, 'Cross-origin request rejected')
        if scope['method'] == 'POST':
            if headers.get(b'content-type', b'').split(b';')[0].strip().lower() != b'application/json':
                return await reject(415, 'Expected application/json')
            try:
                size = int(headers.get(b'content-length', b'0'))
            except ValueError:
                return await reject(400, 'Invalid Content-Length')
            if size < 0 or size > MAX_BODY:
                return await reject(413, 'Body must be at most 16384 bytes')
            body = bytearray()
            async def read_body():
                while True:
                    message = await receive()
                    if message['type'] == 'http.disconnect':
                        return False
                    body.extend(message.get('body', b''))
                    if len(body) > MAX_BODY:
                        return False
                    if not message.get('more_body', False):
                        return True
            try:
                complete = await asyncio.wait_for(read_body(), timeout=5)
            except TimeoutError:
                return await reject(408, 'Request body timed out')
            if not complete or not body:
                return await reject(413, 'Body must be 1–16384 bytes')
            delivered = False
            async def buffered_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {'type':'http.request','body':bytes(body),'more_body':False}
                return await receive()
            return await self.app(scope, buffered_receive, secured_send)
        await self.app(scope, receive, secured_send)
