# CEO leadership lease and fencing contract

Status: **SPECIFIED, NOT IMPLEMENTED OR DISTRIBUTED-SYSTEM TESTED**.
The [lease schema](../schemas/leadership_lease.schema.json) describes a snapshot,
not an election service.

## Authority and storage prerequisites

One persistent lease row per organization and logical CEO. Required storage:
durable atomic transactions, serializable conditional updates/row locking,
linearizable access to the authoritative lease (not a stale replica), a monotonic
persistent epoch counter, and one database-side time/expiration rule.
Partitioned minority replicas must not acknowledge authority. Lease times cannot
use a client clock; a database time regression or unknown clock bound must stop
lease granting/writes until resolved. Database failover must preserve committed
epochs, expired-lease semantics, and ordering. The adapter must demonstrate this.

No leader decision uses only PID existence, local locks, heartbeats, cached lease
data, or a worker's assertion. If the store cannot provide these properties,
leadership is not safe and the runtime stays read-only/stopped.

## Atomic operations

1. **Preflight:** a candidate authenticates, verifies its mandate and pinned Git
   policy, and reconstructs a read-only organizational snapshot before seeking
   control. Missing governance/approval data blocks acquisition.
2. **Acquire:** in one transaction lock the singleton row; permit acquisition
   only when UNHELD or database time is at/after expiration. Verify expected
   lease version, increment the durable epoch (never reset/reuse), set a new
   controller-instance/node holder and database-timed expiration, and append an
   acquisition/handover event with previous owner, new owner, reason, timestamp,
   and epoch. Initial acquisition has a null previous owner.
3. **Reconstruct:** the new holder is RECONSTRUCTING, not business-write capable.
   Read a consistent post-acquisition snapshot and events after the preflight
   watermark. Reconcile tasks, approvals, budgets, policies, risks, and outstanding
   effects. Only a fenced CAS transition to ACTIVE permits business operations.
4. **Renew:** explicitly transact using matching holder, epoch and lease version,
   before database-time expiration. Extend from current authoritative database
   time and append a renewal event. An expired holder cannot renew; it must
   reacquire at a strictly newer epoch, including when it is the same process.
5. **Write:** every authoritative mutation transaction checks matching current
   epoch AND holder AND ACTIVE state AND unexpired lease. Hold the lease
   guard/serialization lock through the write's linearization/commit boundary.
   Acquire, expiration, and business mutations must have a proven total order;
   a check performed earlier in another transaction is insufficient.
6. **Release:** a matching unexpired holder atomically clears authority to UNHELD
   and appends the release event; retain epoch/high-watermark and last-owner
   history. A stale release cannot clear a successor. Release/renew are explicit,
   not inferred from process death.

Expiration is exclusive: valid only while database time `< expires_at`; at
equality a write/renew fails. Overlapping acquisition races allow one committed
winner. If acquisition response is lost, query by request/idempotency key and
holder before acting; never assume success.

## Fencing outside the database

Every authoritative write API, outbox dispatcher, budget service, artifact
publication pointer, and governed effect gate must validate the current fence
at its own linearization point. Private staging blobs may exist without authority;
only fenced transactions publish their authoritative references.

A network API call cannot be atomically coupled to a database commit merely by
checking the lease first. External effect adapters need durable intent/outbox,
idempotency keys, bounded authorization, and reconciliation. If a target cannot
reject stale/duplicate actions, do not permit autonomous non-idempotent effects.
No autonomous financial transactions are enabled.

## Partitions, handover, and restore

A disconnected old process may keep computing, but must be unable to commit.
Local timers trigger conservative stopping, not permission to extend authority.
New ownership always has a larger epoch. Fail closed if exclusivity cannot be
proved; do not "force promote" a second database or copied local cache.

Restore must not roll the epoch counter back. Retain an independently protected
high-watermark and fence/isolate every old authority endpoint and credential
before restoring; acquire above every epoch that might have been issued.
If the watermark is unknown or old endpoints cannot be fenced, remain stopped.
The external watermark/fencing implementation is DEFERRED and a deployment gate.
