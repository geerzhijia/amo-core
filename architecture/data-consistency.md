# Authoritative data and consistency

Status: **SPECIFIED; no persistence implementation selected**.

| Store | Authoritative ownership |
| --- | --- |
| Git | Identity, constitution, principles, governance policy versions, roles, ADRs, schemas, documentation, migration protocols, historical foundation records |
| Transactional database | Live CEO lease, registries, tasks/leases/instances, runtime configuration, budget reservations/consumption, live decision and approval status, ordered events |
| Knowledge/artifact storage | Exportable research, reports, references, large documents, verified checkpoints and result bytes |
| Node cache | Non-authoritative pinned copies, staged outputs, queued reports; never an alternate write authority |

This is one coherent organizational state with separate owners per data class,
not competing copies. At this phase no live database exists; foundation records
in Git describe the actual non-operating stage. `operations/state.json` remains
a navigation summary, not a live coordinator.

## Cross-store references and activation

Database policy bindings include repository identity, full Git commit, path,
content SHA-256, principle ID/version, authority/approval evidence ID and digest,
and activation event ID. The approved pinned baseline, not a mutable branch name
or whichever node has newer files, defines current policy.

Changing Git does not automatically activate a policy. Verify exact human
approval and G-001 lifecycle, stage the approved Git content, then atomically
activate its pinned binding and append the event in the database. Database flags
cannot override the referenced governance. Unknown/missing/conflicting content
blocks operations. Approval-status rows are projections of exact authenticated
evidence; the runtime cannot originate human consent.

Artifacts use stable storage-neutral URIs/IDs plus SHA-256, media type, access
classification, and retention metadata. Upload immutable staging bytes first,
verify content, then transactionally publish the authoritative pointer. An
orphaned upload is not a committed result; a missing object blocks resume.
Signed expiring URLs may deliver content but are not its permanent identity.

There is no assumed atomic transaction across Git, objects, and database.
Use durable staging, a database transaction, idempotent outbox delivery, and
reconciliation. Event exports to Git/backup reference database event IDs,
sequence/watermark, hashes, and the pinned policy. Exports are historical
evidence, not a second live approval database.

## Concurrency contract

Serialize leadership and budget/ownership guards with each affected mutation.
Use expected-version CAS for agents, nodes, tasks, configuration and decisions;
reject conflicts and reload rather than overwrite newer state. Unique active
assignment constraints plus leases and execution epochs prevent duplicate
authoritative ownership. They do not prove only one physical process ran.

Persist idempotency scope/key, request digest and response/event atomically.
Deduplication must cover the entire possible replay/recovery window; deleting
keys cannot make an old effect executable again. Exactly-once external execution
is not claimed. UNKNOWN/non-idempotent effects require reconciliation.

Concurrent spending uses precise currency/units, reservations, bounded provider
allowances, and atomic consumption/settlement. Missing prices or unknown usage
do not mean zero cost. Budget and authority changes need explicit mandates.

## Recovery and offline behavior

Record a consistent database snapshot/event watermark, Git policy commit and
digests, artifact manifest, unresolved outbox/intents and epoch high-watermark
in each backup. Restore all references and reconcile pending effects before
leadership activation. Preserve the epoch rule in the lease contract.

Offline nodes can cache and queue reports, not approve, schedule authoritative
tasks, spend, or promote local state. Reconnect via the current fenced API;
stale versions conflict and require reconciliation. Never use Git pull/push,
last-write-wins files, or bidirectional database copies for live coordination.
