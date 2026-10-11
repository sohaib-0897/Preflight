from asgi_client import ASGIClient as TestClient
from preflight.main import create_app
from preflight.db import Database


def test_health(tmp_path):
    with TestClient(create_app(Database(f"sqlite:///{tmp_path}/test.sqlite"))) as client:
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["database"] == "ok"
        assert response.headers["x-request-id"]
        assert client.get("/openapi.json").status_code == 200
