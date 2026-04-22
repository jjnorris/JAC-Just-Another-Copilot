import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "run_repo_task_flow", Path(__file__).with_name("run_repo_task_flow.py")
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRunRepoTaskFlowCleanup(unittest.TestCase):
    def test_reset_run_artifacts_removes_only_run_scoped_outputs(self):
        temp_dir = Path(tempfile.mkdtemp())
        try:
            jack_dir = temp_dir / "jack"
            jack_dir.mkdir()

            stale_evidence = jack_dir / "repo-docs-evidence.jsonl"
            stale_summary = jack_dir / "repo-task-flow-summary.md"
            stale_validation = jack_dir / "repo-task-validation-report.json"
            unrelated_file = jack_dir / "keep-me.txt"

            stale_evidence.write_text("old evidence\n", encoding="utf-8")
            stale_summary.write_text("old summary\n", encoding="utf-8")
            stale_validation.write_text("old validation\n", encoding="utf-8")
            unrelated_file.write_text("keep\n", encoding="utf-8")

            removed = mod.reset_run_artifacts(temp_dir)

            removed_names = {path.name for path in removed}
            self.assertEqual(
                removed_names,
                {
                    "repo-docs-evidence.jsonl",
                    "repo-task-flow-summary.md",
                    "repo-task-validation-report.json",
                },
            )
            self.assertFalse(stale_evidence.exists())
            self.assertFalse(stale_summary.exists())
            self.assertFalse(stale_validation.exists())
            self.assertTrue(unrelated_file.exists())
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    unittest.main()
