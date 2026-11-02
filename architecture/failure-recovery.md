# Failure recovery

Status: **SPECIFIED acceptance procedures; no live failure tests performed**.
All recovery obeys [lease fencing](leadership-lease.md),
[task transfer](task-lifecycle.md), and the
[handover protocol](../migrations/ceo_handover_protocol.md).

| Failure | Required safe response and recovery |
| --- | --- |
| Local machine shutdown | Stop dispatch, checkpoint if possible; otherwise let leases expire at the authority. Only a newly fenced controller may resume. LOCAL_ONLY may stay unavailable until local storage recovers. |
| Cloud server restart | New runtime instance, verify durable database/artifacts and registered node identity, reconstruct; never reuse an old controller lease as proof of leadership. |
| Database interruption | Stop authoritative writes, dispatch and effects requiring authorization. Do not promote caches. After service recovers, verify committed epochs/versions and reconcile uncertain transactions by request ID before acquiring/renewing. |
| Network partition | Isolated side loses write/effect authority; only the connected authoritative side can obtain a valid lease. No reachable authority means no leader writes. Reconnect reports are version/fence checked. |
| Model provider outage | Bounded safe retry or policy-permitted gateway reroute, preserving privacy/permissions/budget. Otherwise BLOCKED/FAILED; a replacement provider is not a new agent/CEO. |
| Execution node failure | Fence assignment, preserve verified checkpoints, reconcile external intents, increment execution epoch and reassess restart eligibility before reassigning. |
| Corrupted local cache | Quarantine/discard only the identified cache, verify canonical hashes and refetch pinned sources. Cache cannot repair or overwrite authority. |
| Incomplete task/effect | Read durable intents/results/provider operation IDs. Verify checkpoint and effect state; unknown outcome remains BLOCKED for reconciliation/human review, not blindly retried. |

## Coordinated recovery checklist

Freeze unsafe actions, record incident/last known owners and epochs, preserve
evidence, verify current authority and approved policy commit, identify running
tasks/reservations/outbox/approvals/risks, and recover using the handover protocol.
Stage artifacts before publishing references and use idempotent event replay
from the consistent watermark. Reject stale queued reports rather than
last-write-wins merging.

Database disaster restore must isolate old writers/endpoints and exceed every
previously issued leadership epoch using an independently protected watermark.
An old backup cannot reset the epoch counter. If this cannot be proven, stop.
Restoring a database is not permission to change G-001 or erase an incident.

Record previous/new owners, reason, times, epochs, affected tasks/checkpoints,
approvals, data loss/uncertainty, recovery evidence, and acceptance in new events
and handover reports. Approval for a new operational mandate or governance change
remains separate from lease transfer.

Recovery objectives, on-call custodian, database topology, effect adapter
reconciliation and independently anchored backups are UNDECIDED/DEFERRED.
The [scenario matrix](../evaluation/continuity_tests/hybrid_runtime_scenarios.md)
defines future conformance tests; documentation is not proof they pass.
