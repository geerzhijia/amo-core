# Repository file inventory

The initial foundation has 43 files. The hybrid architecture update creates 23
and modifies 13, for 66 deliverable files in total. The lists below are exhaustive
and non-overlapping. Local virtual environments/caches are not deliverables.
No empty placeholders or operational agents are included.

## Created in the hybrid architecture update (23)

```text
architecture/overview.md
architecture/control-plane.md
architecture/execution-plane.md
architecture/hybrid-runtime.md
architecture/leadership-lease.md
architecture/task-lifecycle.md
architecture/data-consistency.md
architecture/model-gateway.md
architecture/security-boundaries.md
architecture/failure-recovery.md
architecture/decisions/ADR-0001-single-logical-ceo.md
governance/node_permissions.yaml
governance/runtime_permissions.yaml
schemas/agent.schema.json
schemas/node.schema.json
schemas/task.schema.json
schemas/leadership_lease.schema.json
migrations/ceo_handover_protocol.md
migrations/runtime_migration_protocol.md
evaluation/continuity_tests/hybrid_runtime_scenarios.md
evaluation/test_runtime_schemas.py
decisions/records/DEC-0003.json
audit/events/EVT-0002.json
```

## Modified in the hybrid architecture update (13)

```text
README.md
AMO_IDENTITY.md
CHANGELOG.md
FILES.md
requirements-dev.txt
agents/ceo/identity.md
governance/INTEGRITY.md
operations/state.json
migrations/README.md
migrations/CEO_HANDOVER_TEMPLATE.md
tools/validate.py
evaluation/test_continuity.py
integrity/manifest.json
```

## Preserved unchanged (30)

```text
.gitattributes
.gitignore
.github/workflows/validate.yml
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
audit/README.md
audit/schema.json
audit/events/EVT-0001.json
evaluation/support.py
evaluation/test_governance.py
evaluation/test_migration.py
```

The architecture overview distinguishes confirmed selection, specification,
implemented offline tooling, tested shapes, and deferred runtime mechanisms.
The inventory manifest records digests, excluding itself; it is not signed
approval or immutable storage. DEC-0002 and initial governance records are
preserved; DEC-0003/ADR-0001 record the later scoped architectural outcome.
