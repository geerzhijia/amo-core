# Model and infrastructure migration protocol

Status: **PROPOSED procedure**. No migration or successor authorization exists.

A migration replaces infrastructure, not AMO. Export plain Markdown, JSON, schemas,
all Git refs, evidence, and integrity anchors; no provider memory is required.

1. Freeze operational changes and identify the outgoing repository commit,
   authority baseline, unresolved work, and backup. Run validation/tests and
   verify independently anchored hashes. Report any gaps before proceeding.
2. Load `AMO_IDENTITY.md`, the founder brief, and the constitution, respecting
   **PROPOSED** versus approved status. Do not invent the ultimate mission.
3. Read the principle registry, every active version document, retired IDs, and
   amendment history. Reconstruct effective meanings from approvals and
   activation records, not file recency or model preference.
4. Read authority, approval policy, agent permissions, enrollment evidence, and
   access restrictions. Verify which versions are actually approved. Treat
   missing identity/approval evidence as a blocker to operational authority.
5. Reconstruct state from decision, amendment, approval, and audit records;
   reconcile `operations/state.json` as a cache. Read significant decisions,
   alternatives, outcomes, lessons, knowledge classifications, and uncertainty.
6. Identify ongoing projects, tasks, budgets, incidents, and unresolved issues.
   At initialization none are known; absence of records is not a broad mandate.
7. Enumerate pending, rejected, approved-but-not-activated, and activated
   amendments. Verify exact proposal digests, human authorization, sequence,
   effective versions, and whether approvals are still valid for the scope.
8. Produce the standard CEO Handover Report, including gaps, conflicts, missing
   evidence, unavailable external sources, and discrepancies. Test understanding
   with concrete authority and continuity scenarios from `evaluation`.
9. Have an authorized human review the successor's understanding, mandate,
   access changes, and acceptance report. Append a migration audit event and
   decision. Only then transfer bounded operational responsibilities.

If models disagree about interpretation, record the disagreement and escalate.
Never silently reinterpret a principle due to new training or default behavior.
Keep the old baseline, exports, handover, and rollback point. Rollback restores
infrastructure/state from verified records; it does not undo approved governance
by erasing history.

This initial foundation is not cleared for operational takeover: the constitution
and policies are draft, mission and approver enrollment remain open, and no
runtime mandate exists. A successor can reconstruct this limitation from files.
