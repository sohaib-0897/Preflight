import threading
import time
import socket
import uvicorn
from conftest import setup_project
from preflight_sdk import Client


def test_installable_sdk_actual_api_roundtrip(client, app):
    project = setup_project(client)
    sock = socket.socket()
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, log_level="error"))
    thread = threading.Thread(target=lambda: server.run(sockets=[sock]), daemon=True)
    thread.start()
    try:
        deadline = time.monotonic() + 10
        while not server.started and time.monotonic() < deadline:
            time.sleep(0.02)
        assert server.started
        sdk = Client(f"http://127.0.0.1:{port}")
        sdk.login("owner@example.test", "synthetic-test-passphrase")
        agent = sdk.register_agent(project["id"], "Python SDK agent")
        run = sdk.evaluate(project["id"], agent["versions"][0]["id"], "sdk-actual-001")
        result = sdk.request("POST", f"/runs/{run['id']}/execute", {})
        assert result["status"] == "COMPLETED"
        assert sdk.run(run["id"])["summary"]["task_success_rate"] == 1
    finally:
        server.should_exit = True
        thread.join(timeout=10)
        sock.close()
        assert not thread.is_alive()
