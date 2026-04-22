#!/usr/bin/env python3
from __future__ import annotations

import unittest
from pathlib import Path
import os

from scripts.repo_task_plan import rank_files


class RepoTaskPlanRankTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path.cwd()
        self.workflow_dir = self.root / ".github" / "workflows"
        self.workflow_dir.mkdir(parents=True, exist_ok=True)
        self.scripts_dir = self.root / "scripts"
        self.scripts_dir.mkdir(parents=True, exist_ok=True)
        self.workflow_file = self.workflow_dir / "tmp-validate.yml"
        self.script_file = self.scripts_dir / "tmp_intake.py"
        self.workflow_file.write_text("name: tmp\n", encoding="utf-8")
        self.script_file.write_text(
            "def load_spec(spec_file):\n    return {}\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        try:
            self.workflow_file.unlink()
        except Exception:
            pass
        try:
            self.script_file.unlink()
        except Exception:
            pass

    def test_script_with_load_spec_ranked_before_workflow(self) -> None:
        candidates = [
            str(self.workflow_file.relative_to(self.root)),
            str(self.script_file.relative_to(self.root)),
        ]
        ranked = rank_files(candidates, "improve loader behavior")
        # Expect the script file (with def load_spec) to be ranked first
        self.assertEqual(ranked[0], str(self.script_file.relative_to(self.root)))


if __name__ == "__main__":
    raise SystemExit(unittest.main())
