# Control Plane

Status: **SPECIFIED; no service implemented**. Constraints derive from ADR-0001
and confirmed G-001. Detailed permission policies remain PROPOSED.

The Control Plane is a logical set of interfaces backed by one transactional
authority, not another organizational identity. It owns logical CEO leadership,
task scheduling, agent/node registries, permission and budget enforcement,
organizational state coordination, task ownership, event recording, and recovery.
It may later have replicated stateless API workers; those are not extra CEOs.

## Interfaces and transaction boundary

All commands authenticate a principal and carry organization ID, request ID,
idempotency key, expected record version, and current leadership epoch.
Task commands additionally carry task ID, task version, task execution epoch,
assigned agent/runtime instance/node, and lease identity.

Within one serializable transaction (or an equivalent proven conditional-write
protocol), the authoritative mutation boundary:

1. Verifies the principal's scoped mandate and the pinned active Git policy.
2. Locks/checks the singleton CEO lease against database time, epoch, holder,
   expiration, and ACTIVE reconstruction state.
3. Checks expected versions, task ownership/fences/lease, permission requirements,
   task approval and, where needed, separately verified human approval.
4. Reserves/charges budget atomically with the operation intent, including
   concurrent reservations; unavailable accounting fails closed.
5. Applies the change, increments versions, appends the event, records the
   idempotency result, and writes any outbound intent to a transactional outbox.

No separate preflight check followed by an unguarded write is safe. Every write
path, including result ingestion, approval-status recording, configuration,
budget settlement, and human-originated commands, crosses this boundary.
Humans authenticate independently; the CEO's fence never substitutes for consent.
Lease acquire/renew/release use the special atomic rules in the
[lease contract](leadership-lease.md), not ordinary business commands.

## Authority versus infrastructure

The CEO interprets and recommends within approved governance; it cannot activate
principle amendments. Nodes only submit reports/proposals through scoped
interfaces. A report, Git change, database flag, or model output cannot itself
manufacture a human approval. Repository publishing credentials and approval
credentials must not belong to the controller.

Non-leader controllers may read and reconstruct. They cannot schedule, reserve
budget, alter task ownership, or publish authoritative state. Loss of lease,
unknown policy, or loss of the authority connection means read-only or stopped.

## Registry invariants

Uniqueness constraints enforce one organization key `amo`, one CEO identity
`amo-ceo`, unique permanent agent/node/task IDs, and one CEO lease row.
Runtime instance IDs identify replaceable executions, never permanent agents.
Registry suspension/revocation is independently authorized and evented.
These constraints must eventually be enforced in storage, not merely UI code.
