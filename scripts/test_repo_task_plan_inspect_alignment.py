import unittest
from pathlib import Path

from scripts.repo_task_plan import rank_files


class TestInspectAlignment(unittest.TestCase):
    def test_inspect_file_ranks_above_loader(self):
        import tempfile

        repo_root = Path(tempfile.mkdtemp())
        scripts_dir = repo_root / "scripts"
        scripts_dir.mkdir()

        inspect_file = scripts_dir / "inspect_helper.py"
        inspect_file.write_text("def inspect_data():\n    pass\n")

        loader_file = scripts_dir / "loader_helper.py"
        loader_file.write_text("def load_spec(path):\n    pass\n")

        candidates = [str(inspect_file), str(loader_file)]
        task = "Self-host JACK: inspect-quality focused run for planner alignment"
        ranked = rank_files(candidates, task, inspect_symbols=None)

        self.assertEqual(Path(ranked[0]).name, "inspect_helper.py")


if __name__ == "__main__":
    unittest.main()
