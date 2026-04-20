import tempfile
import unittest
from pathlib import Path

from scripts.repo_task_plan import rank_files


class StagePreferenceTest(unittest.TestCase):
    def test_inspect_stage_prefers_inspect_filename_over_symbol_boost(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            scripts_dir = td_path / "scripts"
            scripts_dir.mkdir()
            plan = scripts_dir / "repo_task_plan.py"
            inspect = scripts_dir / "repo_task_inspect.py"
            # plan file contains a symbol that would normally get a content boost
            plan.write_text("def load_json(path: Path) -> dict:\n    pass\n")
            inspect.write_text("def inspect_quality():\n    pass\n")

            candidates = [str(plan), str(inspect)]
            task = "Self-host JACK: inspect quality for single-file script edit"
            # provide an inspect_symbols list that would boost plan, but stage match should win
            ranked = rank_files(candidates, task, inspect_symbols=["def load_json"])
            # top result should be the inspect file because 'inspect' is in the task
            self.assertTrue(ranked[0].endswith("repo_task_inspect.py"))


if __name__ == "__main__":
    unittest.main()
