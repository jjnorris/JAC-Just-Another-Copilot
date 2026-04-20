import unittest
import tempfile
import shutil
import json
import importlib.util
from pathlib import Path

# Import the target script by path to avoid package import issues when running
# the test directly.
spec = importlib.util.spec_from_file_location(
    "repo_task_edit_sketch", Path(__file__).with_name("repo_task_edit_sketch.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestLoadJson(unittest.TestCase):
    def test_load_json_various_cases(self):
        td = Path(tempfile.mkdtemp())
        try:
            # valid JSON file
            valid = td / "valid.json"
            valid.write_text(json.dumps({"x": 1}), encoding="utf-8")
            self.assertEqual(mod.load_json(valid), {"x": 1})

            # missing file -> returns None
            missing = td / "missing.json"
            self.assertIsNone(mod.load_json(missing))

            # invalid JSON -> raises ValueError with helpful message
            bad = td / "bad.json"
            bad.write_text("not: yaml_or_json", encoding="utf-8")
            with self.assertRaises(ValueError):
                mod.load_json(bad)
        finally:
            shutil.rmtree(td)


if __name__ == '__main__':
    unittest.main()
