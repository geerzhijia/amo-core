# Hybrid runtime architecture

Selection: [ADR-0001](decisions/ADR-0001-single-logical-ceo.md),
**CONFIRMED_BY_FOUNDER**, accepted 2026-11-01.
Status of mechanisms below: **DESIGNED / SPECIFIED, NOT IMPLEMENTED**.

AMO has one identity, one logical CEO (`amo-ceo`), one governance system, and one
authoritative organizational state. Multiple models and execution nodes serve
that organization. There are no independent Local CEO and Cloud CEO identities.

```text
Human administrator / separate human approval authority
                         |
         Control Plane (one valid CEO leadership lease)
         state APIs / scheduling / registries / policy checks
                 |                         |
    Transactional live authority      Pinned Git governance
                 |
         Authorized task/result interfaces
                 |
       LOCAL nodes              CLOUD nodes
       agent instances          agent instances
                 |                         |
         Provider-independent Model Gateway
                 |
         Providers / local inference

Knowledge storage: content-addressed reports and checkpoints,
referenced by authoritative state, not an alternate authority.
```

The logical CEO leads strategy, interprets the constitution and active principles
within their actual approval status, researches, analyzes, makes decisions within
its mandate, creates/assigns tasks, manages subagents, monitors execution,
reviews results, tracks risks/performance, and preserves continuity. It should
delegate specialized execution rather than personally perform every task.

Hosting the controller does not grant a node authority. Its separately
authenticated controller role, valid lease, approved mandate, and current policy
baseline must all be checked.

## Specification map

| Contract | Document |
| --- | --- |
| Coordination and leadership | [Control Plane](control-plane.md), [lease](leadership-lease.md) |
| Nodes and profiles | [Execution Plane](execution-plane.md), [hybrid runtime](hybrid-runtime.md) |
| Tasks and storage ownership | [Lifecycle](task-lifecycle.md), [consistency](data-consistency.md) |
| Models and permissions | [Gateway](model-gateway.md), [security](security-boundaries.md) |
| Recovery and transfer | [Failures](failure-recovery.md), [handover](../migrations/ceo_handover_protocol.md), [migration](../migrations/runtime_migration_protocol.md) |

## Delivery status

| Component | State |
| --- | --- |
| Architecture A | CONFIRMED_BY_FOUNDER |
| Protocols, boundaries, deployment profiles | DESIGNED and SPECIFIED |
| Four JSON Schemas and offline validation | IMPLEMENTED development tooling |
| Schema rejection/compatibility checks | TESTED locally; see test output |
| Live lease, scheduler, gateway, database, agents | DEFERRED; not implemented |
| Production safety, failover, performance | NOT TESTED; scenario acceptance criteria only |

Database product, hosting, isolation mechanism, approval identity/signatures,
secret store, budgets, recovery objectives, and concrete model adapters remain
UNDECIDED. No credentials, real node registrations, live tasks, or leases are
created. Existing foundation history and the draft constitution remain intact.
