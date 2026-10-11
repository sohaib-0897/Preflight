import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from .auth import current_user, get_db, project_access, audit, Name
from .db import Agent, AgentVersion

router = APIRouter(prefix="/api/v1")
MODES = {"accurate", "regressed", "unsafe", "slow", "false-completion"}


class VersionInput(BaseModel):
    version: str = Field(min_length=1, max_length=60)
    config: dict = Field(default_factory=lambda: {"mode": "accurate"})

    @field_validator("config")
    @classmethod
    def config_valid(cls, v):
        if set(v) - {"mode", "model", "provider", "capabilities", "tool_schemas"}:
            raise ValueError("Unknown configuration keys or credentials; use operator credential references")
        if v.get("mode", "accurate") not in MODES:
            raise ValueError("Unsupported demo agent mode")
        for key in ("model", "provider"):
            if key in v and (not isinstance(v[key], str) or len(v[key]) > 120 or any(term in v[key].lower() for term in ("bearer ", "sk-", "password=", "api_key="))):
                raise ValueError("Model/provider must be plain metadata, never credentials")
        if len(json.dumps(v)) > 16384:
            raise ValueError("Configuration too large")
        return v


class AgentInput(VersionInput, Name):
    description: str = Field(default="", max_length=2000)
    framework: str = "native"


def agent_access(db, user, agent_id, role="viewer"):
    agent = db.get(Agent, agent_id)
    if not agent:
        raise HTTPException(404, "Resource not found")
    _, org_id = project_access(db, user, agent.project_id, role)
    return agent, org_id


def serialize_version(v):
    return {"id": v.id, "agent_id": v.agent_id, "version": v.version, "fingerprint": v.fingerprint, "config": v.config}


def add_version(db, agent, body):
    config = {"mode": "accurate", **body.config}
    fingerprint = hashlib.sha256(json.dumps(config, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    v = AgentVersion(agent_id=agent.id, version=body.version, config=config, fingerprint=fingerprint)
    db.add(v)
    try:
        db.flush()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Version already exists")
    return v


@router.post("/projects/{project_id}/agents", status_code=201)
async def create_agent(project_id: str, body: AgentInput, user=Depends(current_user), db=Depends(get_db)):
    _, org_id = project_access(db, user, project_id, "developer")
    if body.framework != "native":
        raise HTTPException(422, "Web execution currently supports native demos; framework adapters are Python library integrations")
    a = Agent(project_id=project_id, name=body.name, description=body.description, framework=body.framework)
    db.add(a)
    db.flush()
    v = add_version(db, a, body)
    audit(db, user, org_id, "agent.create", a.id)
    db.commit()
    return {"id": a.id, "name": a.name, "framework": a.framework, "versions": [serialize_version(v)]}


@router.get("/projects/{project_id}/agents")
async def agents(project_id: str, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    return [{"id": a.id, "name": a.name, "description": a.description, "framework": a.framework, "versions": [serialize_version(v) for v in db.scalars(select(AgentVersion).where(AgentVersion.agent_id == a.id).order_by(AgentVersion.created_at))]} for a in db.scalars(select(Agent).where(Agent.project_id == project_id).order_by(Agent.name).limit(100))]


@router.post("/agents/{agent_id}/versions", status_code=201)
async def create_version(agent_id: str, body: VersionInput, user=Depends(current_user), db=Depends(get_db)):
    a, org = agent_access(db, user, agent_id, "developer")
    v = add_version(db, a, body)
    audit(db, user, org, "agent.version.create", v.id)
    db.commit()
    return serialize_version(v)
