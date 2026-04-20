import json
import tempfile
import unittest
from pathlib import Path

import scripts.profile_repo_stack as prs


class TestProfileRepoStackPathsPosix(unittest.TestCase):
    def test_evidence_files_are_posix(self):
        with tempfile.TemporaryDirectory() as td:
            repo_root = Path(td)
            # create a couple of manifest/workflow files to be detected
            (repo_root / "package.json").write_text("{}", encoding="utf-8")
            wf_dir = repo_root / ".github" / "workflows"
            wf_dir.mkdir(parents=True)
            (wf_dir / "validate-jac.yml").write_text("name: test", encoding="utf-8")

            # Run the profiler
            rc = prs.main(["--repo-root", str(repo_root)])
            self.assertEqual(rc, 0)

            out_json = repo_root / "jack" / "repo-stack-profile.json"
            self.assertTrue(out_json.is_file())
            data = json.loads(out_json.read_text(encoding="utf-8"))

            # evidence_files entries should use POSIX separators
            for ef in data.get("evidence_files", []):
                self.assertNotIn("\\\\", ef)
                self.assertNotIn("\\", ef)
                # must contain at least one forward slash for nested paths
                if "/" not in ef:
                    self.assertTrue(ef.startswith("package.json"))


if __name__ == "__main__":
    unittest.main()
