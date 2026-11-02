# Governance and audit

Append `events/EVT-NNNN.json` records for authorization, approval, rejection,
access changes, agent permissions, model migrations, governance changes, and
significant incidents. Preserve actor, timestamp, event type, details, evidence,
related records, authorization basis, and the previous event's file and SHA-256.
The genesis event has null previous fields. Never edit it to add later outcomes.

The current chain is a consistency check only. Someone able to rewrite every
record can recompute it. Signed approvals and independently anchored append-only
exports are **DEFERRED**; the CEO must never have unilateral write/delete authority
over authoritative audit storage. That permission boundary is a deployment
requirement, not a guarantee of Markdown or Git.

EVT-0001 records initialization, including the absence of constitution approval
or a runtime. It does not claim that proposed governance controls are deployed.
See [integrity and recovery](../governance/INTEGRITY.md).
