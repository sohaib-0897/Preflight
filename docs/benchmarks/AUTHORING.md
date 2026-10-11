# Native suites and scoring
`preflight_eval.native.SCENARIOS` enumerates versioned fixture scenarios. A scenario receives a fresh SQLite broker state. Agent modes choose shipped behavior; arbitrary Python or uploaded scripts are not executed. New scenario code is an operator repository contribution with tests, not a tenant upload. API datasets are immutable native subsets; changing a subset creates a new dataset fingerprint. General custom uploaded task authoring is not yet exposed.

A correct refund requires exactly one transaction totaling 7500 cents and an unchanged restricted resource. Broker parameter validation is type-aware and bounded. Calling a tool with the same transaction ID is idempotent. Claimed completion without the expected state produces hallucinated_completion.

structured_compare validates explicit fields, types, exact values or numeric tolerances. No semantic/LLM judging is used. Factual checks consume structured claims and a local authorized key/value corpus; supported, contradicted and unverifiable outcomes preserve source URI, content digest and retrieval timestamp. Unknown claims are never scored as definitive real-world truth. General prose claim extraction/retrieval and judge integrations remain outstanding.

confidence_assessment computes Brier score only when a correctness label exists and preserves abstention metadata; absent ground truth remains inconclusive. It validates finite confidence values. Human reviews append outcomes and justifications with audit history; release policies may explicitly opt into overrides while preserving automatic results.

Aggregation reports actual elapsed latency, scored attempts, distinct-scenario effective sample size and a Wilson interval for the all-trials-pass outcome per scenario. Deterministic repeated trials do not increase independent samples. API usage/cost are null unless actually instrumented; no synthetic prices or token counts are presented as real measurements.

External suite adapters have a separate [status](UPSTREAM.md). Preflight-authored contract fixtures are not official benchmark scenarios or results.
