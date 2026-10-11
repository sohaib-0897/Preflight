#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHONPATH=tests .venv/bin/python -m pytest -q
npm run typecheck
npm run build:offline
npm run test:web
.venv/bin/python -m pip check
.venv/bin/python scripts/demo.py --mode accurate --output .local/verified-native.json
set +e
.venv/bin/python scripts/demo.py --mode regressed --output .local/verified-regressed.json
result=$?
set -e
test "$result" = 1
.venv/bin/python -m compileall -q apps/api packages scripts
