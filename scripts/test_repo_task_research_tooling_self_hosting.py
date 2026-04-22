import tempfile
import unittest
from pathlib import Path
import json

import scripts.repo_task_research as rtr


class TestRepoTaskResearchToolingSelfHosting(unittest.TestCase):
    def test_tooling_self_hosting_suppresses_generic_questions_and_updates_next_step(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            # prepare a jack profile indicating python_tooling_repo
            jack_dir = repo / "jack"
            jack_dir.mkdir(parents=True)
            profile = {
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "detected_runtime_targets": ["Python"],
                "confidence_level": "low",
            }
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )

            task = "Self-host JACK: research-quality focused run for single-file edit"
            brief = rtr.make_brief(repo, task, profile, [], [], [])

            # Ensure non-blocking generic questions are not present
            forbidden = [
                "Is this repository using Django, FastAPI, Flask, or another Python framework? Please confirm.",
                "Which runtime/version should we target (e.g., Python 3.10, Node 18)?",
                "Are we allowed to modify build/runtime configuration files (package.json, pyproject.toml)?",
                "Repository appears to be a script-heavy tooling repo. Is this intended as CLI/tools code (not a web framework)? Any preferred packaging or runtime/version to assume?",
            ]
            for q in forbidden:
                self.assertNotIn(q, brief.get("recommended_next_questions", []))

            # write outputs and ensure the next-steps first line is not the old runtime-validation step
            out_json = repo / "jack" / "repo-task-brief.json"
            out_md = repo / "jack" / "repo-task-brief.md"
            out_next = repo / "jack" / "repo-task-next-steps.md"
            rtr.write_outputs(repo, brief, out_md, out_json, out_next)

            self.assertTrue(out_next.exists())
            txt = out_next.read_text(encoding="utf-8")
            self.assertNotIn("validate the repo runtime locally", txt)
            self.assertIn("Inspect JACK artifacts", txt)

    def test_planning_focused_self_hosting_without_plan_file_anchors_to_planner_step(
        self,
    ):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            jack_dir = repo / "jack"
            jack_dir.mkdir(parents=True)
            profile = {
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "detected_runtime_targets": ["Python"],
                "confidence_level": "medium",
            }
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )

            task = "Self-host JACK: verify rank_files canonical implementation"
            snippets = [
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

            brief = rtr.make_brief(repo, task, profile, snippets, snippets, [])

            for q in [
                "Repository appears to be a script-heavy tooling repo. Is this intended as CLI/tools code (not a web framework)? Any preferred packaging or runtime/version to assume?",
                "Which runtime/version should we target (e.g., Python 3.10, Node 18)?",
                "Are we allowed to modify build/runtime configuration files (package.json, pyproject.toml)?",
            ]:
                self.assertNotIn(q, brief.get("recommended_next_questions", []))

            suggestions = brief.get("actionable_suggestions", [])
            self.assertTrue(
                any("scripts/repo_task_plan.py" in s for s in suggestions), suggestions
            )

            out_json = repo / "jack" / "repo-task-brief.json"
            out_md = repo / "jack" / "repo-task-brief.md"
            out_next = repo / "jack" / "repo-task-next-steps.md"
            rtr.write_outputs(repo, brief, out_md, out_json, out_next)

            next_steps = out_next.read_text(encoding="utf-8")
            self.assertNotIn("validate the repo runtime locally", next_steps)
            self.assertIn("scripts/repo_task_plan.py", next_steps)
            self.assertIn("scripts/intake_to_lookup.py", next_steps)

    def test_planning_focused_self_hosting_keeps_brief_anchored_to_planner_target(self):
        with tempfile.TemporaryDirectory() as td:
            repo = Path(td)
            jack_dir = repo / "jack"
            jack_dir.mkdir(parents=True)

            profile = {
                "detected_languages": ["py"],
                "detected_frameworks": [],
                "repo_shape": "python_tooling_repo",
                "repo_shape_confidence": "high",
                "detected_runtime_targets": ["Python"],
                "confidence_level": "medium",
            }
            plan = {
                "recommended_first_edit_area": "scripts/repo_task_plan.py",
            }
            (jack_dir / "repo-stack-profile.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            (jack_dir / "repo-task-plan.json").write_text(
                json.dumps(plan), encoding="utf-8"
            )

            task = "Self-host JACK: verify rank_files canonical implementation"
            snippets = [
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

            brief = rtr.make_brief(
                repo, task, profile, snippets, snippets, [], plan=plan
            )

            forbidden = [
                "Repository appears to be a script-heavy tooling repo. Is this intended as CLI/tools code (not a web framework)? Any preferred packaging or runtime/version to assume?",
                "Which runtime/version should we target (e.g., Python 3.10, Node 18)?",
                "Are we allowed to modify build/runtime configuration files (package.json, pyproject.toml)?",
            ]
            for q in forbidden:
                self.assertNotIn(q, brief.get("recommended_next_questions", []))

            suggestions = brief.get("actionable_suggestions", [])
            self.assertTrue(
                any("scripts/repo_task_plan.py" in s for s in suggestions), suggestions
            )

            out_json = repo / "jack" / "repo-task-brief.json"
            out_md = repo / "jack" / "repo-task-brief.md"
            out_next = repo / "jack" / "repo-task-next-steps.md"
            rtr.write_outputs(repo, brief, out_md, out_json, out_next)

            next_steps = out_next.read_text(encoding="utf-8")
            self.assertNotIn("validate the repo runtime locally", next_steps)
            self.assertIn("scripts/repo_task_plan.py", next_steps)


if __name__ == "__main__":
    unittest.main()
