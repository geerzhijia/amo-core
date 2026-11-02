# Deployment profiles

Status: **SPECIFIED; none deployed**. All profiles use the same AMO identity,
logical CEO, interfaces, schemas, and G-001 boundary.

| Profile | Nodes | Live persistence | Operational implication |
| --- | --- | --- | --- |
| LOCAL_ONLY | LOCAL only | Local transactional database or explicitly configured shared authority | No mandatory cloud dependency; shutdown may stop the organization operationally, not erase identity |
| CLOUD_ONLY | CLOUD only | Persistent cloud transactional authority | Designed for 24/7 service, not a guarantee of uptime |
| HYBRID | Authorized LOCAL and CLOUD nodes | One centralized logical transactional authority | Shared scheduling and safe leadership failover; no offline write leader |

"Centralized" means one ordered authoritative history, not necessarily one
unreplicated physical server. HA replicas must obey the same consensus/transaction
contract; asynchronous replicas cannot independently grant leases.

A LOCAL_ONLY deployment may use a single-host database with an explicitly
enforced single-host failure boundary. Do not share a local database file across
machines or promote a copied cache into a second authority. Any introduction of
multiple hosts/controllers requires a store proven to meet the
[lease guarantees](leadership-lease.md); a file lock is not that guarantee.
No engine is selected here.

In HYBRID, the CEO process can move between Local and Cloud with a new controller
instance, fresh leadership epoch, reconstruction, and scoped credentials.
It does not create a Local CEO and Cloud CEO. Nodes can concurrently run
different tasks; a single task has one current assignment/execution epoch.

Every profile explicitly configures authority endpoint, organization key,
approved Git baseline, artifact endpoints, node registration, permission profile,
budget policy, model gateway routes, and runtime-specific secret references.
These are deployment inputs, not committed secrets.

Profile changes follow the [runtime migration protocol](../migrations/runtime_migration_protocol.md).
Changing hosting does not amend principles, grant operational authority, enroll
approvers, or inherit another machine's interactive personal login.
