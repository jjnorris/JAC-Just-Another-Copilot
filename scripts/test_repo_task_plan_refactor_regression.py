#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


class TestRepoTaskPlanRefactorRegression(unittest.TestCase):
    def test_refactor_preserves_planner_behavior(self):
        # Import the workspace implementation of repo_task_plan.py
        spec = importlib.util.spec_from_file_location(
            "repo_task_plan", Path(__file__).with_name("repo_task_plan.py")
        )
        assert spec is not None and spec.loader is not None
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            scripts_dir = repo / "scripts"
            jack_dir = repo / "jack"
            scripts_dir.mkdir(parents=True)
            jack_dir.mkdir(parents=True)

            # Create a planner file and a helper that would normally match
            # an inspector symbol such as 'def load_spec'.
            plan_file = scripts_dir / "repo_task_plan.py"
            plan_file.write_text(
                "# planner file\ndef rank_files(candidates, task, inspect_symbols=None):\n    pass\n",
                encoding="utf-8",
            )
            helper_file = scripts_dir / "helper_loader.py"
            helper_file.write_text(
                "def load_spec(path):\n    pass\n",
                encoding="utf-8",
            )

            # Provide a profile that signals a python tooling repo so the
            # planner-boost path may trigger when task shape matches.
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps({"repo_shape": "python_tooling_repo"}, indent=2),
                encoding="utf-8",
            )

            # Build candidate list with a duplicate entry to verify dedupe.
            candidates = [str(plan_file), str(helper_file), str(plan_file)]
            task = "Self-host JACK: verify rank_files canonical implementation"

            cwd = Path.cwd()
            try:
                os.chdir(repo)
                ranked = mod.rank_files(
                    candidates, task, inspect_symbols=["def load_spec"]
                )
            finally:
                os.chdir(cwd)

            # Assertions: planner file must be first, results deduplicated,
            # and bounded.
            self.assertGreater(len(ranked), 0)
            self.assertEqual(Path(ranked[0]).name, "repo_task_plan.py")
            self.assertEqual(len(ranked), len(set(ranked)))
            self.assertTrue(len(ranked) <= 25)

            # Recommendation selection should still prefer the planner file
            recommended = mod.choose_recommended_first_edit_area(
                task,
                {"repo_shape": "python_tooling_repo"},
                ["scripts/repo_task_plan.py"],
            )
            self.assertEqual(recommended, "scripts/repo_task_plan.py")


if __name__ == "__main__":
    raise SystemExit(unittest.main())
