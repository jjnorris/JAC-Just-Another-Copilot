import importlib.util
import tempfile
import unittest
from pathlib import Path


spec = importlib.util.spec_from_file_location(
    "repo_task_research", Path(__file__).with_name("repo_task_research.py")
)
assert spec is not None
assert spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class TestRepoTaskResearchImplementationConsiderations(unittest.TestCase):
    def test_planning_focused_self_hosting_brief_synthesizes_task_relevant_consideration(
        self,
    ):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            (repo / "jack").mkdir(parents=True)

            profile = {
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "confidence_level": "medium",
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "detected_runtime_targets": ["Python"],
            }
            plan = {
                "repo_shape": "python_tooling_repo",
                "recommended_first_edit_area": "scripts/repo_task_plan.py",
                "selected_queries": [
                    "Python argparse, subprocess, pathlib, and JSON for tooling scripts"
                ],
                "selected_sources": {
                    "Python argparse, subprocess, pathlib, and JSON for tooling scripts": [
                        "https://docs.python.org/3/library/argparse.html",
                        "https://docs.python.org/3/library/pathlib.html",
                        "https://docs.python.org/3/library/json.html",
                        "https://docs.python.org/3/library/subprocess.html",
                    ]
                },
            }
            task = "Self-host JACK: research considerations focused run for planning single-file edit"
            selected_snippets = [
                {
                    "title": "argparse - Parser for command-line options, arguments and subcommands - Python 3.14.4 documentation",
                    "source_url": "https://docs.python.org/3/library/argparse.html",
                    "chunk_text": "The argparse module makes it easy to write user-friendly command-line interfaces.",
                },
                {
                    "title": "pathlib - Object-oriented filesystem paths - Python 3.14.4 documentation",
                    "source_url": "https://docs.python.org/3/library/pathlib.html",
                    "chunk_text": "Path classes are divided between pure paths and concrete paths.",
                },
                {
                    "title": "json - JSON encoder and decoder - Python 3.14.4 documentation",
                    "source_url": "https://docs.python.org/3/library/json.html",
                    "chunk_text": "This module exposes an API familiar to users of the standard library marshal and pickle modules.",
                },
                {
                    "title": "subprocess - Subprocess management - Python 3.14.4 documentation",
                    "source_url": "https://docs.python.org/3/library/subprocess.html",
                    "chunk_text": "The subprocess module allows you to spawn new processes.",
                },
            ]

            brief = mod.make_brief(
                repo, task, profile, selected_snippets, selected_snippets, [], plan=plan
            )
            considerations = brief["implementation_considerations"]
            generic = "Repository appears Pythonic: prefer virtualenv/venv, pin dependencies, and run unit tests locally before changes."

            self.assertTrue(considerations, considerations)
            self.assertTrue(
                any("scripts/repo_task_plan.py" in item for item in considerations),
                considerations,
            )
            self.assertTrue(
                any(
                    "argparse" in item
                    and "subprocess" in item
                    and "pathlib" in item
                    and "json" in item
                    for item in considerations
                ),
                considerations,
            )
            self.assertNotIn(generic, considerations)


if __name__ == "__main__":
    unittest.main()
