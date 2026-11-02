# Task lifecycle, ownership, and migration

Status: **SPECIFIED; no scheduler or execution engine implemented**.
Snapshot contract: [task schema](../schemas/task.schema.json).

Normal flow:
`PROPOSED -> APPROVED -> QUEUED -> ASSIGNED -> RUNNING -> COMPLETED`.
Approval is a scoped task authorization, not principle-amendment authority.
If human review is required, use AWAITING_HUMAN_APPROVAL before approval.

## Allowed transitions

| From | Permitted next states |
| --- | --- |
| PROPOSED | AWAITING_HUMAN_APPROVAL, APPROVED, CANCELLED, EXPIRED |
| AWAITING_HUMAN_APPROVAL | APPROVED, BLOCKED, CANCELLED, EXPIRED |
| APPROVED | QUEUED, BLOCKED, CANCELLED, EXPIRED |
| QUEUED | ASSIGNED, BLOCKED, CANCELLED, EXPIRED |
| ASSIGNED | RUNNING, BLOCKED, FAILED, CANCELLED, EXPIRED |
| RUNNING | COMPLETED, BLOCKED, FAILED, CANCELLED, EXPIRED |
| BLOCKED | AWAITING_HUMAN_APPROVAL, QUEUED, CANCELLED, EXPIRED |
| FAILED | RETRY_PENDING, CANCELLED |
| RETRY_PENDING | QUEUED, BLOCKED, CANCELLED, EXPIRED |
| COMPLETED, CANCELLED, EXPIRED | None; follow-up work uses a linked new task |

Every transition records reason, actor, previous/new state, version, leadership
epoch, task execution epoch, time, and evidence in the same transaction.
QUEUED/ASSIGNED/RUNNING always need valid scoped authorization. BLOCKED cannot
bypass approval by rejoining QUEUED; revalidate authorization and policy first.
No automatic transition approves an amendment under G-001.

## Persistent task contract

Permanent ID, optional parent, agent ID, node ID, runtime-instance ID, task
version, status, timestamps, task lease expiration, execution epoch, leadership
epoch, retry policy/attempt, required capabilities/permissions, expected outputs,
result/checkpoint references, outstanding operations, approval reference,
idempotency classification/key, and resume policy are distinct data.
Versions increment on every mutation; execution epoch increments on every
assignment/reassignment/retry, never resets. History retains old owners.

Only ASSIGNED/RUNNING holds an active task lease. Terminal records may retain
last-assignment IDs as provenance but no lease. Non-owning pending/blocked/retry
states clear assignment identities and release reservations as policy permits.
Task lease validity also depends on the current controller epoch; controller
failover fences old assignments even if their wall-clock task leases remain.
Renewal requires the current assignment and controller fences.

Result commit is one CAS transaction checking current leadership, task version,
execution epoch, runtime instance, assigned agent/node, lease expiration,
authorization, expected output digests, and prior terminal/idempotency result.
A duplicate exact request returns the prior recorded outcome; the same key with
different content is a conflict, not a successful retry.

## Transfer/retry protocol

1. Fence new dispatch and persist source state, completed work and verified
   checkpoint artifacts; enumerate in-flight/outstanding operation IDs and keys.
2. Determine resumability. Explicit checkpoint-capable workflows may restart
   from the last verified checkpoint. No arbitrary process-memory migration is
   assumed. Pure/idempotent restart still requires verified inputs and permission.
3. If an external effect is uncertain, block for reconciliation/human review.
   UNKNOWN/NON_IDEMPOTENT tasks have no automatic retry/migration authorization.
4. Transactionally end the old assignment, increment task version/execution
   epoch, record source/destination/reason/checkpoint, and queue only if safe.
   Require verified cancellation or effect gating when the old node may still
   operate; lease expiration alone cannot undo a remote side effect.
5. Revalidate capabilities, privacy, permissions, budget, approvals, and
   destination credentials. Assign under the current controller's epoch.
6. Reject all source-node stale results. A current leader may adopt a staged
   artifact only after independent verification and a new fenced event; never
   silently relabel a stale result as current.

Attempts are bounded by max_attempts, allowed error codes, deadline/expiry and
budget. Use persisted bounded backoff and stable operation idempotency keys.
COMPLETED requires a verified result reference; exhausted retries remain FAILED.
