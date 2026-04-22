import unittest
from pathlib import Path
import importlib.util


class TestRankFilesCollapsed(unittest.TestCase):
    def test_rank_files_implementation_collapsed_and_behavior(self):
        repo_root = Path(__file__).resolve().parent
        target = repo_root / "repo_task_plan.py"
        txt = target.read_text(encoding="utf-8")

        # `_rank_files_impl` should no longer exist in the source.
        self.assertNotIn(
            "def _rank_files_impl", txt, "_rank_files_impl should be removed"
        )

        # `def rank_files` must exist as the canonical implementation.
        self.assertIn("def rank_files", txt, "def rank_files must be present")

        # Import the module from file and confirm planner-preference logic still works
        spec = importlib.util.spec_from_file_location("repo_task_plan", str(target))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        profile = {"repo_shape": "python_tooling_repo"}
        task = "Self-host JACK: verify rank_files planner-first guarantee"
        recommended = mod.choose_recommended_first_edit_area(
            task, profile, ["scripts/repo_task_plan.py"]
        )
        self.assertEqual(recommended, "scripts/repo_task_plan.py")


if __name__ == "__main__":
    unittest.main()
