# RealityCheck

Project administrators ingest small JSON reference documents as named scalar facts.
Every ingestion creates an immutable source version, provenance URI, content hash
and timestamp. Claim verification retrieves only authorized project sources and
records source versions and retrieval timestamps. Explicit subject/value claims and
`subject = JSON-value` lines are supported; general free-form claim extraction and
LLM semantic judges are not implemented. Contradicted, unsupported and conflicting
claims are distinguished. Inconsistent reference versions require review.

Custom datasets wrap the shipped eight fixture environments with a custom request,
structured output/state assertions, numerical tolerances, required/prohibited tool
calls, exact tool sequences and bounded read-only SQL assertions. HTTP agents receive
the custom request; native agents retain their documented scripted fixture behavior.
This does not offer arbitrary user code or arbitrary host database queries. Only
captured actual fixture rows populate the SQL assertion database. SQLite authorization
restricts reads to the two fixture tables, selected aggregates, and a statement budget;
ATTACH, writes, filesystem reads and other operations are refused.

Dataset fingerprints include immutable reference records and configured assertions.
Missing snapshots and unavailable/conflicting evidence are INCONCLUSIVE; unassessed
attempts do not become false zero-accuracy scores and block release when coverage is
required. An answer saying “done” cannot override a missing transaction.

Supplemental assertions on existing attempts append assessment evidence without
changing the original run score. Configure a custom dataset before execution for
assertions to contribute to automatic scoring. Administrators can assign eligible
organization developers as reviewers. Assigned decisions require a justification,
append HumanReview history and audit events, and preserve original automated results.
Conflicting human outcomes are visible in the review queue. Review overrides affect
a release only when its versioned policy explicitly honors them; security findings
remain independently enforced.

The browser RealityCheck module supports reference ingestion, claim verification,
review queues, and links to actual attempts. Evaluation details expose assertion
validation, assessment history and assignment. Custom datasets can be authored from
the Benchmarks module. No hosted inference or paid provider is required.
