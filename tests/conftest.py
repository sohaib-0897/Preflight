import pytest
from asgi_client import ASGIClient as TestClient
from preflight.db import Database
from preflight.main import create_app
from preflight.auth import limits


@pytest.fixture
def app(tmp_path):
    limits.clear()
    return create_app(Database(f"sqlite:///{tmp_path}/preflight.sqlite"))


@pytest.fixture
def client(app):
    with TestClient(app) as c:
        yield c


def register(c, email="owner@example.test"):
    r = c.post("/api/v1/auth/register", json={"email": email, "password": "synthetic-test-passphrase"})
    assert r.status_code == 201, r.text
    c.headers["x-csrf-token"] = r.json()["csrf_token"]
    return r.json()


def setup_project(c):
    register(c)
    workspace = c.get("/api/v1/workspaces").json()[0]
    return c.post(f'/api/v1/workspaces/{workspace["id"]}/projects', json={"name": "Refund service"}).json()
