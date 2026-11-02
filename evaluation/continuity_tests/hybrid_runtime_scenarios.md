# Hybrid runtime conformance scenarios

Status: **SPECIFIED acceptance criteria, NOT RUN against a runtime**.
Offline schema tests cannot establish distributed correctness. A future adapter
must demonstrate these using real transactional concurrency, controlled clocks,
crash/restart and network-partition fault injection, without production accounts.

| Scenario | Required evidence / pass condition |
| --- | --- |
| Two simultaneous CEO acquisitions | One committed winner; unique greater epoch, one singleton holder; loser read-only |
| Local partition while Cloud acquires | Old controller cannot renew/write/dispatch effects; new epoch strictly greater; no independent Local/Cloud CEO |
| Lease expires during write | Database linearization/locking proves write ordered before valid expiry or rejected; no preflight/write TOCTOU gap |
| Expired or superseded process returns | Leadership, task results, budget updates, outbox/effect publication and stale release rejected |
| Renewal/acquisition race and clock anomaly | One authoritative order; no extension after expiry; clock uncertainty fails closed |
| Lost acquisition/commit acknowledgement | Query by idempotency key resolves one recorded outcome; no duplicate grant/action |
| Controller dies during reconstruction | No business writes before ACTIVE; subsequent acquisition has greater epoch |
| Concurrent tasks and budget reservations | Different tasks run concurrently; same task has one owner; limits cannot be overspent by racing reservations |
| Duplicate task/result request | Same key/digest returns prior outcome; different content conflicts; completed task not executed anew |
| Local-to-Cloud checkpoint migration | Verified work/operations persist; new task epoch and destination credentials; source result rejected |
| No compatible checkpoint / unknown effect | Restart only from verified safe state or BLOCKED for reconciliation; never pretend process memory migrated |
| Source node keeps computing after reassignment | Old results/effects rejected or task remains blocked when external target cannot fence |
| Database outage / minority replica | No authoritative writes or cached authority promotion; no grant from stale replica |
| Database restore from older backup | Old endpoints isolated and epoch exceeds protected issued high-watermark; unknown watermark stops restore activation |
| Provider outage or missing token/cost data | Policy-safe bounded reroute or BLOCKED; unknown usage/cost explicit, not zero; no silent privacy expansion |
| Local personal login with Cloud node | Cloud denied until separate approved workload credentials exist |
| Corrupted cache / missing artifact | Canonical hashes checked; cache cannot overwrite source; missing checkpoint blocks resume |
| Rejected or pending amendment after migration | G-001 and exact review state retained; no node/model can self-activate |
| New model disagrees with principle | Difference recorded/escalated, not silently reinterpreted |
| Profile/authority migration rollback | One live authority, same AMO/CEO IDs, preserved history, new epoch rather than reused token |

Before any runtime deployment, add executable backend/effect-adapter tests for
these scenarios, verify human authorization and operational controls, and record
results with software/backend versions and evidence. No row above is marked
passed merely because the corresponding document or schema exists.
