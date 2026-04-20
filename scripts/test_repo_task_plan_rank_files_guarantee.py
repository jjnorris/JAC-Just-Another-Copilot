#!/usr/bin/env python3
import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path


class TestRepoTaskPlanRankFilesGuarantee(unittest.TestCase):
    def test_plan_file_guaranteed_first_for_planning_self_hosting(self):
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

            # planner file
            plan_file = scripts_dir / "repo_task_plan.py"
            plan_file.write_text("# planner\ndef rank_files(candidates, task, inspect_symbols=None):\n    pass\n", encoding="utf-8")
            # helper that matches an inspector symbol
            helper_file = scripts_dir / "helper_loader.py"
            helper_file.write_text("def load_spec(path):\n    pass\n", encoding="utf-8")

            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps({"repo_shape": "python_tooling_repo"}, indent=2), encoding="utf-8"
            )

            candidates = [str(plan_file), str(helper_file), str(plan_file)]
            task = "Self-host JACK: implement rank_files planning fix"

            cwd = Path.cwd()
            try:
                os.chdir(repo)
                ranked = mod.rank_files(candidates, task, inspect_symbols=["def load_spec"])
            finally:
                os.chdir(cwd)

            # planner must be first, deduped, bounded
            self.assertGreater(len(ranked), 0)
            self.assertEqual(Path(ranked[0]).name, "repo_task_plan.py")
            self.assertEqual(len(ranked), len(set(ranked)))
            self.assertTrue(len(ranked) <= 25)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
