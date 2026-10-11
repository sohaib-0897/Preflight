FROM python:3.12.12-slim
WORKDIR /runner
COPY packages /runner/packages
COPY scripts/sandbox_runner.py /runner/runner.py
ENV PYTHONPATH=/runner/packages/evaluation-core:/runner/packages/scoring:/runner/packages/security
USER 10001:10001
ENTRYPOINT ["python", "-B", "/runner/runner.py"]
