# Execution Plane and identity

Status: **SPECIFIED; no agents or nodes deployed**.

Execution nodes run assigned agents, invoke models through the Model Gateway,
call only authorized tools, return results, and report status. They cannot
directly write authoritative governance, registries, approvals, or live state.
Even an authorized controller process on a node uses distinct credentials and
the fenced Control Plane interface.

## Identity separation

| Identity | Example | Lifetime / owner |
| --- | --- | --- |
| Organization | `amo` | Continuous organizational identity |
| Agent | `amo-ceo`, `amo-research-agent-001` | Permanent role/history identity |
| Configuration | `research-config-003`, version 2 | Versioned settings; not agent identity |
| Runtime instance | `run-8a17` | One replaceable process execution |
| Node | `amo-node-local-a` | Independently registered execution environment |
| Task | `task-0042` | Persistent work identity across retries/migration |
| Model | provider key plus model ID/revision | Replaceable compute selection |

A process ID may be diagnostic metadata, never a permanent agent identifier.
Moving an agent preserves its ID, role, permissions, and task/event history;
configuration changes get new versions and authorization rather than an implicit
permission reset.

## Registration and capabilities

Each node has a unique registered ID and LOCAL or CLOUD type. Future supported
types are REMOTE_SERVER, EDGE_DEVICE, and DEDICATED_COMPUTE_NODE. Registration
requires explicit human-admin authorization of a workload identity, permission
ceiling, credential profile, resources, and revocation path.

Expose available model routes, tools, runtime/checkpoint capabilities, resource
limits, security permissions, availability, last observation time, and execution
status. These are claims/observations, not grants; the scheduler intersects them
with verified authorization. Heartbeat freshness affects availability only,
never leadership legitimacy.

Scheduling considers capabilities, budget/cost, latency, privacy/data residency,
security and trust, availability, and capacity. Private local-only data cannot
be sent to a cloud node solely because it is cheaper or available.

## Execution contract

Receive a signed/authenticated scoped assignment, verify task/version/epoch and
allowed tools, execute within resource bounds, checkpoint durable outputs, and
submit a result containing all assignment identities and content digests.
Results are candidates until the current leader validates them transactionally.

On lease uncertainty or disconnection stop launching tools/side effects, cancel
in-flight work where possible, and retain only clearly labeled cache/checkpoints
and queued reports. Do not autonomously retry non-idempotent/uncertain operations.
The interface must reject stale writes even if a buggy node keeps computing.
