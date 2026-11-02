# CEO leadership handover protocol

Status: **SPECIFIED, NOT EXECUTABLE**. Organizational identity remains `amo`;
the logical CEO remains `amo-ceo` throughout. Use the existing
[handover report](CEO_HANDOVER_TEMPLATE.md), not a duplicate template.

## Before transfer

1. Verify outgoing mandate, current owner/controller/node, lease version/epoch,
   approved Git baseline, database/event watermark and artifact digests.
   The successor performs read-only preflight reconstruction before acquisition.
2. Append a handover-intent event with previous owner, intended new owner, reason,
   timestamp, current epoch and request ID. In unplanned failure the successor
   records the observed previous owner and failure reason in acquisition; do not
   fabricate an outgoing sign-off.
3. Quiesce dispatch and new effects; persist current organizational state,
   verified outputs/checkpoints, running tasks and outstanding operations,
   reservations, approvals, active risks and unresolved decisions. Lost source
   nodes leave explicit uncertainty, not assumed completion.

## Exclusive leadership transfer

4. Release the old lease using matching holder/epoch/version, or wait for
   authoritative database expiration. Do not use a local timeout or claim
   release when unreachable. Old result/effect submission remains fenced.
5. Successor acquires atomically with a strictly greater epoch and
   RECONSTRUCTING state, recording previous/new owners, reason and timestamp.
   Verify the committed response against authority; an ambiguous response is
   resolved by idempotency key, not another unverified leader.
6. Reconstruct again from a consistent post-acquisition database snapshot and
   events since the preflight watermark. Verify current Git/knowledge references,
   approvals, task owners, pending effects, risks and permission/budget policy.
7. Record the report and complete fenced readiness/ACTIVE transition only when
   the same existing operational mandate covers takeover and required human
   acceptance is present. If not, remain read-only/stopped; no new mandate is
   inferred from holding the lease.

## Resume

8. Revalidate each task. Old controller-epoch assignments cannot commit; explicitly
   fence/reassign with a new task execution epoch. Resume only checkpoint-capable
   or demonstrably restart-safe work; block unknown/non-idempotent effects.
9. Append completion/acceptance events, link the handover report, and monitor
   stale-result rejections, budget reconciliation and unresolved effects.
   Failure releases/expires the new lease; rollback is another fenced handover,
   never reuse of an old epoch or erasure of the failed transfer.

Human approval of governance changes remains mandatory under G-001. A previously
approved failover mandate may eventually cover ordinary process replacement;
none exists now. Human identity enrollment, mandate policy and runtime remain
DEFERRED, so this repository authorizes no operational takeover.
