import os
import time
import uuid
import json
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path
from sqlalchemy import text
from .db import Database

log = logging.getLogger("preflight")


def create_app(database=None):
    db = database or Database()

    @asynccontextmanager
    async def lifespan(app):
        db.initialize()
        yield

    app = FastAPI(title="Preflight API", version="1.0.0", lifespan=lifespan)
    app.state.db = db

    @app.exception_handler(StarletteHTTPException)
    async def http_error(request, exc):
        return JSONResponse({"detail": exc.detail, "error": {"code": str(exc.status_code), "message": exc.detail}}, status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        return JSONResponse({"detail": "Request validation failed", "error": {"code": "validation_error", "fields": [{"field": ".".join(map(str, item["loc"])), "message": item["msg"]} for item in exc.errors()]}}, status_code=422)

    @app.middleware("http")
    async def correlation(request: Request, call_next):
        if request.method in {"POST", "PUT", "PATCH"}:
            data = bytearray()
            async for chunk in request.stream():
                data.extend(chunk)
                if len(data) > 65536:
                    return JSONResponse({"detail": "Request body exceeds 64 KiB"}, status_code=413)
            request._body = bytes(data)
        start = time.perf_counter()
        response = await call_next(request)
        request_id = str(uuid.uuid4())
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        log.info(json.dumps({"request_id": request_id, "method": request.method, "status": response.status_code, "duration_ms": round((time.perf_counter()-start)*1000, 2)}))
        return response

    @app.get("/api/v1/health")
    async def health():
        with db.sessions() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "ok", "execution": "docker" if os.environ.get("PREFLIGHT_EXECUTION") == "docker" else "trusted-demo"}

    public = Path(__file__).resolve().parents[3] / "apps/web/public"

    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def interface():
        return HTMLResponse((public / "index.html").read_text(), headers={"Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'"})

    @app.get("/assets/{name}", include_in_schema=False)
    async def asset(name: str):
        if name not in {"app.js", "styles.css"}:
            return Response(status_code=404)
        return Response((public / name).read_bytes(), media_type="text/javascript" if name.endswith(".js") else "text/css")

    @app.get("/metrics", include_in_schema=False)
    async def metrics():
        from sqlalchemy import select, func
        from .db import EvaluationRun
        with db.sessions() as session:
            count = session.scalar(select(func.count()).select_from(EvaluationRun))
        return Response(f"# HELP preflight_runs_total Persisted evaluation runs\n# TYPE preflight_runs_total gauge\npreflight_runs_total {count}\n", media_type="text/plain")

    from .auth import router
    app.include_router(router)
    from .registry import router as registry_router
    app.include_router(registry_router)
    from .jobs import router as jobs_router
    app.include_router(jobs_router)
    from .reports import router as reports_router
    app.include_router(reports_router)
    from .datasets import router as datasets_router
    app.include_router(datasets_router)
    from .credentials import router as credential_router
    app.include_router(credential_router)
    from .connections import router as connection_router
    app.include_router(connection_router)
    return app


app = create_app()
