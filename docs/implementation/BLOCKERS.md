# Blockers and incomplete scope

## External restrictions

- Local Codex Docker daemon access is denied at unix:///var/run/docker.sock.
  Engine/Compose CLI exist and configuration validates. Fifteen live checks fail
  their prerequisite with permission denied locally. Actual remote CI builds and
  verifies containers, PostgreSQL migrations, Redis and Compose browser execution.
  No group/socket/security settings were changed. Ordinary terminal access reported
  by the user is distinct from this session's permission.
- Hosted models/Ollama are not configured for verified inference; paid calls and
  large model downloads remain unauthorized. Offline frameworks/native/official
  scripted subsets execute without them.
- Official tau2's supported LiteLLM constraint excludes patched releases. CrewAI's
  ChromaDB audit lists no fixed version. These are unresolved optional upstream
  dependency risks, not silently waived checks. See security/DEPENDENCIES.md.

## Partially implemented or not implemented

- Official tau2 and AgentDojo support genuine documented scripted smoke subsets,
  including controlled banking injection. Full suites and arbitrary connected-agent
  official protocols are not verified/implemented.
- Most application transactions remain synchronous; async readiness/queue dispatch
  are real, but a full SQLAlchemy async service conversion is partial.
- General prose fact extraction, semantic LLM judge validation and LLM root-cause
  hypotheses are not implemented. Explicit trusted facts/deterministic validators
  and audited human reviews are implemented.
- S3/MinIO storage, OTLP exporter and microVM execution are not implemented. Local
  artifacts and metadata trace export work. Optional monitoring runtime is unverified.
- Public arbitrary-code execution is refused. Docker fixture isolation does not
  establish protection for hostile multi-tenant code. Operator host worker setup is
  required for Docker jobs; the default safe Compose stack needs no daemon socket.
- Full arbitrary-field sorting/pagination across every entity, external database
  assertions, free-form document retrieval, exhaustive assistive-technology testing,
  OCI/OS vulnerability scanning and production backup/restore certification remain
  outside the verified scope. No production-ready claim is made.

## Manual operator setup

Provide the private existing/new PostgreSQL password, create the first account,
configure TLS/secure cookies for nonlocal access, optional private gateway origins,
credential/provider budgets, official environments, independent Docker worker and
GitHub required-check branch protection. Never expose data service ports publicly.
No default/shared password, paid service, force push or volume deletion was used.
