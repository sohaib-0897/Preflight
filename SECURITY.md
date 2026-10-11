# Security policy
Preflight 0.1 is a development platform, not hardened public multi-tenant hosting. Do not expose the local demo directly to the Internet. Report vulnerabilities privately to the repository owner's GitHub security advisory channel once publishing is configured; do not include real secrets or attack third-party systems.

Native demo execution runs only trusted built-in code. It is not a sandbox. Restricted Docker source drops capabilities, runs non-root, disables network and mounts, constrains cgroups and writable tmpfs, and cleans up after execution. Live isolation tests were not executed on the implementation host because Docker is absent. Arbitrary code is refused; a stronger backend must be implemented before public hostile workloads are accepted.

Authentication uses Argon2id and expiring opaque HttpOnly SameSite=strict cookie sessions. Writes require CSRF tokens. Organizations form the authorization boundary; members can access workspaces/projects in their organization according to role. Tests exercise cross-organization denial, restricted tools, artifact isolation and redaction. See [methodology](docs/security/METHODOLOGY.md) and [sandbox model](docs/security/SANDBOX.md).

No automatic deployment, paid model calls, arbitrary network scanning or hidden reasoning capture is included. Pattern redaction is conservative but cannot identify all personal data. Keep real secrets and datasets out of demonstration prompts. Real dependency vulnerability audits remain blocked by offline access; package consistency checks are not vulnerability scans.
