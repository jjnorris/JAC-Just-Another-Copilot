#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class VerifyValidationReportMethodsAlignmentTests(unittest.TestCase):
    def test_methods_missing_runner_reference_fails_verification(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            jack_dir = temp_dir / "jack"
            jack_dir.mkdir()
            current_task = "current task"
            artifacts = {
                "repo-task-plan.json": {
                    "task": current_task,
                    "recommended_first_edit_area": "scripts/repo_task_plan.py",
                },
                "repo-task-inspect.json": {
                    "task": current_task,
                    "recommended_first_code_edit_area": "scripts/repo_task_plan.py",
                },
                "repo-task-edit-sketch.json": {
                    "task": current_task,
                    "target_file": "scripts/repo_task_plan.py",
                },
                "repo-task-change-outline.json": {
                    "task": current_task,
                    "target_file": "scripts/repo_task_plan.py",
                },
            }
            for name, payload in artifacts.items():
                (jack_dir / name).write_text(json.dumps(payload), encoding="utf-8")

            report: dict[str, object] = {
                "task": current_task,
                "validated": [
                    "profile_repo_stack.py",
                    "profile_to_docs_lookup.py",
                    "repo_task_research.py",
                    "repo_task_plan.py",
                    "repo_task_inspect.py",
                    "repo_task_edit_sketch.py",
                    "repo_task_change_outline.py",
                ],
                "methods": ["ran: demo"],
                "evidence_links": [
                    "jack/repo-task-plan.json",
                    "jack/repo-task-inspect.json",
                    "jack/repo-task-edit-sketch.json",
                    "jack/repo-task-change-outline.json",
                ],
                "verifier_version": "doublecheck v1",
            }
            (jack_dir / "repo-task-validation-report.json").write_text(
                json.dumps(report),
                encoding="utf-8",
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).with_name("verify_validation_report.py")),
                ],
                cwd=temp_dir,
                capture_output=True,
                text=True,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("INVALID METHODS", result.stdout)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
