# Execution boundaries
## Trusted native backend
Executes shipped deterministic Python agents with an in-memory SQLite fixture. User configuration selects only enumerated modes and scenarios. No dynamic code, shell input, user image or filesystem path is accepted. This backend is suitable for local demonstrations and tests only; UI/report configuration labels it explicitly.

## Docker native backend
Operator builds `preflight-sandbox:0.1.0`, or supplies an immutable digest through PREFLIGHT_SANDBOX_IMAGE. The command uses `--pull=never`, no host mounts, no networking, UID/GID 10001, read-only root, no capabilities, no-new-privileges, 128 MiB memory and swap ceiling, 0.5 CPU, 32 PIDs, 128 file descriptors and 16 MiB noexec/nosuid tmpfs. Docker's default seccomp profile stays active. Do not globally disable AppArmor/seccomp. Rootless daemon is preferred; validate `docker info` before operator setup.

The operator worker runs on a host with Docker CLI access. Never mount `/var/run/docker.sock` into an agent container. The default Compose worker has no daemon access and deliberately uses trusted native execution. For restricted execution, run `scripts/worker.sh` on a Docker-enabled host against the same database, set PREFLIGHT_SANDBOX_IMAGE and queue backend=docker. An image build is necessary before any run:

```bash
docker build -f infra/docker/sandbox.Dockerfile -t preflight-sandbox:0.1.0 .
```

Live tests in `tests/security/test_docker_live.py` are skipped only if the Docker executable is absent. With the executable present, daemon or image access failures fail explicitly. CI checks daemon access and builds the image from repository root before running all tests. They check actual non-root/read-only/network behavior, cgroup limits, memory exhaustion, writable disk ceilings, timeout and cleanup. Command construction tests alone do not establish isolation.

Abandoned cleanup is an operator-only method `DockerBackend.cleanup_abandoned()`. Stop workers first; it removes only containers with the Preflight sandbox label. A scheduler for age-aware cleanup is not implemented. Failure to provision a sandbox is an infrastructure result, never an agent task failure. Expired worker leases become BLOCKED and require an explicit rerun.

## Stronger isolation
`ExecutionBackend` is a protocol for future microVM backends. `StrongIsolationRequired` refuses execution. Firecracker is not implemented. Docker is an initial boundary, not a guarantee against hostile workloads. No outbound networking, provider credentials or arbitrary public tenant code is supported inside native runner containers.

## Compose service networking
The trusted API joins the ingress bridge for localhost-only port publication and the internal backend bridge for database access. The API can make outbound connections through ingress; it does not execute arbitrary agent code. PostgreSQL, Redis and the durable worker join only the internal bridge and publish no ports. Restricted native agent containers still use `--network=none`; no socket mount or outbound permission was added to them.
