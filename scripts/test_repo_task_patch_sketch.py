import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "repo_task_patch_sketch", Path(__file__).with_name("repo_task_patch_sketch.py")
)
assert spec is not None
assert spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRepoTaskPatchSketch(unittest.TestCase):
    def test_patch_sketch_emits_conservative_summary(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            jack_dir = repo / "jack"
            jack_dir.mkdir(parents=True)

            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps(
                    {
                        "recommended_first_edit_area": "scripts/repo_task_plan.py",
                        "files_to_inspect_first": [
                            "scripts/repo_task_plan.py",
                            "scripts/intake_to_lookup.py",
                        ],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (jack_dir / "repo-task-edit-sketch.json").write_text(
                json.dumps(
                    {
                        "target_file": "scripts/repo_task_plan.py",
                        "target_symbol_or_section": "def rank_files",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
            (jack_dir / "repo-task-change-outline.json").write_text(
                json.dumps(
                    {
                        "target_file": "scripts/repo_task_plan.py",
                        "target_symbol_or_section": "def rank_files",
                        "change_intent": "Tighten def rank_files for the planning-focused path.",
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )

            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                result = mod.main(["--repo-root", str(repo), "--task", "Self-host JACK: patch sketch smoke test"])

            self.assertEqual(result, 0)
            report = json.loads(stdout.getvalue())
            self.assertEqual(report["status"], "ready")
            self.assertEqual(report["target_file"], "scripts/repo_task_plan.py")
            self.assertEqual(report["target_symbol_or_section"], "def rank_files")
            self.assertTrue(report["do_not_auto_apply"])
            self.assertGreaterEqual(len(report["patch_steps"]), 2)
            self.assertTrue(any("repo_task_plan.py" in step for step in report["patch_steps"]))
            self.assertTrue(any("focused planner" in step.lower() for step in report["patch_steps"]))


if __name__ == "__main__":
    unittest.main()
