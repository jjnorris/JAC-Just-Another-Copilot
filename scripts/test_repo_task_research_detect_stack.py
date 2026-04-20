import tempfile
import unittest
from pathlib import Path

import scripts.repo_task_research as rtr


class TestSupplementScan(unittest.TestCase):
    def test_detect_manage_py(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            (repo / "manage.py").write_text("print('manage')", encoding="utf-8")
            profile = {
                "detected_frameworks": [],
                "detected_languages": ["py"],
                "confidence_level": "low",
                "confidence_notes": [],
            }
            newp = rtr.supplement_profile_with_local_scan(repo, profile)
            self.assertIn("Django", newp.get("detected_frameworks", []))


if __name__ == "__main__":
    unittest.main()
