import hashlib
import json
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field, field_validator
from sqlalchemy import select
from .auth import current_user, get_db, project_access, audit, Name
from .db import Dataset, Scenario, GroundTruthRecord
from preflight_eval import SCENARIOS, SCENARIO_IDS

router = APIRouter(prefix="/api/v1")


class DatasetInput(Name):
    scenario_ids: list[str] = Field(min_length=1, max_length=8)

    @field_validator("scenario_ids")
    @classmethod
    def validate_ids(cls, v):
        if len(set(v)) != len(v) or set(v)-set(SCENARIO_IDS):
            raise ValueError("Choose distinct registered native scenario IDs")
        return sorted(v)


@router.post("/projects/{project_id}/datasets", status_code=201)
def create_dataset(project_id: str, body: DatasetInput, user=Depends(current_user), db=Depends(get_db)):
    _, org = project_access(db, user, project_id, "developer")
    payload = {"name": body.name, "scenario_ids": body.scenario_ids, "benchmark": "native", "benchmark_version": "1.0.0"}
    payload["fingerprint"] = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    dataset = Dataset(project_id=project_id, payload=payload)
    db.add(dataset)
    db.flush()
    for scenario_id in body.scenario_ids:
        source = next(s for s in SCENARIOS if s["id"] == scenario_id)
        scenario = Scenario(dataset_id=dataset.id, payload=source)
        db.add(scenario)
        db.flush()
        db.add(GroundTruthRecord(scenario_id=scenario.id, payload={"method": "native versioned deterministic validators", "benchmark_version": "1.0.0", "scenario_id": scenario_id}))
    audit(db, user, org, "dataset.create", dataset.id)
    db.commit()
    return {"id": dataset.id, **dataset.payload}


@router.get("/projects/{project_id}/datasets")
def datasets(project_id: str, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    return [{"id": d.id, **d.payload} for d in db.scalars(select(Dataset).where(Dataset.project_id == project_id).order_by(Dataset.created_at.desc()).limit(100))]
