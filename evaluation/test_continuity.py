import subprocess

from jsonschema import ValidationError

from support import FoundationFixture
from tools.validate import digest, validate_history


class ContinuityTests(FoundationFixture):
    def test_foundation_reconstructs_confirmed_and_proposed_state(self):
        self.seal()
        self.check()
        self.assertIn("NOT FORMALLY APPROVED",
                      (self.root / "constitution/constitution_v0.1.md").read_text(encoding="utf-8"))
        self.assertEqual(self.read("governance/authority_matrix.yaml")["authorized_humans"], [])

    def test_registry_cannot_erase_confirmed_principle(self):
        self.put("principles/registry.json", {"principles": []})
        with self.assertRaisesRegex(ValueError, "authorized activations"):
            self.check()

    def test_metadata_change_is_not_merely_editorial(self):
        registry = self.read("principles/registry.json")
        registry["principles"][0]["scope"] = "Only changes the CEO chooses to submit."
        self.put("principles/registry.json", registry)
        with self.assertRaisesRegex(ValueError, "differs from historical version"):
            self.check()

    def test_audit_chain_detects_changed_predecessor(self):
        event = self.read("audit/events/EVT-0001.json")
        event.update(id="EVT-0002", recorded_at="2026-11-02T10:00:00Z",
                     event_type="incident", previous_event="audit/events/EVT-0001.json",
                     previous_sha256=digest(self.root / "audit/events/EVT-0001.json"))
        self.put("audit/events/EVT-0002.json", event)
        self.seal()
        self.check()
        original = self.read("audit/events/EVT-0001.json")
        original["details"] = "Rewritten history."
        self.put("audit/events/EVT-0001.json", original)
        with self.assertRaisesRegex(ValueError, "predecessor digest mismatch"):
            self.check()

    def test_genesis_audit_requires_real_timezone_qualified_timestamp(self):
        path = "audit/events/EVT-0001.json"
        event = self.read(path)
        for invalid in ("not-a-date", "2026-11-02T03:31:28", "2026-02-30T03:31:28Z"):
            with self.subTest(timestamp=invalid):
                event["recorded_at"] = invalid
                self.put(path, event)
                with self.assertRaises(ValidationError):
                    self.check()

    def test_manifest_detects_document_tampering(self):
        self.seal()
        with (self.root / "AMO_IDENTITY.md").open("a", encoding="utf-8", newline="\n") as file:
            file.write("\nUnreviewed identity change.\n")
        with self.assertRaisesRegex(ValueError, "Integrity manifest mismatch"):
            self.check()

    def test_history_guard_allows_addition_but_rejects_rewrite_and_delete(self):
        def git(*args):
            return subprocess.check_output(
                ["git", *args], cwd=self.root, text=True, stderr=subprocess.STDOUT
            ).strip()

        def commit():
            git("add", ".")
            git("commit", "-m",
                "Synthetic continuity test\n\n"
                "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>\n"
                "Copilot-Session: 158baa9c-6beb-4c4f-b604-a013249df786")

        git("init", "-b", "main")
        git("config", "user.name", "Synthetic Test")
        git("config", "user.email", "test@example.invalid")
        git("config", "commit.gpgsign", "false")
        commit()
        base = git("rev-parse", "HEAD")
        self.put("decisions/records/DEC-9999.json", {"synthetic": True})
        commit()
        validate_history(self.root, base)
        adr = self.root / "architecture/decisions/ADR-0001-single-logical-ceo.md"
        accepted = adr.read_text(encoding="utf-8")
        adr.write_text(accepted + "\nUnrecorded reinterpretation.\n", encoding="utf-8", newline="\n")
        with self.assertRaisesRegex(ValueError, "Historical rewrite forbidden"):
            validate_history(self.root, base)
        adr.write_text(accepted, encoding="utf-8", newline="\n")
        with (self.root / "constitution/constitution_v0.1.md").open("a", encoding="utf-8", newline="\n") as file:
            file.write("\nRewritten draft.\n")
        commit()
        with self.assertRaisesRegex(ValueError, "Historical rewrite forbidden"):
            validate_history(self.root, base)
        with self.assertRaisesRegex(ValueError, "Historical rewrite forbidden"):
            validate_history(self.root, "0" * 40)
        before_delete = git("rev-parse", "HEAD")
        (self.root / "decisions/records/DEC-0001.json").unlink()
        commit()
        with self.assertRaisesRegex(ValueError, "Historical rewrite forbidden"):
            validate_history(self.root, before_delete)
