#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.intake_to_lookup import load_spec, main


class LoadSpecTests(unittest.TestCase):
    def _write_temp(self, content: str) -> Path:
        tf = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".json", encoding="utf-8"
        )
        try:
            tf.write(content)
        finally:
            tf.close()
        return Path(tf.name)

    def test_valid_json_object_returns_dict(self) -> None:
        p = self._write_temp(json.dumps({"a": 1}))
        try:
            res = load_spec(p)
            self.assertIsInstance(res, dict)
            self.assertEqual(res.get("a"), 1)
        finally:
            try:
                p.unlink()
            except Exception:
                pass

    def test_missing_file_raises_FileNotFoundError(self) -> None:
        tf = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        name = tf.name
        tf.close()
        # remove so it is missing
        os.unlink(name)
        p = Path(name)
        with self.assertRaises(FileNotFoundError):
            load_spec(p)

    def test_invalid_json_raises_ValueError(self) -> None:
        p = self._write_temp("{bad: }")
        try:
            with self.assertRaises(ValueError):
                load_spec(p)
        finally:
            try:
                p.unlink()
            except Exception:
                pass

    def test_non_object_json_raises_TypeError(self) -> None:
        p = self._write_temp(json.dumps([1, 2, 3]))
        try:
            with self.assertRaises(TypeError):
                load_spec(p)
        finally:
            try:
                p.unlink()
            except Exception:
                pass


class PlanRequestsTests(unittest.TestCase):
    def test_plan_only_mode_generates_prioritized_lookup_requests(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            spec_path = temp_path / "spec.json"
            out_path = temp_path / "plan.json"
            spec = {
                "normalized_goal": "build a secure upload service",
                "candidate_stack": "Python",
                "missing_required_details": ["auth", "deployment_target"],
            }
            spec_path.write_text(json.dumps(spec), encoding="utf-8")

            result = main(["--spec-file", str(spec_path), "--out", str(out_path)])
            self.assertEqual(result, 0)

            output = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(output["candidate_stack"], "Python")
            self.assertEqual(output["execution_mode"], "plan_only")
            self.assertEqual(
                output["priority_topics"][:2], ["authentication", "deployment"]
            )
            self.assertTrue(output["recommended_lookup_requests"])
            self.assertEqual(
                output["recommended_lookup_requests"][0]["query"],
                "getting started Python docs",
            )
            self.assertTrue(
                any(
                    req["query"].startswith("authentication Python docs")
                    for req in output["recommended_lookup_requests"]
                )
            )


if __name__ == "__main__":
    raise SystemExit(unittest.main())
