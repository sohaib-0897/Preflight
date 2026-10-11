import asyncio
import json
import socket
import ssl
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime, timedelta, timezone
import pytest
from preflight.db import Credential
from preflight.jobs import perform
from preflight_adapters import HTTPAdapter, resolve_target
from preflight.credentials import cipher
from conftest import setup_project, register
from asgi_client import ASGIClient


@pytest.fixture
def agent_server():
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            body = json.dumps({"status": "ok"}).encode()
            self.send_response(200)
            self.end_headers()
            self.wfile.write(body)

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            assert body["inputs"]["trace_id"]
            action = {
                "tool": "refund",
                "arguments": {
                    "order_id": "order-001",
                    "cents": 7500,
                    "transaction_id": "refund-001",
                },
            }
            response = {
                "output": {"completed": True},
                "actions": [action],
                "events": [{"kind": "agent_invocation", "framework": "python"}],
            }
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()
    thread.join(timeout=5)
    server.server_close()


def test_actual_http_worker_side_effect_and_false_completion(
    client, app, agent_server, monkeypatch
):
    project = setup_project(client)
    origin = f"127.0.0.1:{agent_server.server_port}"
    monkeypatch.setenv("PREFLIGHT_AGENT_PRIVATE_ORIGINS", origin)
    agent = client.post(
        f"/api/v1/projects/{project['id']}/agents",
        json={
            "name": "Real HTTP agent",
            "framework": "python",
            "version": "1.0",
            "config": {"endpoint": f"http://{origin}/invoke"},
        },
    ).json()
    assert client.post(f"/api/v1/agents/{agent['id']}/health").json()["status"] == "ok"
    run = client.post(
        f"/api/v1/projects/{project['id']}/runs",
        json={
            "version_id": agent["versions"][0]["id"],
            "idempotency_key": "actual-http-001",
            "scenarios": ["refund"],
        },
    ).json()
    assert client.post(f"/api/v1/runs/{run['id']}/execute").status_code == 409
    assert perform(app.state.db, run["id"])
    result = client.get(f"/api/v1/runs/{run['id']}").json()
    assert result["status"] == "COMPLETED" and result["summary"]["task_success_rate"] == 1
    assert result["attempts"][0]["result"]["state"]["refund_count"] == 1
    from preflight_eval.connected import verify_response
    from preflight_adapters import AgentOutput

    false = verify_response("refund", AgentOutput({"completed": True}), 42, 1)
    assert not false["assessment"]["task_success"]
    assert false["failure"]["category"] == "hallucinated_completion"


def test_credential_encryption_and_tenant_boundary(client, app, tmp_path, monkeypatch):
    monkeypatch.setenv("PREFLIGHT_CREDENTIAL_KEY_FILE", str(tmp_path / "key"))
    project = setup_project(client)
    body = {"name": "Synthetic token", "value": "fixture-token-only-0123456789"}
    path = f"/api/v1/workspaces/{project['workspace_id']}/credentials"
    item = client.post(path, json=body).json()
    assert body["value"] not in json.dumps(item)
    with app.state.db.sessions() as db:
        record = db.get(Credential, item["id"])
        assert body["value"] not in record.ciphertext
        assert cipher().decrypt(record.ciphertext.encode()).decode() == body["value"]
    with ASGIClient(app) as outsider:
        register(outsider, "credential-outsider@example.test")
        assert outsider.get(path).status_code == 404
        workspace = outsider.get("/api/v1/workspaces").json()[0]
        other = outsider.post(
            f"/api/v1/workspaces/{workspace['id']}/projects", json={"name": "Other"}
        ).json()
        assert (
            outsider.post(
                f"/api/v1/projects/{other['id']}/agents",
                json={
                    "name": "Unauthorized",
                    "version": "1",
                    "config": {"credential_id": item["id"]},
                },
            ).status_code
            == 404
        )
    assert client.post(f"/api/v1/credentials/{item['id']}/revoke").json()["active"] is False


def test_metadata_rejected_even_if_operator_private_origin(monkeypatch):
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 0, "", ("169.254.169.254", 80))
        ],
    )
    with pytest.raises(ValueError):
        resolve_target(
            "http://authorized.example/invoke", private_origins=("authorized.example:80",)
        )


def test_real_tls_pinned_connection_preserves_hostname(agent_server, tmp_path, monkeypatch):
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "agent.example")])
    now = datetime.now(timezone.utc)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=1))
        .add_extension(x509.SubjectAlternativeName([x509.DNSName("agent.example")]), critical=False)
        .sign(key, hashes.SHA256())
    )
    ca = tmp_path / "ca.pem"
    private = tmp_path / "key.pem"
    ca.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    private.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
    )
    server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    server_context.load_cert_chain(ca, private)
    agent_server.socket = server_context.wrap_socket(agent_server.socket, server_side=True)
    original = socket.getaddrinfo
    lookups = []

    def dns(host, *args, **kwargs):
        if host == "agent.example":
            lookups.append(host)
            destination = "127.0.0.1" if len(lookups) == 1 else "169.254.169.254"
            return original(destination, *args, **kwargs)
        return original(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", dns)
    origin = f"agent.example:{agent_server.server_port}"
    result = asyncio.run(
        HTTPAdapter(
            f"https://{origin}/invoke",
            private_origins=(origin,),
            verify=ssl.create_default_context(cafile=str(ca)),
        ).health()
    )
    assert result["status"] == "ok" and len(lookups) == 1
