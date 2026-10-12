from asgi_client import ASGIClient as TestClient
from conftest import register, setup_project


def test_tenant_isolation(app):
    with TestClient(app) as alice, TestClient(app) as bob:
        p = setup_project(alice)
        register(bob, "bob@example.test")
        path = f"/api/v1/workspaces/{p['workspace_id']}/projects"
        assert bob.get(path).status_code == 404
        assert bob.post(path, json={"name": "attack"}).status_code == 404
        assert alice.get(path).json()[0]["id"] == p["id"]


def test_csrf_session_logout(client):
    register(client)
    me = client.get("/api/v1/auth/me").json()
    org_id = me["organizations"][0]["id"]
    token = client.headers.pop("x-csrf-token")
    assert (
        client.post(f"/api/v1/organizations/{org_id}/workspaces", json={"name": "x"}).status_code
        == 403
    )
    client.headers["x-csrf-token"] = token
    assert client.post("/api/v1/auth/logout").status_code == 200
    assert client.get("/api/v1/workspaces").status_code == 401


def test_viewer_cannot_write(app):
    with TestClient(app) as owner, TestClient(app) as viewer:
        p = setup_project(owner)
        register(viewer, "viewer@example.test")
        org = owner.get("/api/v1/auth/me").json()["organizations"][0]["id"]
        assert (
            owner.post(
                f"/api/v1/organizations/{org}/members",
                json={"email": "viewer@example.test", "role": "viewer"},
            ).status_code
            == 201
        )
        assert viewer.get(f"/api/v1/workspaces/{p['workspace_id']}/projects").status_code == 200
        assert (
            viewer.post(
                f"/api/v1/workspaces/{p['workspace_id']}/projects", json={"name": "forbidden"}
            ).status_code
            == 403
        )


def test_password_and_cookie_controls(client):
    assert (
        client.post("/api/v1/auth/register", json={"email": "bad", "password": "short"}).status_code
        == 422
    )
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "x@example.test", "password": "synthetic-long-passphrase"},
    )
    assert "HttpOnly" in r.headers["set-cookie"] and "SameSite=strict" in r.headers["set-cookie"]
    assert (
        client.post(
            "/api/v1/auth/login", json={"email": "x@example.test", "password": "incorrect-password"}
        ).status_code
        == 401
    )
