# Comparisons and release policies

Compare completed runs from the same project. Benchmark/version, scenario IDs,
trials, seeds, execution backend, dataset fingerprint, custom assertions, trusted
source versions and security mode must match. Different model, prompt, tool or
framework versions can be compared through immutable agent configurations when
both agents implement the same declared scenario contract. Incompatible or missing
paired attempts are explicitly rejected rather than normalized into a favorable score.

Task comparisons pair scenario/trial outcomes and report sample counts, distinct
scenario counts, wins, regressions and an exact paired task test on scenario clusters.
Deterministic repeated trials are correlated. Small differences or small samples do
not establish improvement. The 95% task significance indicator is evidence about
these recorded cases, not a production performance estimate. Latency differences use
an approximate scenario-cluster percentile bootstrap (1,000 draws, seed 42), with
unknown intervals for fewer than two scenarios. Measured timings vary between runs. Connected latency measures the gateway round trip;
fixture validation and queue waiting are not included in that agent latency field.

Dimensions retain their own assessed denominators: structured exact/tolerance
accuracy, state validation, trusted factual correctness, configured assertions,
validated tool execution, timeout recovery and observed security finding rate. Tool
execution counts enforcing-broker statuses or declared tool assertions; it is not
a general semantic tool-choice judge. Missing or non-applicable dimensions show
Unavailable rather than zero. Security finding rate is observed finding frequency,
not a general security rating. Human review results reflect latest persisted reviews.

Token usage is summed only when every attempt reports valid nonnegative integers.
Costs require explicit estimated_cost_usd, currency USD and cost_source in the agent
usage record. Estimated cost means USD per task attempt; total estimated cost is
separate. These are agent/provider reports, not independent billing verification.
Partial coverage, invalid/negative/nonfinite values and absent prices stay unknown.
Native fixtures never synthesize token measurements or API prices.

Policies are immutable named versions. Admins configure minimum task success,
distinct scenario sample count, required scenarios/benchmark suites, critical/high
finding budgets, latency, reported per-task cost, paired regression tolerance,
completed review count, latest human approval count and mandatory security categories.
Concurrent version conflicts return 409 so callers refresh and retry safely.

A latest failed or inconclusive review is not an approval. Optional human accuracy
overrides preserve the automatic summary and never clear critical security findings.
Required security checks need executed evidence; NOT_RUN/INCONCLUSIVE or absent
checks block PASS. NOT_APPLICABLE alone does not satisfy a mandatory category.
Dependency artifacts remain separate scoped advisory evidence and do not silently
satisfy a broad missing dependency check. Missing baseline, cost, sample size,
reviews or coverage yields INCONCLUSIVE; an observed policy violation yields FAIL.

The offline CLI `python scripts/demo.py --mode accurate --output .local/report.json`
returns 0 for PASS, 1 for FAIL, 2 for INCONCLUSIVE or invalid policy input. Use
`--policy path.json` for overrides; unknown fields, invalid thresholds and malformed
required lists are refused. Example `.github/workflows/release-example.yml` evaluates
the checked-in candidate mode on pull requests. A regressed candidate causes the
release-gate job to fail; configure it as a required branch check in GitHub settings.
Preflight never automatically deploys a candidate.
