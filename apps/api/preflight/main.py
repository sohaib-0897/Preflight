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
if not log.handlers:
    handler=logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(message)s'))
    log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate=False


def create_app(database=None):
    db = database or Database()

    @asynccontextmanager
    async def lifespan(app):
        import asyncio
        await asyncio.to_thread(db.initialize)
        yield
        await db.async_engine.dispose()

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
        from .telemetry import tracer, propagator, identifiers
        request_id = str(uuid.uuid4())
        with tracer.start_as_current_span('http.request',context=propagator.extract({'traceparent':request.headers.get('traceparent','')}),record_exception=False,set_status_on_exception=False) as span:
            span.set_attribute('http.request.method',request.method)
            try:
                response = await call_next(request)
            except Exception:
                from opentelemetry.trace import Status, StatusCode
                span.set_status(Status(StatusCode.ERROR,'HTTP request failed'))
                raise
            route=request.scope.get('route')
            span.set_attribute('http.route',getattr(route,'path','unmatched'))
            span.set_attribute('http.response.status_code',response.status_code)
            span.set_attribute('preflight.request_id',request_id)
            correlation_ids=identifiers(span)
        response.headers['X-Trace-ID']=correlation_ids['trace_id']
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "same-origin"
        response.headers["Cache-Control"] = "no-store"
        log.info(json.dumps({**correlation_ids, "request_id": request_id, "method": request.method, "status": response.status_code, "duration_ms": round((time.perf_counter()-start)*1000, 2)}))
        return response

    @app.get("/api/v1/health")
    async def health():
        await db.readiness()
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
    async def metrics(request: Request):
        import secrets
        token=os.environ.get('PREFLIGHT_METRICS_TOKEN')
        if not token or not secrets.compare_digest(request.headers.get('authorization','').encode(),('Bearer '+token).encode()):
            return Response(status_code=401)
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
    from .realitycheck import router as realitycheck_router
    app.include_router(realitycheck_router)
    from .security_checks import router as security_router
    app.include_router(security_router)
    return app


app = create_app()
