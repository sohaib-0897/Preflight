FROM python:3.12.15-slim
WORKDIR /app
COPY requirements.lock .
RUN pip install --no-cache-dir -r requirements.lock
COPY apps/api apps/api
COPY packages packages
COPY infra/migrations infra/migrations
COPY alembic.ini .
COPY apps/web/public apps/web/public
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app/apps/api:/app/packages/evaluation-core:/app/packages/scoring:/app/packages/security:/app/packages/agent-adapters:/app/packages/benchmark-adapters
RUN useradd --uid 10001 --create-home preflight && mkdir /app/.local && chown preflight /app/.local
USER 10001:10001
CMD ["sh", "-c", "alembic upgrade head && exec uvicorn preflight.main:app --host 0.0.0.0 --port 8000"]
