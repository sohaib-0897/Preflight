# First evaluation
1. Start the API with `bash scripts/dev.sh` from an ordinary terminal. Visit localhost:8000 and create your own account. Registration creates an organization and workspace; there is no default password.
2. Create a project, open Agents, and connect a native agent named Refund Agent with version 1.0.0 and behavior accurate.
3. Open Evaluations, select New evaluation, choose that version, trusted native demo, one trial and seed 42. Keep all eight scenarios selected. Queue and execute the native demo.
4. Inspect an attempt. Trace shows actual broker calls; RealityCheck shows refund cents/count and restricted resource invariants. Security distinguishes findings, passed executed checks and NOT_RUN checks.
5. Add agent version 2.0.0 with behavior regressed, run the identical suite, and compare completed runs. Four native cases regress. This synthetic agent deliberately fails; the result is evidence about fixtures, not real model performance.
6. Evaluate release policy. Default eight-case smoke policy passes the accurate mode and fails the regressed mode. A two-scenario subset is INCONCLUSIVE under the default minimum sample rule. Repeated deterministic trials do not increase independent sample count.
7. Export JSON or HTML, or save an integrity-checked artifact snapshot. Use SDK/API for artifact retrieval and full configuration.

Use behavior false-completion for missing refund state, unsafe for injection/canary exposure and denied unauthorized operations, and slow for three broker calls and actual elapsed delay. Tokens/cost remain unavailable because these agents do not invoke a model. The retry case intentionally returns one fixture timeout; timing values are actual measurements, the timeout response is explicitly synthetic.

Select Docker backend only after an operator has built the native runner and started a Docker-enabled host worker. The trusted native execute button deliberately does not pretend to provision a container. A missing Docker executable produces BLOCKED infrastructure evidence.
