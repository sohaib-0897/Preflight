"""Operator-owned HTTP bridge for trusted Python/framework agents.

The platform never imports user-supplied code. Run this in your own environment.
Agent responses declare requested fixture actions; Preflight's broker authorizes
and applies them. Remote claims about side effects are not treated as proof.
"""
import asyncio
import hmac
from typing import Callable
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field


class Invocation(BaseModel):
    inputs: dict
    seed: int = 42
    trace_id: str = Field(default="", max_length=128)


def create_agent_app(invoke: Callable, bearer_token: str | None = None, timeout=20):
    app = FastAPI(title="Preflight agent bridge")

    def authenticate(request):
        if bearer_token and not hmac.compare_digest(request.headers.get("authorization", ""), "Bearer " + bearer_token):
            raise HTTPException(401, "Agent authentication required")

    @app.get("/health")
    async def health(request: Request):
        authenticate(request)
        return {"status": "ok", "interface": "preflight-http/v1"}

    @app.post("/invoke")
    async def execute(body: Invocation, request: Request):
        authenticate(request)
        try:
            async with asyncio.timeout(timeout):
                result = await invoke(body.inputs, body.seed)
            if hasattr(result, "output"):
                result = {"output": result.output, "events": result.events, "usage": result.usage, "actions": result.actions}
            if not isinstance(result, dict) or "output" not in result:
                raise TypeError("Agent must return an output mapping")
            result.setdefault("events", [])
            result.setdefault("usage", {})
            return {**result, "trace_id": body.trace_id}
        except TimeoutError:
            raise HTTPException(504, "Agent invocation deadline exceeded")
        except Exception:
            raise HTTPException(502, "Agent invocation failed; inspect operator diagnostics")

    return app


def serve(invoke, host="127.0.0.1", port=8090, bearer_token=None):
    import uvicorn
    uvicorn.run(create_agent_app(invoke, bearer_token), host=host, port=port)
