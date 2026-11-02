# Foundation file inventory

These are the 43 version-controlled foundation files. Generated virtual
environments and caches are local development artifacts, not deliverables.
No empty placeholder files or operational agents are included.

```text
.gitattributes
.gitignore
.github/workflows/validate.yml
README.md
AMO_IDENTITY.md
CHANGELOG.md
FILES.md
requirements-dev.txt
constitution/constitution_v0.1.md
principles/README.md
principles/G-001-principle-amendment-authority.md
principles/registry.json
principles/schema.json
governance/founder_brief.md
governance/authority_matrix.yaml
governance/approval_policy.yaml
governance/agent_permissions.yaml
governance/approval_schema.json
governance/REVIEW.md
governance/INTEGRITY.md
decisions/README.md
decisions/schema.json
decisions/records/DEC-0001.json
decisions/records/DEC-0002.json
amendments/README.md
amendments/schema.json
history/principle_evolution/G-001-v1.0.0.md
history/principle_evolution/G-001-v1.0.0.json
knowledge/README.md
agents/README.md
agents/ceo/identity.md
operations/state.json
audit/README.md
audit/schema.json
audit/events/EVT-0001.json
migrations/README.md
migrations/CEO_HANDOVER_TEMPLATE.md
integrity/manifest.json
tools/validate.py
evaluation/support.py
evaluation/test_governance.py
evaluation/test_continuity.py
evaluation/test_migration.py
```

The README explains directory deferrals and the architecture tradeoff recorded
as proposed DEC-0002. `integrity/manifest.json` inventories file digests, excluding
itself; it is a consistency baseline, not a signed approval.
