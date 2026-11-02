# Decision ledger

Significant records live in `records/DEC-NNNN.json` and follow `schema.json`.
Record recommendations before action, then append outcomes/lessons as a new
`outcome_update` with `supersedes` referencing the earlier decision. Do not edit
the original. Record corrections the same way, explaining the correction.

`human_instruction` records a directly supplied instruction and its provenance;
it is not a reusable approval credential. `ai_recommendation` is never an
authorized decision. `human_approved` and `authorized_actor_decision` need explicit
authorization evidence and a scoped mandate, not just a declared owner.
The validator checks linked approvals; independent human verification is still
required. Other-actor mandates are not available at initialization.

DEC-0001 records confirmed instructions. DEC-0002 is a **PROPOSED** architecture
recommendation, not an approved organizational mandate. Unknown actual outcomes
are `null`, not fictional success.
