# Integrity, access, backup, and recovery

Status: **PROPOSED operational controls**, not yet deployed guarantees.

## Boundaries

The human repository owner controls administrative access. Future AI credentials
should be read-only or restricted to proposal branches: no repository admin,
force-push, branch deletion, approval credentials, or bypass privileges. Separate
proposal submission from human approval and merge. Use protected branches,
required independent review and checks, restricted bypass, and suitable
CODEOWNERS after the founder chooses verified identities. These hosting controls
are not configured or guaranteed by these files. Do not enable autonomous agents
until real permission boundaries have been verified.

No credentials, tokens, private keys, private founder information, or financial
data belong here. A public repository exposes every committed historical version.
Use references to a controlled evidence store for sensitive material; portability
requires exportable evidence, not vendor-only links. Redact before committing.
If a secret appears, revoke it first and follow an explicitly authorized incident
process; history rewriting for containment is an exceptional human-controlled
action that must itself be audited externally.

## Integrity checks

`python tools\validate.py` validates schemas, links, approval sequencing,
proposal bindings, active principle provenance, and `integrity/manifest.json`.
SHA-256 detects byte changes relative to that manifest; an attacker able to
replace both can forge consistency. A human must independently anchor the
manifest/commit digest in a separately controlled backup or signed release.

`python tools\validate.py --write-manifest` regenerates the manifest for
intentional reviewed changes. It is **not approval** and must not automatically
run to repair a failed integrity check in CI. Review each old/new digest against
the authorized change before accepting a new baseline. The manifest covers every
tracked foundation file except itself and generated/cache files. It is not
self-authenticating.

Historical decision, amendment, approval, audit, principle-version, and
constitution files are append-only by convention and CI diff checking.
Corrections are new records with references. Git administrators can rewrite
history, disable checks, change workflows, or delete the repository. Local
checks cannot prevent a malicious writer from replacing the validator or
authority list. Git alone is **not immutable or tamper-proof storage**.

## Backup and recovery expectations

Proposed targets: export after each governance activation and at least weekly
while active; recovery point <= 7 days, recovery time <= 2 days. Founder must
approve targets and assign a human custodian; none is currently provisioned.
Maintain two independently controlled copies, at least one offline, including
all Git refs, records, evidence exports, authority versions, and integrity anchors.
Use `git bundle create <backup-path> --all` in a verified clone and
`git bundle verify <backup-path>`; store outside this public repository.
Test a restore into a fresh clone quarterly and record results.

On recovery, freeze operations, preserve suspect copies, restore from an
independently verified bundle, compare against external digest/signature anchors,
run validation/tests, reconstruct state and approvals, enumerate missing evidence,
and obtain human sign-off before resuming. Record the incident, loss window,
recovery source, unresolved gaps, and authorization in new audit records.

## Future capabilities

DEFERRED: cryptographically verified human approvals, independently anchored
hash-chained audit exports, immutable/WORM backups, hosted enforcement, automated
access review, and signed release/restore attestations. Plain audit records and
hashes today provide consistency evidence, not authentication or nonrepudiation.
