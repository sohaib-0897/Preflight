#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
benchmark="${1:?Choose tau3 or agentdojo}"
case "$benchmark" in
  tau3)
    target=.local/tau-venv
    source_path=.local/upstream/tau2
    if [ ! -d "$source_path/.git" ]; then
      mkdir -p .local/upstream
      git clone --depth 1 --filter=blob:none --sparse --branch v1.0.1 https://github.com/sierra-research/tau2-bench.git "$source_path"
      git -C "$source_path" sparse-checkout set src/tau2 data/tau2/domains/mock
    fi
    test "$(git -C "$source_path" rev-parse HEAD)" = fc0055dc4e0a316c3f83133267fbd6faaa770992
    ;;
  agentdojo) target=.local/agentdojo-venv ;;
  *) exit 2 ;;
esac
uv venv "$target" --python 3.12 --allow-existing
uv pip sync --python "$target/bin/python" "requirements/benchmarks/$benchmark.lock"
if [ "$benchmark" = tau3 ]; then
  uv pip install --python "$target/bin/python" --no-deps --build-constraints requirements/benchmarks/build.lock -e "$source_path"
fi
