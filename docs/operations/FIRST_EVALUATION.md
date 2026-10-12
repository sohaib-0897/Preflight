# First evaluation

1. Start the stack using [Compose](COMPOSE.md), open localhost:3000 and create your private account. Registration creates an organization and workspace; no default password exists.
2. Create a project. In Agents, connect a native agent with behavior accurate and version 1.0.0.
3. In Evaluations choose that version, native benchmark, trusted offline demo, one trial and seed 42. Keep all eight scenarios. Queue the run. Compose's ARQ worker executes automatically; a development API without Redis provides Execute native demo for native fixture code only.
4. Inspect attempts and their Trace, RealityCheck, Security and Review tabs. The refund transaction and restricted resource checks inspect actual fixture state. Trace events distinguish broker evidence from agent-reported events. Unexecuted security checks remain NOT_RUN.
5. Add version 2.0.0 with regressed behavior. Execute an identical suite, then select both completed runs in Comparisons. The scripted regression fails four native cases; this demonstrates fixture differences, not real model quality.
6. Apply the default native smoke policy from the run. Accurate passes; regressed fails. A small subset is INCONCLUSIVE under its minimum sample requirement. Configure stricter versioned policies in Release gates.
7. Use Reports or the run's export links for JSON, HTML and PDF. PDF is a bounded overview with explicit Unicode escapes where standard fonts lack glyphs; JSON/HTML preserve complete evidence. Save an integrity-checked artifact snapshot for later authorized retrieval.

Use false-completion for claimed success without a refund, unsafe for synthetic canary/injection and denied operations, and slow for measured delays and invocation differences. Token usage and cost are unavailable because native demos do not invoke a model. The retry case returns one deliberately synthetic timeout.

RealityCheck lets you import versioned JSON reference facts, verify explicit claims, author configured assertions and assign reviewers. Original automatic evidence survives an override. A critical security finding can still block release.

Docker evaluations require a separately controlled operator worker and prebuilt sandbox image. Settings shows actual queue readiness. A trusted in-process demo never pretends to provision a container. Optional official benchmarks require their pinned environments and currently execute documented scripted smoke presets only.
