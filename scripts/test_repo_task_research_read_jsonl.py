#!/usr/bin/env python3
from __future__ import annotations

import unittest
import tempfile
import json
from pathlib import Path

from scripts.repo_task_research import read_jsonl


class ReadJsonlTests(unittest.TestCase):
    def test_read_jsonl_valid(self) -> None:
        data = [{"a": 1}, {"b": "x"}]
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "test.jsonl"
            with p.open("w", encoding="utf-8") as fh:
                for obj in data:
                    fh.write(json.dumps(obj) + "\n")

            got = list(read_jsonl(p))
            self.assertEqual(got, data)

    def test_read_jsonl_nonexistent(self) -> None:
        p = Path("this_file_should_not_exist_12345.jsonl")
        if p.exists():
            p.unlink()
        got = list(read_jsonl(p))
        self.assertEqual(got, [])


if __name__ == "__main__":
    raise SystemExit(unittest.main())
