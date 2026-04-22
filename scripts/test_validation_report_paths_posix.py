import json
import tempfile
import unittest
from pathlib import Path

from scripts import run_repo_task_flow as rtf


class TestValidationReportPathsPosix(unittest.TestCase):
    def test_validation_report_paths_are_posix(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            jack = repo_root / "jack"
            jack.mkdir(parents=True)

            # Create stub artifacts that should appear in evidence_links
            for name in (
                "repo-task-plan.json",
                "repo-task-inspect.json",
                "repo-task-edit-sketch.json",
                "repo-task-change-outline.json",
            ):
                (jack / name).write_text("{}", encoding="utf-8")

            completed = ["profile_repo_stack.py", "profile_to_docs_lookup.py"]
            vr_path = rtf.write_validation_report(
                repo_root, "posix-check-task", completed
            )

            data = json.loads(vr_path.read_text(encoding="utf-8"))
            # evidence_links should be POSIX relative paths (no backslashes)
            for link in data.get("evidence_links", []):
                self.assertNotIn("\\\\", link)
                self.assertNotIn("\\", link)
                self.assertIn("/", link)

            # methods entry should not contain backslashes
            methods = data.get("methods", [])
            self.assertTrue(methods)
            for m in methods:
                self.assertNotIn("\\\\", m)
                self.assertNotIn("\\", m)
                self.assertIn("/", m)


if __name__ == "__main__":
    unittest.main()
