"""Explicit diagnostic routes; collector results are never persisted."""
from typing import Literal
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict
from threading import Lock
from techops.toolkit import collect
from techops.tool_catalog import CATALOG

router = APIRouter()
_collection_lock = Lock()

class ToolRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    tool: Literal['network', 'connections', 'health', 'services']

@router.get('/api/tools/catalog')
def catalog():
    return CATALOG

@router.post('/api/tools/run')
def run(body: ToolRequest):
    if not _collection_lock.acquire(blocking=False):
        raise HTTPException(409, 'A diagnostic is already running. Try again shortly.')
    try:
        return collect(body.tool)
    finally:
        _collection_lock.release()
