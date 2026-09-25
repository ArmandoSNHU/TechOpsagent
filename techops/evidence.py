"""Small transparent rule engine over structured, untrusted observations."""
from datetime import datetime, timezone
import json
from typing import Literal
from uuid import uuid4
from pydantic import BaseModel, ConfigDict, Field, ValidationError
from techops.engine import SCENARIOS, redact

class Observation(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True, allow_inf_nan=False)
    kind: Literal['http','log','dns','timeout','probe_error','redirect_rejected']
    source: str = Field(min_length=1,max_length=120)
    detail: str = Field(max_length=2000)
    status: int | None = Field(default=None,ge=100,le=599)
    observed_at: str | None = Field(default=None,max_length=80)
    elapsed_ms: float | None = Field(default=None,ge=0)

def parse_jsonl(text):
    if not isinstance(text,str) or not text.strip() or len(text.encode('utf-8'))>12000:
        raise ValueError('Logs must contain 1–12000 UTF-8 bytes')
    lines=[line for line in text.splitlines() if line.strip()]
    if len(lines)>50: raise ValueError('At most 50 observations are allowed')
    try: return [Observation.model_validate(json.loads(line)).model_dump() for line in lines]
    except (ValueError,ValidationError) as exc: raise ValueError('Invalid JSONL observation') from exc

def analyze(observations, ticket='', environment='imported_logs'):
    if not isinstance(ticket,str) or len(ticket)>4000: raise ValueError('Invalid ticket')
    if not 1 <= len(observations) <= 50: raise ValueError('Expected 1–50 observations')
    rows=[Observation.model_validate(row).model_dump() for row in observations]
    evidence=[]
    scores={key:0 for key in SCENARIOS}
    citations={key:[] for key in SCENARIOS}
    for index,row in enumerate(rows,1):
        eid=f'E{index}'
        detail=redact(row['detail'])
        status=row['status']
        ok = row['kind']=='http' and status is not None and 200 <= status < 300
        dns_ok=row['kind']=='dns' and detail=='localhost resolved to loopback'
        evidence.append({'id':eid,'source':redact(row['source']),
                         'signal':f'{eid} · '+(f'HTTP {status}' if status is not None else row['kind']),
                         'detail':detail,'state':'passed' if ok or dns_ok else 'failed',
                         'observed_at':row['observed_at'],'elapsed_ms':row['elapsed_ms']})
        text=detail.lower()
        weights={
            'api_error': (2 if row['kind']=='http' and status==500 else 0) + (2 if any(x in text for x in ['keyerror','unhandled exception','traceback']) else 0),
            'dependency_timeout': (2 if row['kind']=='timeout' or (row['kind']=='http' and status==504) else 0) + (2 if any(x in text for x in ['read timeout','upstream timeout','deadline exceeded']) else 0),
            'invalid_credential': (2 if row['kind']=='http' and status in (401,403) else 0) + (2 if any(x in text for x in ['invalid_token','token expired','credential rejected']) else 0),
        }
        for key,weight in weights.items():
            if weight:
                scores[key]+=weight
                citations[key].append(eid)
    ranked=sorted(({'scenario':k,'cause':SCENARIOS[k]['cause'],'score':v,'evidence_ids':citations[k]} for k,v in scores.items() if v),key=lambda h:h['score'],reverse=True)
    healthy=all(e['state']=='passed' for e in evidence)
    selected=ranked[0]['scenario'] if ranked else None
    competing=len(ranked)>1
    cause='Multiple plausible causes' if competing else ranked[0]['cause'] if ranked else 'No failure observed' if healthy else 'Insufficient evidence'
    certainty='competing' if competing else 'supported' if ranked and ranked[0]['score']>=4 else 'limited' if ranked else 'insufficient'
    steps=SCENARIOS[selected]['next_steps'] if selected and not competing else [
        'Correlate observations by service and timestamp; separate unrelated failures.',
        'Collect missing error logs and repeat bounded health checks.',
        'Verify a hypothesis with an independent check before requesting remediation.']
    return {'id':uuid4().hex,'created_at':datetime.now(timezone.utc).isoformat(),
            'title':'Observed evidence investigation','service':'local-lab' if environment=='local_fault_lab' else 'imported-logs',
            'severity':'P3','description':'Rule-based triage from structured observations.',
            'cause':cause,'certainty':certainty,'impact':'Observed technical signals only; customer impact and severity require operator assessment.',
            'evidence':evidence,'hypotheses':ranked,'next_steps':list(steps),
            'prevention':SCENARIOS[selected]['prevention'] if selected and not competing else 'Improve correlated logging and document verified recovery checks.',
            'ticket':redact(ticket),'status':'suspected','analysis_mode':'rule_based','environment':environment,
            'author':'Armando Gomez','scenario':selected or 'unknown',
            'limitations':'Rule-based triage is not a confirmed root cause. Imported logs are unverified user data; local fault-lab observations come from intentionally failing loopback endpoints. No model inference, remediation, or remote writes occurred.'}
