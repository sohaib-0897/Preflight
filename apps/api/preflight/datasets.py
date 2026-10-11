import hashlib
import json
from fastapi import APIRouter, Depends
from pydantic import Field, field_validator, model_validator
from sqlalchemy import select
from .auth import current_user, get_db, project_access, audit, Name
from .db import Dataset, Scenario, GroundTruthRecord
from preflight_eval import SCENARIOS, SCENARIO_IDS

from .realitycheck import Rules, source_records

router = APIRouter(prefix="/api/v1")


class CustomScenario(Rules):
    id: str = Field(pattern=r"^custom_[a-z0-9_-]{1,64}$")
    name: str = Field(min_length=1, max_length=120)
    base_scenario: str
    request: str = Field(min_length=1, max_length=4000)

    @field_validator("base_scenario")
    @classmethod
    def base_valid(cls, v):
        if v not in SCENARIO_IDS:
            raise ValueError("Choose a registered fixture environment")
        return v


class DatasetInput(Name):
    scenario_ids: list[str] = Field(default_factory=list, max_length=8)
    custom_scenarios: list[CustomScenario] = Field(default_factory=list, max_length=8)
    source_ids: list[str] = Field(default_factory=list, max_length=16)

    @model_validator(mode="after")
    def distinct(self):
        if bool(self.scenario_ids) == bool(self.custom_scenarios):
            raise ValueError("Choose native IDs or custom scenarios")
        if len({s.id for s in self.custom_scenarios}) != len(self.custom_scenarios):
            raise ValueError("Custom scenario IDs must be distinct")
        for scenario in self.custom_scenarios:
            if not any(
                [
                    scenario.expected_output is not None,
                    scenario.expected_state is not None,
                    scenario.expected_tools,
                    scenario.prohibited_tools,
                    scenario.expected_sequence,
                    scenario.sql_assertions,
                    self.source_ids,
                ]
            ):
                raise ValueError(
                    "Custom scenarios require explicit assertions or reference evidence"
                )
        return self

    @field_validator("scenario_ids")
    @classmethod
    def validate_ids(cls, v):
        if len(set(v)) != len(v) or set(v) - set(SCENARIO_IDS):
            raise ValueError("Choose distinct registered native scenario IDs")
        return sorted(v)


@router.post("/projects/{project_id}/datasets", status_code=201)
def create_dataset(
    project_id: str, body: DatasetInput, user=Depends(current_user), db=Depends(get_db)
):
    _, org = project_access(db, user, project_id, "developer")
    sources = source_records(db, project_id, body.source_ids)
    payload = {
        "custom_scenarios": [c.model_dump() for c in body.custom_scenarios],
        "sources": sources,
        "name": body.name,
        "scenario_ids": body.scenario_ids,
        "benchmark": "native",
        "benchmark_version": "1.0.0",
    }
    if body.custom_scenarios:
        payload["scenario_ids"] = [c.id for c in body.custom_scenarios]
    payload["fingerprint"] = hashlib.sha256(
        json.dumps(payload, sort_keys=True).encode()
    ).hexdigest()
    dataset = Dataset(project_id=project_id, payload=payload)
    db.add(dataset)
    db.flush()
    for scenario_id in payload["scenario_ids"]:
        source = (
            next(s for s in payload["custom_scenarios"] if s["id"] == scenario_id)
            if body.custom_scenarios
            else next(s for s in SCENARIOS if s["id"] == scenario_id)
        )
        scenario = Scenario(dataset_id=dataset.id, payload=source)
        db.add(scenario)
        db.flush()
        db.add(
            GroundTruthRecord(
                scenario_id=scenario.id,
                payload={
                    "method": "native versioned deterministic validators",
                    "benchmark_version": "1.0.0",
                    "scenario_id": scenario_id,
                },
            )
        )
    audit(db, user, org, "dataset.create", dataset.id)
    db.commit()
    return {"id": dataset.id, **dataset.payload}


@router.get("/projects/{project_id}/datasets")
def datasets(project_id: str, user=Depends(current_user), db=Depends(get_db)):
    project_access(db, user, project_id)
    return [
        {"id": d.id, **d.payload}
        for d in db.scalars(
            select(Dataset)
            .where(Dataset.project_id == project_id)
            .order_by(Dataset.created_at.desc())
            .limit(100)
        )
    ]
