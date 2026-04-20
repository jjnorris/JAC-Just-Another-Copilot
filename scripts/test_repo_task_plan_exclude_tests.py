import unittest
from pathlib import Path

from scripts.repo_task_plan import collect_candidate_files


class TestCollectCandidateFilesExcludesTests(unittest.TestCase):
    def test_excludes_test_files(self):
        repo_root = Path(self._create_temp_repo())
        scripts_dir = repo_root / "scripts"
        scripts_dir.mkdir()

        # Create a normal script
        (scripts_dir / "normal.py").write_text("print('hello')")

        # Create test files that should be excluded
        (scripts_dir / "test_helper.py").write_text("print('test')")
        (scripts_dir / "utils_test.py").write_text("print('test2')")

        candidates = collect_candidate_files(repo_root)

        self.assertIn(str(Path("scripts/normal.py")), candidates)
        self.assertNotIn(str(Path("scripts/test_helper.py")), candidates)
        self.assertNotIn(str(Path("scripts/utils_test.py")), candidates)

    def _create_temp_repo(self):
        import tempfile

        td = tempfile.mkdtemp()
        return td


if __name__ == "__main__":
    unittest.main()
