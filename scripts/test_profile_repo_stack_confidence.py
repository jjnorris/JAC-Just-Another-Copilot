import unittest
import tempfile
import shutil
import json
import importlib.util
from pathlib import Path

# Import the target script by path to avoid package import issues when running
# the test directly.
spec = importlib.util.spec_from_file_location(
    "profile_repo_stack", Path(__file__).with_name("profile_repo_stack.py")
)
prs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prs)


class TestProfileRepoStackConfidence(unittest.TestCase):
    def test_tooling_repo_confidence_not_forced_low(self):
        td = Path(tempfile.mkdtemp())
        try:
            # create >20 python scripts to trigger tooling classification
            for i in range(25):
                (td / f"script_{i}.py").write_text("print('hi')\n", encoding="utf-8")

            # run profile on the temporary repo (writes to td/jack/...)
            ret = prs.main(["--repo-root", str(td), "--out-json", "jack/repo-stack-profile.json", "--out-md", "jack/repo-stack-profile.md", "--brief-md", "jack/repo-research-brief.md"])
            self.assertEqual(ret, 0)

            out_path = td / "jack" / "repo-stack-profile.json"
            self.assertTrue(out_path.exists(), msg=f"profile json not written: {out_path}")
            pj = json.loads(out_path.read_text(encoding="utf-8"))

            # assertions per the narrow regression expectation
            self.assertEqual(pj.get("repo_shape"), "python_tooling_repo")
            self.assertEqual(pj.get("repo_shape_confidence"), "high")
            # confidence_level should NOT be forced to 'low' just because manifests absent
            self.assertNotEqual(pj.get("confidence_level"), "low")
        finally:
            shutil.rmtree(td)


if __name__ == '__main__':
    unittest.main()
