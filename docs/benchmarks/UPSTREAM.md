# Official benchmark integration status

Verified locally on 2026-10-12 using isolated Python 3.12.15 environments.
CI confirmation is recorded separately in implementation verification.

| Benchmark | Provenance | Verification | Supported execution |
|---|---|---|---|
| τ³ / tau2 | MIT; v1.0.1, commit `fc0055dc4e0a316c3f83133267fbd6faaa770992`; package **tau2** 1.0.1 | OFFICIAL_SMOKE_EXECUTED | Official mock `create_task_1`, scripted agent/user, upstream ENV database scorer |
| AgentDojo | MIT; package 0.1.35 hash-locked, banking benchmark v1.2.2 | OFFICIAL_SMOKE_EXECUTED | Official `user_task_0`, actual tool runtime, upstream utility scorer |

Both accurate and regressed reference agents executed. Upstream scores were 1 and
0, respectively; these are integration smoke outcomes, **not** measurements of
hosted-model quality. Evaluation-time outbound connections were blocked and none
attempted. Actual API scheduling, worker execution, persisted scenario evidence,
JSON report export and conservative release gates were also verified. One independent
scenario cannot satisfy the default minimum of eight; repetition does not change that.

No full official suite, model-driven agent/user, LLM natural-language judge, voice,
or adversarial AgentDojo task is verified by these smoke runs. No benchmark results
are invented or substituted with normalization fixtures. Existing fixture tests remain
normalization contracts only. SWE-bench and GAIA remain not implemented.

## Installation and execution

Install uv 0.13.0 and use the committed hash locks. Install optional environments:

```sh
bash scripts/install_benchmark.sh tau3
bash scripts/install_benchmark.sh agentdojo
.local/tau-venv/bin/python scripts/verify_official.py tau3
.local/agentdojo-venv/bin/python scripts/verify_official.py agentdojo
```

The tau install fetches a pinned sparse checkout (source and small mock data only,
about 6 MiB), verifies its commit and installs the original package. No model weights,
voice assets or large retail/banking corpora are downloaded. Build dependencies are
version-constrained separately. AgentDojo is installed from its pinned, hashed wheel.
Benchmark dependencies are isolated from the main app and other frameworks.

Configure the API and trusted host worker with absolute interpreter paths:
`PREFLIGHT_TAU_PYTHON` and `PREFLIGHT_AGENTDOJO_PYTHON`. Their file existence enables
the corresponding UI selection; every execution independently verifies package and
scenario provenance. Only native `accurate`/`regressed` reference versions are
accepted for these presets. The connection is deliberately not advertised as support
for arbitrary HTTP agent execution against full official suites.

The upstream process runs trusted fixed code with a deadline and cancellation cleanup,
without inheriting provider credentials. It is **not a Docker sandbox**. Arbitrary
untrusted code is refused. Default Compose omits these optional environments and
reports them BLOCKED with setup guidance. Never add provider credentials to an
offline preset to make it run. Broader official execution requires a separately
implemented compatible agent protocol, authorized providers and an explicit budget.

See [tau2 upstream](https://github.com/sierra-research/tau2-bench) and
[AgentDojo TaskSuite](https://agentdojo.spylab.ai/api/task_suite/) for original APIs,
licenses and scoring definitions. Inspect preserved upstream reward evidence in each
attempt; Preflight does not rewrite official scoring.
