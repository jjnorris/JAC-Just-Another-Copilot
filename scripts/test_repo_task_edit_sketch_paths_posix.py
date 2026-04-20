import json
import tempfile
import unittest
from pathlib import Path

import scripts.repo_task_edit_sketch as rtes


class TestEditSketchPathsPosix(unittest.TestCase):
    def test_target_file_is_posix(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            jack = repo_root / "jack"
            jack.mkdir(parents=True)

            # provide a plan with a Windows-style path to simulate input
            plan = {"recommended_first_edit_area": "scripts\\profile_to_docs_lookup.py"}
            (jack / "repo-task-plan.json").write_text(json.dumps(plan), encoding="utf-8")

            rc = rtes.main(["--repo-root", str(repo_root), "--task", "posix-check"])
            self.assertEqual(rc, 0)

            out = json.loads((jack / "repo-task-edit-sketch.json").read_text(encoding="utf-8"))
            tf = out.get("target_file")
            self.assertIsNotNone(tf)
            self.assertNotIn("\\\\", tf)
            self.assertNotIn("\\", tf)
            self.assertIn("/", tf)


if __name__ == "__main__":
    unittest.main()
