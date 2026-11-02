# ADR-0001 - Single Logical CEO with Multiple Execution Nodes

Status: CONFIRMED_BY_FOUNDER
Accepted: 2026-11-01
Acceptance date basis: actual local calendar date at recording.
Source: founder's explicit architecture update, supplied
2026-11-01T19:48:33.325-08:00.

## Context and decision

The founder explicitly selected:
**"Architecture A: One Shared Logical CEO with Multiple Execution Nodes."**

AMO has one organizational identity, one persistent logical AI CEO, one
authoritative governance system, and one authoritative organizational state,
with multiple independently identifiable execution nodes and agents.
LOCAL and CLOUD are environments, not separate organizations or CEO identities.
The stable CEO agent ID is `amo-ceo`; controller processes and models are
replaceable instances of that role.

The logical CEO persists when a process stops, restarts, migrates, or changes
models. A node hosting the CEO process gains no organizational authority from
hosting it. Different tasks may execute concurrently; at most one controller
holds a valid organizational leadership lease at any time.

## Required design consequences

- Separate a coordinating Control Plane from an agent-running Execution Plane.
- Use a transactional persistent authority for live state, expiring leadership
  and task leases, monotonically increasing fencing epochs, explicit renewals,
  compare-and-swap versions, idempotency, and an append-only event history.
- Validate current leadership fencing within every authoritative mutation.
  Stale or partitioned controllers fail closed, never become a second CEO.
- Preserve permanent agent/task/node identities separately from configuration,
  process instances, models, and current location.
- Support LOCAL_ONLY, CLOUD_ONLY, and HYBRID without changing AMO identity.
- Keep governance versions in Git, live coordination in a transactional database,
  and exportable research/artifacts in knowledge storage.
- Require a provider-independent Model Gateway and separately authorized runtime
  credentials. A personal local login does not authenticate a cloud node.
- Preserve G-001 unchanged across all nodes, processes, agents, and providers.
- Specify verified checkpoint/restart and handover; do not assume arbitrary
  in-memory execution can be moved between machines.

## Rationale, alternatives, and tradeoffs

A single logical leadership identity preserves continuity while allowing varied
execution capabilities, costs, privacy boundaries, latency, and availability.
Independent Local/Cloud CEOs and organizations were not selected; the founder
has already decided, so no architecture re-selection is needed.

A single transactional authority reduces ambiguity but makes its availability
a prerequisite for authoritative writes. Under partition, consistency and
exclusive leadership take precedence over write availability. Git synchronization,
local file locks, process liveness, and heartbeats alone are not leader election.

Provider neutrality costs adapter work. Explicit checkpoints and idempotency
cost workflow design but avoid false exactly-once and migration guarantees.

## Authorization boundary and outcome

This ADR records the explicit architectural selection and required invariants.
Detailed implementation contracts are **SPECIFIED** designs, not additional
founder-approved policies, deployment authorization, or evidence of enforcement.
The constitution remains PROPOSED; G-001 remains CONFIRMED and unchanged.
No approver enrollment, runtime activation, infrastructure, external transactions,
database engine, or provider has been authorized by this record.

Actual operational outcome: **DEFERRED**; no runtime exists to evaluate.
Validate architectural consistency now; demonstrate transactional safety in a
later isolated conformance phase before requesting any deployment approval.
Corrections/supersession require a new ADR, retaining this accepted record.

See [overview](../overview.md), [lease contract](../leadership-lease.md), and
[continuity scenarios](../../evaluation/continuity_tests/hybrid_runtime_scenarios.md).
