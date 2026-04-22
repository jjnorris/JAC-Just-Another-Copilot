#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class VerifyValidationReportTaskAlignmentTests(unittest.TestCase):
    def test_mismatched_artifact_task_fails_verification(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            jack_dir = temp_dir / "jack"
            jack_dir.mkdir()
            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps(
                    {
                        "task": "different task",
                        "recommended_first_edit_area": "scripts/repo_task_plan.py",
                    }
                ),
                encoding="utf-8",
            )
            report: dict[str, object] = {
                "task": "current task",
                "validated": ["repo_task_plan.py"],
                "methods": ["ran: demo"],
                "evidence_links": ["jack/repo-task-plan.json"],
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
            self.assertIn("INVALID EVIDENCE ARTIFACTS", result.stdout)
            self.assertIn("task mismatch", result.stdout)
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
