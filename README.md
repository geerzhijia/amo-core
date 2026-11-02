# AMO Core

**AMO (Autonomous Mission Organization) is the organization; models are replaceable infrastructure.**

This repository is AMO's authoritative, portable record of identity, governance,
institutional knowledge, and continuity. It is not a chatbot, agent runtime, legal
entity declaration, or authorization to transact.

## Current stage

| Item | Status |
| --- | --- |
| Name, model independence, repository authority, G-001 | CONFIRMED by the founder's initialization instructions |
| Architecture A: one logical CEO, multiple execution nodes | CONFIRMED_BY_FOUNDER in ADR-0001, accepted 2026-11-01 |
| Constitution v0.1 and supporting governance policy | PROPOSED; not formally approved |
| Ultimate mission, legal structure, revenue, compensation, external scope | UNDECIDED |
| Authorized human account enrollment | UNDECIDED; no account is implicitly enrolled |
| CEO runtime, subagents, finance integrations, signed approvals | DEFERRED |

No autonomous execution capability or operational authority is enabled.
Repository publication, a passing test, or a commit is **not** document approval.
See [the full file inventory](FILES.md) for all foundation deliverables.

## Read in this order

1. [Identity](AMO_IDENTITY.md), [founder brief](governance/founder_brief.md),
   and [current state](operations/state.json).
2. [Draft constitution](constitution/constitution_v0.1.md) and
   [active principles](principles/registry.json), starting with [G-001](principles/G-001-principle-amendment-authority.md).
3. [Authority matrix](governance/authority_matrix.yaml),
   [approval policy](governance/approval_policy.yaml), and
   [agent permissions](governance/agent_permissions.yaml).
4. [Decision ledger](decisions/README.md), [amendment history](amendments/README.md),
   [audit](audit/README.md), and [CEO role](agents/ceo/identity.md).
5. [Migration protocol](migrations/README.md) and
   [handover template](migrations/CEO_HANDOVER_TEMPLATE.md).
6. [Hybrid architecture overview](architecture/overview.md),
   [ADR-0001](architecture/decisions/ADR-0001-single-logical-ceo.md), and
   [CEO handover protocol](migrations/ceo_handover_protocol.md).

## Architecture

Markdown carries human-readable meaning; JSON records and JSON Schema carry
structured evidence and lifecycle state. Governance `.yaml` files deliberately
use JSON syntax, a valid YAML 1.2 subset, to avoid a YAML parser dependency.
There is no deployed database, AI provider, orchestration framework, or cloud.
The confirmed hybrid architecture specifies one logical CEO (`amo-ceo`) and
multiple execution nodes. Future live state requires a transactional database,
not Git synchronization. Git remains authoritative for identity/governance
versions; a future database coordinates leases, tasks and live status, while
knowledge storage holds referenced artifacts. No database engine is selected.
Historical records are new files, not edits to old records. Git is useful history,
but is neither immutable nor tamper-proof.

The principle registry is a current index; immutable version documents and
amendment snapshots preserve prior meanings. Current state is a non-authorizing
navigation aid: resolve conflicts against confirmed instructions, G-001, approved
records, and historical evidence, not this summary.

## Validate

Requires Python 3.10+ and the development-only JSON Schema and RFC 3339 validators:

```powershell
python -m pip install -r requirements-dev.txt
python tools\validate.py
python -m unittest discover -s evaluation -p "test_*.py" -v
```

CI runs the same checks and rejects edits/deletions to historical record files
relative to the PR base or previous pushed commit. This is a review aid, **not**
an access-control boundary. See [integrity and recovery](governance/INTEGRITY.md).
Schema validation checks structure and declared relationships, not the truth of
evidence or a person's identity. No scripts execute organizational decisions.

## Review and initial approval

Read [the founder review procedure](governance/REVIEW.md). G-001 is already a
confirmed initial design decision; it does not imply approval of the draft
constitution or proposed policies. Enroll and verify a human approval identity
before accepting any new amendment or policy activation.

## Deliberate deferrals

Empty project/task/budget, research/reference, milestone, and lessons directories
are omitted until real records exist. `operations/state.json` explicitly records
that there are no known projects or pending amendments and lists unresolved
questions. History directories exist only where an actual record is present.
Executable evaluation is kept in focused test files; the hybrid scenario
document specifies future distributed conformance tests, not passing runtime
tests. No license is selected: licensing is UNDECIDED, and public visibility
does not grant a general reuse license.

## Proposed next phase

Review the detailed specifications, enroll verified human approvers, and approve
a constitution/policy baseline. Next build an isolated, non-production persistence
adapter conformance harness for lease fencing, task ownership, crash/partition and
restore scenarios, using synthetic data and fake effect/model adapters.
No autonomous CEO is needed for that harness. Runtime deployment, external
operations, and delegation require separate approval.
