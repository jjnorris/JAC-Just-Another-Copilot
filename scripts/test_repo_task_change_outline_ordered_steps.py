import unittest
import tempfile
import shutil
import json
import importlib.util
from pathlib import Path

# Import the target script by path to avoid package import issues when running
spec = importlib.util.spec_from_file_location(
    "repo_task_change_outline", Path(__file__).with_name("repo_task_change_outline.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestChangeOutlineOrderedSteps(unittest.TestCase):
    def test_ordered_steps_extracted_from_sketch(self):
        td = Path(tempfile.mkdtemp())
        try:
            jack = td / "jack"
            jack.mkdir()
            sketch = {
                "suggested_change_shape": "Edit the function `def load_json`...\n1) validate the file exists;\n2) wrap json.loads in try/except;\n3) assert parsed value is a dict;",
                "target_file": "scripts/repo_task_change_outline.py",
                "target_symbol_or_section": "def load_json",
            }
            (jack / "repo-task-edit-sketch.json").write_text(json.dumps(sketch), encoding="utf-8")

            # invoke the module to generate the outline
            ret = mod.main(["--repo-root", str(td), "--task", "test task"])
            self.assertEqual(ret, 0)

            out = json.loads((jack / "repo-task-change-outline.json").read_text(encoding="utf-8"))
            self.assertIn("ordered_steps", out)
            self.assertIsInstance(out["ordered_steps"], list)
            self.assertGreaterEqual(len(out["ordered_steps"]), 3)
            # basic content checks
            self.assertIn("validate the file exists", out["ordered_steps"][0].lower())
        finally:
            shutil.rmtree(td)

    def test_rank_files_outline_is_structured_and_filters_self_reference(self):
        td = Path(tempfile.mkdtemp())
        try:
            jack = td / "jack"
            jack.mkdir()
            plan = {
                "recommended_first_edit_area": "scripts/repo_task_plan.py",
                "likely_target_files": [
                    "scripts/repo_task_plan.py",
                    "scripts/intake_to_lookup.py",
                    "scripts/verify_validation_report.py",
                    "scripts/run_repo_task_flow.py",
                    "scripts/repo_task_change_outline.py",
                ],
            }
            inspect = {
                "inspected_files": [
                    "scripts/repo_task_plan.py",
                    "scripts/intake_to_lookup.py",
                    "scripts/repo_task_change_outline.py",
                ]
            }
            sketch = {
                "suggested_change_shape": "Edit the function `def rank_files` in `scripts/repo_task_plan.py` so the planning-focused self-hosting path keeps the right first-edit file at the front.",
                "target_file": "scripts/repo_task_plan.py",
                "target_symbol_or_section": "def rank_files",
                "why_this_target_first": "Selected because the inspector reported symbol(s) and the first symbol was found inside this inspected file.",
            }
            (jack / "repo-task-plan.json").write_text(json.dumps(plan), encoding="utf-8")
            (jack / "repo-task-inspect.json").write_text(json.dumps(inspect), encoding="utf-8")
            (jack / "repo-task-edit-sketch.json").write_text(json.dumps(sketch), encoding="utf-8")

            ret = mod.main(["--repo-root", str(td), "--task", "test task"])
            self.assertEqual(ret, 0)

            out = json.loads((jack / "repo-task-change-outline.json").read_text(encoding="utf-8"))
            self.assertEqual(out["target_file"], "scripts/repo_task_plan.py")
            self.assertTrue(out["change_intent"].startswith("Tighten `def rank_files`"))
            self.assertEqual(
                out["change_breakdown"][0],
                "Keep `scripts/repo_task_plan.py` first in the planning-focused candidate order.",
            )
            self.assertTrue(out["ordered_steps"][0].startswith("Preflight:"))
            self.assertEqual(
                out["likely_touch_points"],
                [
                    "scripts/repo_task_plan.py",
                    "scripts/intake_to_lookup.py",
                    "scripts/verify_validation_report.py",
                    "scripts/run_repo_task_flow.py",
                ],
            )
        finally:
            shutil.rmtree(td)


if __name__ == '__main__':
    unittest.main()
