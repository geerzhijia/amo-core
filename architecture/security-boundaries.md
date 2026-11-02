# Security and authority boundaries

Status: **SPECIFIED least-privilege design; enforcement is DEFERRED**.
Proposed machine-readable policies:
[nodes](../governance/node_permissions.yaml) and
[runtime roles](../governance/runtime_permissions.yaml).

| Principal | Prospective scope | Explicit exclusions |
| --- | --- | --- |
| CEO controller | Fenced planning/scheduling/state APIs under mandate | Human approval, Git admin, unfenced state writes, self-granted permissions |
| Subagent | Assigned task inputs, scoped tools, staged outputs/reports | Leadership, approvals, direct database/governance writes |
| LOCAL node | Authorized workload host and local scoped resources | Cloud credential inheritance, personal credential access, hosting-derived authority |
| CLOUD node | Authorized workload host and cloud scoped resources | Local/private data unless explicitly allowed, inherited personal login, governance authority |
| Human administrator | Verified provisioning/access/recovery mandate | Implied principle approval from admin status |
| Human approval authority | Explicitly enrolled review of exact scoped content | Implicit deployment/admin rights or blanket approval of unrelated changes |

No principal is enrolled or granted these permissions by documentation.
Default deny; effective permissions are the intersection of role mandate,
node ceiling, task requirements, privacy constraints and current policy.
Even if the same human eventually holds admin and approval roles, independently
record both scoped authorizations; possession of one never implies the other.

Execution nodes have no direct database write or authoritative Git credentials.
Only the mutation service has narrowly scoped database access and it must enforce
the current leadership fence transactionally. Protect this from raw SQL bypass;
future backend-specific roles/stored procedures and integration tests must prove
the boundary. Human recovery/admin exceptions require separate authentication,
isolation of live writers, independent audit, and explicit authorization.

Agents cannot enroll approvers, alter policy baselines, change permissions,
approve their own authority, or bypass G-001 through delegation or migration.
All runtime locations/providers inherit the same confirmed human approval rule.
No autonomous financial transactions or real financial accounts are enabled.

Use per-runtime workload identities, isolated execution/sandbox limits, encrypted
transport/storage, secret-store references, restricted outbound access, per-tool
capability grants, data classification and revocation. These controls are
requirements, not implemented services. A node gets only its assigned work's
credentials, never a personal login or a complete organization-wide secret set.

Prompt injection or provider output is untrusted input. Never treat it as a
governance amendment, credential request, or override of tool/approval gates.
Masking logs is not sufficient access isolation; artifact access must be checked.

Limitations: schemas validate shape, not consent, isolation, freshness, fencing,
database serializability, identity authentication, or safe external effects.
Git/hash chains are not tamper-proof. Backup anchoring, signed approvals, policy
activation, workload identity, sandboxing and effect adapters remain undeployed.
