import unittest
import tempfile
import shutil
import json
import importlib.util
from pathlib import Path

# Import the target script by path to avoid package import issues when running
spec = importlib.util.spec_from_file_location(
    "repo_task_inspect", Path(__file__).with_name("repo_task_inspect.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestInspectFocus(unittest.TestCase):
    def test_inspect_prefers_recommended_and_importers(self):
        td = Path(tempfile.mkdtemp())
        try:
            # create scripts dir and files
            scripts = td / "scripts"
            scripts.mkdir()
            # primary recommended file
            (scripts / "target_module.py").write_text("def load_json(path):\n    pass\n", encoding="utf-8")
            # importer that references target_module
            (scripts / "importer.py").write_text("import target_module\n\n", encoding="utf-8")
            # unrelated file
            (scripts / "unrelated.py").write_text("def foo():\n    pass\n", encoding="utf-8")
            # hook_regression_tests (should be excluded)
            (scripts / "hook_regression_tests.py").write_text("def test_stub():\n    pass\n", encoding="utf-8")

            jack = td / "jack"
            jack.mkdir()
            plan = {
                "likely_target_files": [
                    "scripts/target_module.py",
                    "scripts/importer.py",
                    "scripts/unrelated.py",
                    "scripts/hook_regression_tests.py",
                ],
                "recommended_first_edit_area": "scripts/target_module.py",
            }
            (jack / "repo-task-plan.json").write_text(json.dumps(plan), encoding="utf-8")

            # run inspect
            ret = mod.main(["--repo-root", str(td), "--task", "test inspect"])
            self.assertEqual(ret, 0)

            out_path = jack / "repo-task-inspect.json"
            self.assertTrue(out_path.exists())
            data = json.loads(out_path.read_text(encoding="utf-8"))
            inspected = data.get("inspected_files", [])
            # recommended primary must come first
            self.assertGreaterEqual(len(inspected), 1)
            self.assertEqual(inspected[0], "scripts/target_module.py")
            # importer should be included, unrelated should be excluded
            self.assertIn("scripts/importer.py", inspected)
            self.assertNotIn("scripts/unrelated.py", inspected)
            self.assertNotIn("scripts/hook_regression_tests.py", inspected)
        finally:
            shutil.rmtree(td)


if __name__ == '__main__':
    unittest.main()
