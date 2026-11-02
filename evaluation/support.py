"""Isolated synthetic records: never real approvals or operational authority."""

from copy import deepcopy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from tools.validate import ROOT, digest, validate, write_manifest


class FoundationFixture(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "foundation"
        shutil.copytree(
            ROOT, self.root,
            ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", ".ruff_cache"),
        )

    def read(self, reference):
        return json.loads((self.root / reference).read_text(encoding="utf-8"))

    def put(self, reference, value):
        path = self.root / reference
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8", newline="\n")
        return reference

    def seal(self):
        write_manifest(self.root)

    def check(self):
        validate(self.root)

    def amendment(self, final="activated", *, change_type="revision", original=None):
        """Create a wholly synthetic approved policy and lifecycle in temp storage."""
        authority = self.read("governance/authority_matrix.yaml")
        authority["status"] = "ACTIVE"
        authority["authorized_humans"] = [{
            "id": "synthetic-human",
            "actor_type": "human",
            "scopes": ["amendments", "documents"],
            "valid_from": "2026-11-01T00:00:00Z",
            "valid_until": None,
            "enrollment_evidence": ["governance/founder_brief.md"],
        }]
        self.put("governance/authority_matrix.yaml", authority)
        original = original or self.read("principles/registry.json")["principles"][0]
        proposed = deepcopy(original)
        proposed["version"] = "1.1.0"
        proposed["description"] = "Synthetic reviewed revision; fixture only."
        proposed["document"] = "history/principle_evolution/G-001-v1.1.0.md"
        proposed["source"] = "amendments/records/AM-0001-R001.json"
        if change_type == "retirement":
            proposed["status"] = "retired"
        (self.root / proposed["document"]).write_text(
            "Synthetic proposal only.\n", encoding="utf-8", newline="\n"
        )
        self.put("history/principle_evolution/G-001-v1.1.0.json", proposed)
        proposal = {
            "amendment_id": "AM-0001", "record_number": 1,
            "recorded_at": "2026-11-02T10:00:00Z", "status": "proposed",
            "previous_record": None, "change_type": change_type,
            "original_principle": original, "proposed_principle": proposed,
            "proposed_by": {"id": "synthetic-ceo", "actor_type": "ai"},
            "reason": "Synthetic new circumstance.", "evidence": ["governance/founder_brief.md"],
            "expected_impact": "Exercise review boundaries without real approval.",
            "document_sha256": digest(self.root / proposed["document"]),
            "human_review": None, "effective_at": None, "revisits": None,
        }
        first_ref = self.put("amendments/records/AM-0001-R001.json", proposal)
        approval = {
            "id": "APR-0001", "reviewer": {"id": "synthetic-human", "actor_type": "human"},
            "authority_ref": "governance/authority_matrix.yaml",
            "target": first_ref, "target_sha256": digest(self.root / first_ref),
            "decision": "reject" if final == "rejected" else "approve",
            "reviewed_at": "2026-11-02T11:30:00Z",
            "evidence": ["governance/founder_brief.md"], "reason": None,
        }
        review_ref = self.put("governance/approvals/APR-0001.json", approval)
        statuses = ["proposed", "in_review", "rejected" if final == "rejected" else "approved"]
        if final == "activated":
            statuses.append("activated")
        for number, status in enumerate(statuses[1:], 2):
            record = deepcopy(proposal)
            record.update({
                "record_number": number, "status": status,
                "recorded_at": f"2026-11-02T{number + 9:02}:00:00Z",
                "previous_record": f"amendments/records/AM-0001-R{number - 1:03}.json",
                "human_review": review_ref if number >= 3 else None,
                "effective_at": "2026-11-02T13:00:00Z" if status == "activated" else None,
            })
            self.put(f"amendments/records/AM-0001-R{number:03}.json", record)
        state = self.read("operations/state.json")
        if final == "activated":
            self.put("principles/registry.json", {"principles": [proposed]})
            state["active_principles"] = [] if proposed["status"] == "retired" else ["G-001@1.1.0"]
        else:
            state["pending_amendments"] = ["AM-0001"] if final == "approved" else []
        self.put("operations/state.json", state)
        self.seal()
        return proposal
