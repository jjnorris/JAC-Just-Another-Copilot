#!/usr/bin/env python3
from __future__ import annotations

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


class ValidationReportCheckTests(unittest.TestCase):
    def test_missing_validation_report_fails_check(self) -> None:
        temp_dir = Path(tempfile.mkdtemp())
        try:
            scripts_dir = temp_dir / "scripts"
            scripts_dir.mkdir()
            shutil.copy2(
                Path(__file__).with_name("verify_validation_report.py"),
                scripts_dir / "verify_validation_report.py",
            )
            (temp_dir / "jack").mkdir()

            self.assertFalse(mod.run_validation_report_check(temp_dir))
        finally:
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    raise SystemExit(unittest.main())
