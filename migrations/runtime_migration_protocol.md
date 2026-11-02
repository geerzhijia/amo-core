# Runtime, node, profile, and model migration

Status: **SPECIFIED; no migration has been performed**.
Use the [organizational reconstruction protocol](README.md) together with the
[CEO handover protocol](ceo_handover_protocol.md) when leadership moves.

1. Classify the change: model adapter/configuration, agent instance, execution
   node, deployment profile, controller leadership, or authority-store migration.
   Record source/destination, rationale, risk, required mandate and rollback.
2. Export/pin Git policy commit and hashes, consistent database snapshot and
   event watermark, agent/configuration/node/task IDs, budgets/reservations,
   approval evidence, artifacts/checkpoints and outstanding operation IDs.
   Mark missing data and retain an independently anchored epoch high-watermark.
3. Verify destination capabilities, registration, privacy/residency, resource
   limits, least-privilege tools, gateway routes and separately authorized secret
   profiles. Do not copy personal sessions or grant authority from location.
4. Quiesce and fence the affected source. For each task persist completed work,
   execution state and effects; independently verify checkpoint compatibility.
   Transfer/restart only under the task lifecycle, with new execution epoch and
   version. Non-checkpointable work restarts only from a verified checkpoint or
   safe initial state; uncertain side effects require reconciliation.
5. If moving the controller, reconstruct before acquisition and after obtaining
   the new fenced lease as the handover protocol requires. The agent ID remains
   `amo-ceo`; runtime-instance ID, node and epoch change.
6. If moving the authoritative database, freeze writes and drain/reconcile
   outbox/intents, snapshot at one consistent watermark, fence old endpoints
   and credentials, validate restore and epoch continuity, then redirect to
   exactly one verified authority. Never dual-write two independent primaries.
   Inability to prove fencing/high-watermark means stay stopped.
7. Verify references, events, policy meanings, pending approvals, task ownership,
   budgets and active risks. Run offline checks and future adapter conformance
   tests; seek required human acceptance before resuming the approved scope.
8. Append migration/handover events and report with old/new identities,
   configurations, versions, epochs, artifacts, outcomes, uncertainties and
   rollback point. Preserve all prior records. Rollback uses new fences.

Model changes cannot silently reinterpret principles or inherit provider
permissions. LOCAL_ONLY, CLOUD_ONLY and HYBRID are deployment profiles of the
same organization, never independent AMO copies. Exported snapshots/caches do
not become a new live authority merely because they can be loaded.
