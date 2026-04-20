import importlib.util
import json
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


class TestRepoTaskResearchActionableSynthesis(unittest.TestCase):
    def test_self_hosting_python_tooling_brief_synthesizes_repo_guidance(self):
        with tempfile.TemporaryDirectory() as temp_dir_str:
            repo = Path(temp_dir_str)
            jack_dir = repo / "jack"
            jack_dir.mkdir(parents=True)
            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps({"recommended_first_edit_area": "scripts/profile_to_docs_lookup.py"}, indent=2) + "\n",
                encoding="utf-8",
            )

            profile: dict[str, object] = {
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "confidence_level": "medium",
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "detected_runtime_targets": ["Python"],
            }
            task = "Self-host JACK: single-file edit"
            selected_snippets: list[dict[str, str]] = [
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

            brief = mod.make_brief(repo, task, profile, selected_snippets, selected_snippets, [])
            suggestions = brief["actionable_suggestions"]
            doc_titles = {snippet["title"] for snippet in selected_snippets}

            self.assertFalse(set(suggestions).issubset(doc_titles))
            self.assertIn(
                "Inspect scripts/profile_to_docs_lookup.py for argument parsing and subprocess invocation before editing.",
                suggestions,
            )
            self.assertIn(
                "Check scripts/profile_to_docs_lookup.py for path handling and JSON/file I/O paths for the single-file change.",
                suggestions,
            )


if __name__ == "__main__":
    unittest.main()
