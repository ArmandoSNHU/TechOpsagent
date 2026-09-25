"""Configured read-only integrations. Request bodies cannot choose remote hosts."""
from techops.settings import load_settings
import time
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel,ConfigDict,Field
from techops.connectors.github import GitHubIssues
from techops.connectors.observability import Grafana,Loki
from techops.connectors.http import ConnectorError
from techops.evidence import analyze

class GitHubRead(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    page:int=Field(default=1,ge=1,le=1000)

class LokiRead(BaseModel):
    model_config=ConfigDict(extra='forbid',strict=True)
    service:str=Field(min_length=1,max_length=100,pattern=r'^[A-Za-z0-9_.:-]+$')
    minutes:int=Field(default=15,ge=1,le=60)

def integration_router(store, settings=None):
    router=APIRouter()
    settings=load_settings() if settings is None else settings
    config={name:settings.get(key, '') for name,key in [('github_repository','GITHUB_REPOSITORY'),('grafana_url','GRAFANA_URL'),('loki_url','LOKI_URL')]}
    def required(name):
        value=config.get(name)
        if not value: raise HTTPException(409,name+' is not configured')
        return value
    def upstream(call):
        try: return call()
        except ConnectorError as exc: raise HTTPException(502,exc.code+': '+str(exc)) from None
        except ValueError: raise HTTPException(400,'Invalid integration configuration or query') from None

    @router.get('/api/integrations')
    def status():
        return {'github':{'configured':bool(config.get('github_repository')),'repository':config.get('github_repository')},
                'grafana':{'configured':bool(config.get('grafana_url'))},
                'loki':{'configured':bool(config.get('loki_url'))},'remote_writes':False}

    @router.post('/api/integrations/github/read')
    def github_read(body:GitHubRead):
        repository=required('github_repository')
        return upstream(lambda:GitHubIssues(repository,token=settings.get('GITHUB_TOKEN')).list_issues(page=body.page,per_page=20))

    @router.get('/api/integrations/github/preview')
    def github_preview():
        return upstream(lambda:GitHubIssues(required('github_repository')).preview())

    @router.get('/api/integrations/grafana/health')
    def grafana_health():
        url=required('grafana_url')
        return upstream(lambda:Grafana(url,token=settings.get('GRAFANA_TOKEN')).health())

    @router.post('/api/integrations/loki/analyze',status_code=201)
    def loki_analyze(body:LokiRead):
        url=required('loki_url')
        end=int(time.time())
        logs=upstream(lambda:Loki(url,token=settings.get('LOKI_TOKEN')).query(body.service,end-body.minutes*60,end))
        if not logs['observations']: raise HTTPException(404,'No logs in the selected window')
        result=analyze(logs['observations'],environment='imported_logs')
        result.update(title='Loki evidence: '+body.service,service=body.service,source='loki',source_truncated=logs['truncated'])
        store.save(result)
        return result
    return router
