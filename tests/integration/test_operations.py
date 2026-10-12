from sqlalchemy import inspect
from alembic import command
from alembic.config import Config
from preflight.db import Database
from preflight.jobs import claim
from preflight.storage import LocalStore
from integration.test_jobs import create_run
from asgi_client import ASGIClient
from conftest import register


def test_migration_round_trip(tmp_path, monkeypatch):
    url = f"sqlite:///{tmp_path}/migration.sqlite"
    monkeypatch.setenv("DATABASE_URL", url)
    config = Config("alembic.ini")
    command.upgrade(config, "head")
    db = Database(url)
    assert len(inspect(db.engine).get_table_names()) == 30
    command.check(config)
    command.downgrade(config, "base")
    assert inspect(db.engine).get_table_names() == ["alembic_version"]
    command.upgrade(config, "head")
    assert "evaluation_runs" in inspect(db.engine).get_table_names()


def test_artifact_integrity_authorization(client, app, tmp_path, monkeypatch):
    monkeypatch.setenv("PREFLIGHT_ARTIFACT_ROOT", str(tmp_path / "artifacts"))
    _, _, run = create_run(client)
    client.post(f"/api/v1/runs/{run['id']}/execute")
    created = client.post(f"/api/v1/runs/{run['id']}/artifacts").json()
    path = f"/api/v1/artifacts/{created['id']}"
    assert client.get(path).json()["id"] == run["id"]
    with ASGIClient(app) as outsider:
        register(outsider, "artifact-outsider@example.test")
        assert outsider.get(path).status_code == 404
    LocalStore().path(created["key"]).write_bytes(b"tampered")
    assert client.get(path).status_code == 409


def test_worker_capacity_and_duplicate_claim(client, app):
    p, body, run = create_run(client)
    r2 = client.post(
        f"/api/v1/projects/{p['id']}/runs", json={**body, "idempotency_key": "concurrent-002"}
    ).json()
    r3 = client.post(
        f"/api/v1/projects/{p['id']}/runs", json={**body, "idempotency_key": "concurrent-003"}
    ).json()
    with app.state.db.sessions() as db:
        assert claim(db, run["id"])
        assert claim(db, run["id"]) is None
        assert claim(db, r2["id"])
        assert claim(db, r3["id"]) is None


def test_web_assets_and_request_budget(client):
    assert client.get("/").status_code == 200
    assert 'type="module"' in client.get("/").text
    assert client.get("/assets/app.js").status_code == 200
    assert client.get("/assets/not-a-file").status_code == 404
    assert client.post("/api/v1/auth/register", content=b"x" * 65537).status_code == 413
