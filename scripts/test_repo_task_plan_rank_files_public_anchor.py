import unittest
from pathlib import Path
import re


class TestRankFilesSymbol(unittest.TestCase):
    def test_rank_files_is_canonical(self):
        repo_root = Path(__file__).resolve().parent
        target = repo_root / "repo_task_plan.py"
        txt = target.read_text(encoding="utf-8")

        # `def rank_files` must exist as the canonical implementation.
        m_public = re.search(r"^\s*def\s+rank_files\b", txt, flags=re.M)
        # `_rank_files_impl` should no longer exist in the source.
        m_impl = re.search(r"^\s*def\s+_rank_files_impl\b", txt, flags=re.M)

        self.assertIsNotNone(m_public, "def rank_files not found in repo_task_plan.py")
        self.assertIsNone(m_impl, "def _rank_files_impl should have been removed; found in repo_task_plan.py")


if __name__ == "__main__":
    unittest.main()
