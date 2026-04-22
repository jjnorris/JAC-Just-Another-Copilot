import tempfile
import unittest
from pathlib import Path
import json

import scripts.profile_repo_stack as prs


class TestProfileRepoStackToolingShape(unittest.TestCase):
    def test_script_heavy_without_packaging_classified_as_tooling(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            # create 21 python files (script-heavy)
            for i in range(21):
                p = repo / f"script_{i}.py"
                # include __main__ in one file to ensure entrypoint exists
                content = "print('hello')\n"
                if i == 0:
                    content += "if __name__ == '__main__':\n    print('run')\n"
                p.write_text(content, encoding="utf-8")

            # ensure no packaging manifests present
            # run the profiler main to write outputs into repo/jack/
            out_json = "jack/repo-stack-profile.json"
            rc = prs.main(
                [
                    "--repo-root",
                    str(repo),
                    "--out-json",
                    out_json,
                    "--out-md",
                    "jack/repo-stack-profile.md",
                    "--brief-md",
                    "jack/repo-research-brief.md",
                ]
            )
            self.assertEqual(rc, 0)

            data_path = repo / out_json
            self.assertTrue(data_path.exists(), f"Expected profile JSON at {data_path}")
            data = json.loads(data_path.read_text(encoding="utf-8"))
            self.assertEqual(data.get("repo_shape"), "python_tooling_repo")
            self.assertIn(
                "Large number of standalone scripts",
                " ".join(data.get("repo_shape_notes", [])),
            )


if __name__ == "__main__":
    unittest.main()
