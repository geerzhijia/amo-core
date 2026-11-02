from copy import deepcopy

from jsonschema import ValidationError

from support import FoundationFixture
from tools.validate import validate_registry


class GovernanceTests(FoundationFixture):
    def test_explicit_human_review_then_separate_activation(self):
        self.amendment()
        self.check()

    def test_approval_is_not_activation(self):
        self.amendment(final="approved")
        self.check()
        self.assertEqual(self.read("principles/registry.json")["principles"][0]["version"], "1.0.0")

    def test_rejection_retained_without_invented_reason(self):
        self.amendment(final="rejected")
        self.check()
        self.assertIsNone(self.read("governance/approvals/APR-0001.json")["reason"])

    def test_ai_cannot_self_approve(self):
        self.amendment()
        path = "governance/approvals/APR-0001.json"
        approval = self.read(path)
        approval["reviewer"]["actor_type"] = "ai"
        self.put(path, approval)
        with self.assertRaises(ValidationError):
            self.check()

    def test_missing_or_unenrolled_human_approval_fails(self):
        self.amendment()
        authority = self.read("governance/authority_matrix.yaml")
        authority["authorized_humans"] = []
        self.put("governance/authority_matrix.yaml", authority)
        with self.assertRaisesRegex(ValueError, "not uniquely enrolled"):
            self.check()
        (self.root / "governance/approvals/APR-0001.json").unlink()
        with self.assertRaisesRegex(ValueError, "Missing human review"):
            self.check()

    def test_draft_authority_and_expired_scope_cannot_approve(self):
        self.amendment()
        path = "governance/authority_matrix.yaml"
        authority = self.read(path)
        for mutation, message in (
            (lambda a: a.update(status="PROPOSED"), "Draft authority"),
            (lambda a: a["authorized_humans"][0].update(scopes=[]), "exceeds enrolled scope"),
            (lambda a: a["authorized_humans"][0].update(valid_until="2026-11-02T11:00:00Z"), "expired mandate"),
        ):
            with self.subTest(message=message):
                changed = deepcopy(authority)
                mutation(changed)
                self.put(path, changed)
                with self.assertRaisesRegex(ValueError, message):
                    self.check()

    def test_changed_proposal_invalidates_approval_digest(self):
        self.amendment()
        path = "amendments/records/AM-0001-R001.json"
        proposal = self.read(path)
        proposal["reason"] = "Changed after human review."
        self.put(path, proposal)
        with self.assertRaisesRegex(ValueError, "target digest mismatch"):
            self.check()

    def test_changed_revision_during_lifecycle_fails(self):
        self.amendment()
        path = "amendments/records/AM-0001-R003.json"
        approved = self.read(path)
        approved["expected_impact"] = "A different unreviewed consequence."
        self.put(path, approved)
        with self.assertRaisesRegex(ValueError, "Proposal content changed"):
            self.check()

    def test_skipped_review_and_backdated_activation_fail(self):
        self.amendment()
        path = "amendments/records/AM-0001-R002.json"
        review = self.read(path)
        changed = deepcopy(review)
        changed["status"] = "approved"
        changed["human_review"] = "governance/approvals/APR-0001.json"
        self.put(path, changed)
        with self.assertRaisesRegex(ValueError, "Invalid amendment transition"):
            self.check()
        self.put(path, review)
        path = "amendments/records/AM-0001-R004.json"
        activation = self.read(path)
        activation["effective_at"] = "2026-11-02T09:00:00Z"
        self.put(path, activation)
        with self.assertRaisesRegex(ValueError, "actual implementation time"):
            self.check()

    def test_rejected_proposal_cannot_activate(self):
        self.amendment(final="rejected")
        record = self.read("amendments/records/AM-0001-R003.json")
        record.update(record_number=4, status="activated",
                      previous_record="amendments/records/AM-0001-R003.json",
                      recorded_at="2026-11-02T13:00:00Z", effective_at="2026-11-02T13:00:00Z")
        self.put("amendments/records/AM-0001-R004.json", record)
        with self.assertRaisesRegex(ValueError, "Invalid amendment transition"):
            self.check()

    def test_retirement_keeps_id_and_history(self):
        self.amendment(change_type="retirement")
        self.check()
        self.assertEqual(self.read("principles/registry.json")["principles"][0]["id"], "G-001")
        self.assertTrue((self.root / "history/principle_evolution/G-001-v1.0.0.md").exists())

    def test_retired_id_cannot_be_reused_for_an_addition(self):
        self.amendment(change_type="retirement")
        retirement = self.read("amendments/records/AM-0001-R004.json")
        addition = deepcopy(retirement)
        addition.update(amendment_id="AM-0002", change_type="addition",
                        original_principle=None, effective_at="2026-11-02T14:00:00Z")
        addition["proposed_principle"]["status"] = "active"
        with self.assertRaisesRegex(ValueError, "ID cannot be reused"):
            validate_registry(self.root, [retirement, addition])

    def test_significant_decision_requires_rationale_evidence_and_outcome_fields(self):
        path = "decisions/records/DEC-0002.json"
        decision = self.read(path)
        for field in ("context", "evidence", "alternatives", "authorization", "actual_outcome"):
            with self.subTest(field=field):
                incomplete = deepcopy(decision)
                del incomplete[field]
                self.put(path, incomplete)
                with self.assertRaises(ValidationError):
                    self.check()
