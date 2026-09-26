"""FastAPI application and loopback-only Uvicorn launcher."""
import argparse
from pathlib import Path
from typing import Literal
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
from techops.engine import SCENARIOS, investigate, render_report
from techops.security import LocalOnlyMiddleware
from techops.store import Store
from techops.evidence import analyze, parse_jsonl
from techops.lab import collect
from techops.ai import LocalModelAdapter
from techops.integration_routes import integration_router
from techops.runtime import build_id
from techops.toolkit_routes import router as toolkit_router

ROOT = Path(__file__).resolve().parent
ROUTES = ('GET /api/health', 'GET /api/scenarios', 'GET /api/incidents', 'GET /api/incidents/{id}', 'GET /api/incidents/{id}/report', 'POST /api/investigate', 'GET /openapi.json', 'POST /api/lab/investigate', 'POST /api/analyze', 'GET /api/incidents/{id}/ai-preview', 'GET /api/integrations', 'POST /api/integrations/github/read', 'GET /api/integrations/github/preview', 'GET /api/integrations/grafana/health', 'POST /api/integrations/loki/analyze', 'POST /api/integrations/servicenow/read', 'GET /api/incidents/{incident_id}/servicenow-preview')

ROUTES += ('GET /api/tools/catalog', 'POST /api/tools/run')

class InvestigationRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    scenario: Literal['api_error','dependency_timeout','invalid_credential']
    ticket: str = Field(default='', max_length=4000)

class LogRequest(BaseModel):
    model_config = ConfigDict(extra='forbid',strict=True)
    log_text: str = Field(min_length=1,max_length=12000)
    ticket: str = Field(default='',max_length=4000)

def create_app(database=None, settings=None):
    started_build=build_id()
    store = Store(database or ROOT.parent/'data'/'incidents.sqlite3')
    app = FastAPI(title='TechOpsagent', version='0.3.0',
                  description='Local support operations lab by Armando Gomez. Synthetic evidence; suspected causes.',
                  docs_url=None, redoc_url=None)
    app.add_middleware(LocalOnlyMiddleware)
    app.include_router(integration_router(store, settings))
    app.include_router(toolkit_router)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({'error':'Invalid JSON, scenario, or ticket (maximum 4000 characters)'},status_code=400)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse({'error':str(exc.detail)},status_code=exc.status_code)

    @app.exception_handler(sqlite3.Error)
    async def storage_error(request, exc):
        return JSONResponse({'error':'Local storage unavailable'},status_code=503)

    @app.get('/api/health')
    def health():
        return {'status':'ok','mode':'simulated','version':'0.3.0','framework':'fastapi','build_id':started_build}

    @app.get('/api/scenarios')
    def scenarios():
        return [dict(id=k, **{f:v[f] for f in ('title','service','severity','description')}) for k,v in SCENARIOS.items()]

    @app.get('/api/incidents')
    def incidents():
        return store.list()

    def get_incident(incident_id):
        record = store.get(incident_id)
        if record is None: raise HTTPException(404, 'Incident not found')
        return record

    @app.get('/api/incidents/{id}')
    def incident(id: str):
        return get_incident(id)

    @app.get('/api/incidents/{id}/ai-preview')
    def ai_preview(id: str):
        return LocalModelAdapter().dry_run(get_incident(id))

    @app.get('/api/incidents/{id}/report')
    def report(id: str):
        return Response(render_report(get_incident(id)), media_type='text/markdown',
                        headers={'Content-Disposition':'attachment; filename="incident-report.md"'})

    @app.post('/api/investigate',status_code=201)
    def run_investigation(body: InvestigationRequest):
        result = investigate(body.scenario,body.ticket)
        store.save(result)
        return result

    @app.post('/api/lab/investigate',status_code=201)
    def investigate_lab(body: InvestigationRequest):
        result=analyze(collect(body.scenario),body.ticket,environment='local_fault_lab')
        result['title']=SCENARIOS[body.scenario]['title']
        store.save(result)
        return result

    @app.post('/api/analyze',status_code=201)
    def analyze_logs(body: LogRequest):
        try: result=analyze(parse_jsonl(body.log_text),body.ticket)
        except ValueError: raise HTTPException(400,'Invalid JSONL observations; see docs/LOGS.md')
        store.save(result)
        return result

    @app.get('/',include_in_schema=False)
    def index():
        html = (ROOT/'static'/'toolkit'/'index.html').read_text(encoding='utf-8')
        return Response(html.replace('data-mode="demo"', 'data-mode="local"'), media_type='text/html')

    @app.get('/incidents', include_in_schema=False)
    def incident_workspace(): return FileResponse(ROOT/'static'/'index.html', media_type='text/html')

    @app.get('/toolkit.js', include_in_schema=False)
    def toolkit_js(): return FileResponse(ROOT/'static'/'toolkit'/'toolkit.js', media_type='text/javascript')

    @app.get('/investigation.js', include_in_schema=False)
    def investigation_js(): return FileResponse(ROOT/'static'/'toolkit'/'investigation.js', media_type='text/javascript')

    @app.get('/toolkit.css', include_in_schema=False)
    def toolkit_css(): return FileResponse(ROOT/'static'/'toolkit'/'toolkit.css', media_type='text/css')

    @app.get('/app.js',include_in_schema=False)
    def javascript(): return FileResponse(ROOT/'static'/'app.js',media_type='text/javascript')

    @app.get('/style.css',include_in_schema=False)
    def stylesheet(): return FileResponse(ROOT/'static'/'style.css',media_type='text/css')

    return app

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port',type=int,default=8765)
    args=parser.parse_args()
    uvicorn.run(create_app(),host='127.0.0.1',port=args.port,proxy_headers=False,access_log=False)

if __name__=='__main__': main()
