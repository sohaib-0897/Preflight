# ADR 001: modular monolith
Accepted. Share evaluation/scoring/security logic between CLI, API and isolated fixture runner. Keep orchestration durable in the database. A dedicated worker claims jobs atomically. The transport layer must authorize access before loading any child entity. Native built-in scenarios use a enforcing broker and per-attempt SQLite fixture. No dynamic imports or arbitrary code on the trusted backend.

Docker CLI runs only operator-installed, pinned native image with no mounts, network, capabilities or credentials. Public multi-tenant arbitrary code is refused until a stronger isolation backend exists. Provider-neutral storage and execution protocols permit future integrations without claiming implementation.
