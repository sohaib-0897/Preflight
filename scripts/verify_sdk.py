"""Verify the installed wheel without relying on the repository PYTHONPATH."""

from importlib.metadata import version
from fastapi.testclient import TestClient
from preflight_sdk import Client
from preflight_sdk.server import create_agent_app


async def invoke(inputs, seed):
    return {"output": {"request": inputs["request"], "seed": seed}, "actions": []}


def main():
    assert version("preflight-agent-sdk") == "0.2.0"
    assert Client("http://127.0.0.1:8000").csrf == ""
    with TestClient(create_agent_app(invoke, bearer_token="synthetic-wheel-test-token")) as client:
        assert client.get("/health").status_code == 401
        headers = {"authorization": "Bearer synthetic-wheel-test-token"}
        assert client.get("/health", headers=headers).status_code == 200
        response = client.post(
            "/invoke", headers=headers, json={"inputs": {"request": "wheel probe"}, "seed": 42}
        )
        assert response.status_code == 200, response.text
        assert response.json()["output"] == {"request": "wheel probe", "seed": 42}
    print("Installed SDK wheel 0.2.0: authenticated gateway and invocation passed")


if __name__ == "__main__":
    main()
