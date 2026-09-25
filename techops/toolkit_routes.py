"""Explicit diagnostic routes; collector results are never persisted."""
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator
from threading import Lock
from techops.toolkit import collect
from techops.dns import collect_dns, normalize_hostname
from techops.tool_catalog import CATALOG

router = APIRouter()
_collection_lock = Lock()

class ToolRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    tool: Literal['network', 'connections', 'health', 'services', 'dns']
    hostname: str | None = Field(default=None, max_length=255)

    @model_validator(mode='after')
    def validate_target(self):
        if self.tool == 'dns':
            self.hostname = normalize_hostname(self.hostname)
        elif 'hostname' in self.model_fields_set:
            raise ValueError('Only DNS accepts a hostname')
        return self

@router.get('/api/tools/catalog')
def catalog():
    return CATALOG

@router.post('/api/tools/run')
def run(body: ToolRequest):
    if not _collection_lock.acquire(blocking=False):
        raise HTTPException(409, 'A diagnostic is already running. Try again shortly.')
    try:
        if body.tool == 'dns':
            return collect_dns(body.hostname)
        return collect(body.tool)
    finally:
        _collection_lock.release()
