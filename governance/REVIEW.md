# Founder review and approval

Status: **PROPOSED procedure**, constrained by confirmed G-001.

1. Verify the source summary in `founder_brief.md` and DEC-0001. Confirm G-001
   reflects the instruction; corrections must preserve the original record.
2. Review identity, every draft constitution clause, principle metadata, proposed
   policies, architecture decision DEC-0002, schemas, and unresolved state.
   Resolve or explicitly retain mission/legal/business questions.
3. Establish an authorized human identity through an independently verified
   channel. Record the identity, mandate, effective time, and source evidence in
   a new versioned authority document and audit event. The bootstrap enrollment
   itself requires explicit founder evidence, not AI assertion. The empty
   `authorized_humans` list intentionally blocks new approval validation.
4. Propose exact document contents and record their SHA-256 digests. Reviewers
   inspect those exact bytes. Draft policies do not become active merely by
   enrollment. Adopt policies and constitution explicitly through human review,
   an approval record, and a separate activation event; retain draft versions.
   Constitution/policy adoption uses a significant decision plus approval/audit
   records; principle changes additionally use the amendment lifecycle.
5. For principles, append proposal, in-review, approved/rejected, and (only if
   approved) activated snapshots. Approval references the immutable proposal
   digest. Record human evidence separately; check it out of band until signed
   approval verification exists. A schema-valid claim is not proof of consent.
6. Publish the exact approved historical version and update current indexes
   only after activation. Record effective dates, unresolved limits, and audit
   references. A rejected or superseded proposal remains available.
7. Verify CI, manually review the diff and authorization evidence, then merge
   using human-controlled credentials. Anchor the baseline digest externally
   and take a verified backup.

Do not fabricate an approval during initialization. No genuine approval,
signature, enrollment, or constitution adoption is supplied by this repository.
New governance policy versions need explicit adoption and an extension of
validation before they replace the draft singleton files. Do not edit historical
policy snapshots or accept tooling changes as implicit approval.
