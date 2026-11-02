# Principle amendment ledger

Status: **PROPOSED record format** implementing the confirmed G-001 boundary.
No amendment is pending, approved, rejected, or activated at initialization.

Create `records/AM-NNNN-RNNN.json` snapshots. A proposal receives a permanent
amendment ID and record number 1. Every subsequent state is a new numbered file
with `previous_record`; never overwrite an old snapshot.

Allowed sequence: `proposed -> in_review -> approved -> activated`, or
`proposed -> in_review -> rejected`. Each snapshot records its timestamp.
The approved or rejected snapshot is the **recording** stage; activation is a
later separate snapshot with effective time. Rejection never activates.

Each snapshot carries the same original principle, proposed complete principle
metadata, reason, evidence, impact, proposer, and proposed document digest.
Create the proposed historical document and its matching JSON metadata before
review; their presence does not make them active. A human review record binds
the digest of the **first proposal snapshot**, which includes the document digest,
so both principle text and metadata are covered. No wording may change within
that lifecycle. A revision to the proposal requires a new amendment ID.

Human approval/rejection lives in `governance/approvals/APR-NNNN.json` and follows
`governance/approval_schema.json`. Review evidence, identity, authorization basis,
and timestamp are required; rejection reason may be null if none was supplied.
Do not invent a reason. `effective_at` is null until activation, then records
the actual implementation timestamp, not a fictional or backdated date.

For additions, original principle is null and the ID must never have existed.
Revisions and retirements name the exact current original version and increment
the version. Retirement preserves the ID with retired status and its history.
Any change to G-001 uses the same approval path, never a self-exemption.

Revisit a rejected proposal using a new amendment with `revisits` referencing
the rejected snapshot, explaining genuinely new evidence/circumstances in
`reason` and `evidence`. Keep the rejection intact.

The current validator implements the initial human authority model only.
Changes to that model require human approval under current rules, new versioned
policy records, and explicit tooling updates. Do not circumvent it by editing
the validator, enrollment list, draft policies, or registry.
