import tempfile
import unittest
from pathlib import Path

from scripts.repo_task_plan import rank_files


class InspectSymbolBoostTest(unittest.TestCase):
    def test_inspect_symbol_boosts_file(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            a = td_path / "a.py"
            b = td_path / "b.py"
            a.write_text("def load_json(path: Path) -> dict:\n    pass\n")
            b.write_text("def other():\n    pass\n")

            # Provide inspect symbols that should prefer file `a.py`.
            ranked = rank_files(
                [str(b), str(a)], task="example task", inspect_symbols=["def load_json"]
            )
            self.assertEqual(ranked[0], str(a))


if __name__ == "__main__":
    unittest.main()
