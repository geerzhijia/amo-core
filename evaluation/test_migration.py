from pathlib import Path
import shutil
import tempfile

from support import FoundationFixture
from tools.validate import local_path, validate


class MigrationTests(FoundationFixture):
    def test_plain_file_export_validates_without_vendor_memory_or_git(self):
        self.seal()
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "restored"
            shutil.copytree(self.root, destination)
            self.assertFalse((destination / ".git").exists())
            validate(destination)
            state = self.read("operations/state.json")
            self.assertFalse(state["runtime_enabled"])
            self.assertTrue(any("ultimate organizational mission" in item for item in state["unresolved"]))

    def test_missing_evidence_and_stale_pending_summary_block_takeover(self):
        self.amendment(final="approved")
        state = self.read("operations/state.json")
        state["pending_amendments"] = []
        self.put("operations/state.json", state)
        with self.assertRaisesRegex(ValueError, "Stale pending amendment"):
            self.check()
        (self.root / "governance/founder_brief.md").unlink()
        with self.assertRaisesRegex(ValueError, "Missing referenced file"):
            self.check()

    def test_evidence_paths_cannot_escape_repository(self):
        for reference in ("../outside.json", "C:\\outside.json", "/outside.json"):
            with self.subTest(reference=reference):
                with self.assertRaisesRegex(ValueError, "Not a repository-relative path"):
                    local_path(self.root, reference)
