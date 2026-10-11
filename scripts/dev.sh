#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH="apps/api:packages/evaluation-core:packages/agent-adapters:packages/benchmark-adapters:packages/scoring:packages/security:packages/python-sdk"
exec .venv/bin/python -m uvicorn preflight.main:app --host 127.0.0.1 --port "${PREFLIGHT_PORT:-8000}"
