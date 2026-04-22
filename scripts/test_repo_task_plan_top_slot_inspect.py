import unittest
import tempfile
from pathlib import Path

from scripts.repo_task_plan import rank_files


class TestTopSlotInspect(unittest.TestCase):
    def test_top_slot_is_inspect_when_plan_only_references_inspect(self):
        td = Path(tempfile.mkdtemp())
        scripts_dir = td / "scripts"
        scripts_dir.mkdir()

        # Simulate a planner-like file that only references the inspect artifact
        plan_file = scripts_dir / "repo_task_plan.py"
        plan_file.write_text(
            "INSPECT_ARTIFACT = 'jack/repo-task-inspect.json'\n# reference only\n"
        )

        # Actual inspect implementation file with a real inspect function
        inspect_file = scripts_dir / "repo_task_inspect.py"
        inspect_file.write_text("def run_inspect():\n    pass\n")

        # Generic loader helper
        loader_file = scripts_dir / "intake_to_lookup.py"
        loader_file.write_text("def load_spec(path):\n    pass\n")

        candidates = [str(plan_file), str(inspect_file), str(loader_file)]
        task = "Self-host JACK: inspect-quality focused run for planner alignment"
        ranked = rank_files(candidates, task, inspect_symbols=None)

        self.assertEqual(Path(ranked[0]).name, "repo_task_inspect.py")


if __name__ == "__main__":
    unittest.main()
