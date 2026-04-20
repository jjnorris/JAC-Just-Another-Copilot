#!/usr/bin/env python3
"""Repo-task research bridge for JACK."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, cast


DEFAULT_MAX_SNIPPETS = 3
PROFILE_FILENAME = "repo-stack-profile.json"
TASK_PLAN_FILENAME = "repo-task-plan.json"
DOCS_PLAN_FILENAME = "repo-docs-lookup-plan.json"
PROFILE_REPO_STACK_SCRIPT = "profile_repo_stack.py"
DOCS_LOOKUP_SCRIPT = "docs_lookup.py"
REPO_DOCS_EVIDENCE_FILENAME = "repo-docs-evidence.jsonl"
NO_DOCS_EVIDENCE_AFTER_FALLBACK = "No docs evidence available after fallback lookup"
SELF_HOST_PHRASES = ("self-host", "self host", "self-hosting")
PLANNER_FIRST_EDIT_AREA = "scripts/repo_task_plan.py"
NEXT_JS_NAME = "Next.js"
PYTHON_APP_QUESTION = (
    "Repository appears to be a Python application. Is it a library/script or a web application? "
    "If web app, which framework should we assume (Django, FastAPI, Flask, etc.)?"
)
PYTHON_TOOLING_QUESTION = (
    "Repository appears to be a script-heavy tooling repo. Is this intended as CLI/tools code (not a web framework)? "
    "Any preferred packaging or runtime/version to assume?"
)
GENERIC_PYTHON_QUESTION = "Is this repository using Django, FastAPI, Flask, or another Python framework? Please confirm."
PYTHON_VERSION_QUESTION = "Which runtime/version should we target (e.g., Python 3.10, Node 18)?"
PACKAGE_CONFIG_QUESTION = "Are we allowed to modify build/runtime configuration files (package.json, pyproject.toml)?"


def as_sequence(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, dict):
        return list(cast(Iterable[Any], value.values()))
    if isinstance(value, (list, tuple, set)):
        return list(cast(Iterable[Any], value))
    if isinstance(value, (str, bytes)):
        return [value]
    try:
        return list(cast(Iterable[Any], value))
    except TypeError:
        return [value]


def as_str_list(value: Any) -> List[str]:
    return [str(item) for item in as_sequence(value)]


def as_dict(value: Any) -> Dict[str, Any]:
    return cast(Dict[str, Any], value) if isinstance(value, dict) else {}


def extend_unique_strings(target: List[str], values: Any) -> None:
    seen = set(target)
    for item in as_str_list(values):
        if item and item not in seen:
            seen.add(item)
            target.append(item)


def tokenize(text: str) -> List[str]:
    return [token for token in re.findall(r"\w+", text.lower()) if token]


def normalize_profile_sequence(profile: Optional[Dict[str, Any]], key: str) -> List[str]:
    return as_str_list(as_dict(profile).get(key))


def first_matching_item(items: Any, needles: Tuple[str, ...]) -> bool:
    for item in as_str_list(items):
        lowered = item.lower()
        if any(needle in lowered for needle in needles):
            return True
    return False


def snippet_source(snippet: Dict[str, Any]) -> str:
    return str(snippet.get("source_url") or snippet.get("source") or "")


def snippet_query(snippet: Dict[str, Any]) -> str:
    return str(snippet.get("query") or "")


def snippet_text(snippet: Dict[str, Any]) -> str:
    return " ".join(
        [
            str(snippet.get("title") or ""),
            snippet_source(snippet),
            str(snippet.get("chunk_text") or snippet.get("excerpt") or ""),
        ]
    ).lower()


def plan_selected_queries(plan: Optional[Dict[str, Any]]) -> List[str]:
    return as_str_list(as_dict(plan).get("selected_queries"))


def plan_selected_sources(plan: Optional[Dict[str, Any]]) -> List[str]:
    selected_sources = as_dict(plan).get("selected_sources")
    if not isinstance(selected_sources, dict):
        return []

    sources: List[str] = []
    for source_list in cast(Dict[str, Any], selected_sources).values():
        extend_unique_strings(sources, source_list)
    return sources


def plan_query_target(plan: Optional[Dict[str, Any]], query: str) -> str:
    query_rationales = as_dict(plan).get("query_rationales")
    if not isinstance(query_rationales, dict):
        return ""

    rationale = cast(Dict[str, Any], query_rationales).get(query)
    if not isinstance(rationale, dict):
        return ""

    return str(cast(Dict[str, Any], rationale).get("target") or "")


def score_snippet(
    snippet: Dict[str, Any],
    task_tokens: set[str],
    plan_queries: set[str],
    plan_sources: List[str],
    profile_shape: str,
) -> int:
    score = 0
    source = snippet_source(snippet)
    query = snippet_query(snippet)
    text = snippet_text(snippet)

    if source and any(source == prefix or source.startswith(prefix) or prefix.startswith(source) for prefix in plan_sources):
        score += 100
    if query in plan_queries:
        score += 80
    if profile_shape == "python_tooling_repo" and any(token in text for token in ("argparse", "subprocess", "pathlib", "json")):
        score += 10
    score += sum(1 for token in task_tokens if token in text)
    return score


def render_bullet_section(title: str, items: Any) -> List[str]:
    lines = [title]
    bullet_items = as_str_list(items)
    if bullet_items:
        lines.extend([f"- {item}" for item in bullet_items])
    else:
        lines.append("- (none)")
    lines.append("")
    return lines


def render_mapping_section(title: str, mapping: Dict[str, Any]) -> List[str]:
    lines = [title]
    lines.extend([f"- {key}: {value}" for key, value in mapping.items()])
    lines.append("")
    return lines


def render_confidence_notes(notes: Any) -> List[str]:
    note_items = as_str_list(notes)
    if not note_items:
        return []

    lines = ["### Confidence notes"]
    lines.extend([f"- {note}" for note in note_items])
    lines.append("")
    return lines


def render_snippet_block(snippet: Dict[str, Any]) -> List[str]:
    return [
        "---",
        f"### {snippet.get('title') or '(untitled)'}",
        f"Source: {snippet.get('source_url') or '(unknown)'}",
        "",
        (snippet.get("excerpt") or "")[:1200],
        "",
    ]


def render_ambiguity_details(details: Dict[str, Any]) -> List[str]:
    lines = ["## Ambiguity details"]
    for key in ("stack", "task", "evidence"):
        values = as_str_list(details.get(key))
        if values:
            lines.append(f"### {key}")
            lines.extend([f"- {value}" for value in values])
            lines.append("")
    return lines


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_docs_plan(repo: Path) -> Optional[Dict[str, Any]]:
    return load_json(repo / "jack" / DOCS_PLAN_FILENAME)


def load_task_plan(repo: Path) -> Optional[Dict[str, Any]]:
    return load_json(repo / "jack" / TASK_PLAN_FILENAME)


def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    if not path.exists():
        return records

    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                text = line.strip()
                if not text:
                    continue
                try:
                    parsed = json.loads(text)
                except Exception:
                    continue
                if isinstance(parsed, dict):
                    records.append(cast(Dict[str, Any], parsed))
    except Exception:
        return []

    return records


def collect_evidence(repo: Path) -> List[Dict[str, Any]]:
    evidence: List[Dict[str, Any]] = []
    jack_dir = repo / "jack"
    for path in sorted(jack_dir.glob("repo-docs-evidence*.jsonl")):
        evidence.extend(read_jsonl(path))
    return evidence


def summarize_profile(profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not profile:
        return {"summary": "unknown", "signals": {}}

    languages = normalize_profile_sequence(profile, "detected_languages")
    frameworks = normalize_profile_sequence(profile, "detected_frameworks")
    runtimes = normalize_profile_sequence(profile, "detected_runtime_targets")
    package_managers = normalize_profile_sequence(profile, "detected_package_managers")

    parts: List[str] = []
    if languages:
        parts.append(f"languages: {', '.join(languages)}")
    if frameworks:
        parts.append(f"frameworks: {', '.join(frameworks)}")
    if runtimes:
        parts.append(f"runtimes: {', '.join(runtimes)}")
    if not parts:
        parts.append("unknown")

    return {
        "summary": "; ".join(parts),
        "signals": {
            "detected_frameworks": frameworks,
            "detected_languages": languages,
            "detected_runtime_targets": runtimes,
            "detected_package_managers": package_managers,
        },
    }


def supplement_profile_with_local_scan(repo: Path, profile: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    base_profile: Dict[str, Any] = dict(profile or {})
    detected_frameworks = normalize_profile_sequence(base_profile, "detected_frameworks")
    detected_languages = normalize_profile_sequence(base_profile, "detected_languages")
    detected_runtime_targets = normalize_profile_sequence(base_profile, "detected_runtime_targets")

    package_json = repo / "package.json"
    package_text = package_json.read_text(encoding="utf-8", errors="ignore").lower() if package_json.exists() else ""

    if (repo / "manage.py").exists():
        extend_unique_strings(detected_frameworks, ["Django"])
        extend_unique_strings(detected_runtime_targets, ["Python"])

    if any((repo / name).exists() for name in ("next.config.js", "next.config.mjs", "next.config.ts")) or NEXT_JS_NAME.lower() in package_text:
        extend_unique_strings(detected_frameworks, [NEXT_JS_NAME])

    if "react" in package_text:
        extend_unique_strings(detected_frameworks, ["React"])

    if any((repo / name).exists() for name in ("pyproject.toml", "requirements.txt", "setup.py")):
        extend_unique_strings(detected_languages, ["py"])

    if detected_frameworks:
        if "Django" in detected_frameworks:
            base_profile["repo_shape"] = "python_app_repo"
        elif first_matching_item(detected_frameworks, ("next", "react")):
            base_profile["repo_shape"] = "mixed_utility_repo"
        else:
            base_profile.setdefault("repo_shape", "python_tooling_repo")
    else:
        base_profile.setdefault("repo_shape", "python_tooling_repo")

    base_profile["detected_frameworks"] = detected_frameworks
    base_profile["detected_languages"] = detected_languages
    base_profile["detected_runtime_targets"] = detected_runtime_targets
    return base_profile


def is_self_hosting_single_file_task(task: str) -> bool:
    lowered = task.lower()
    return any(phrase in lowered for phrase in ("single-file", "single file", "singlefile", "single script"))


def is_planning_focused_self_hosting_task(
    task: str,
    profile: Optional[Dict[str, Any]],
    plan: Optional[Dict[str, Any]] = None,
) -> bool:
    if not profile or profile.get("repo_shape") != "python_tooling_repo":
        return False

    lowered = task.lower()
    if not any(phrase in lowered for phrase in SELF_HOST_PHRASES):
        return False

    if plan and plan.get("recommended_first_edit_area") == PLANNER_FIRST_EDIT_AREA:
        return True

    return any(token in lowered for token in ("planning", "planner", "rank_files", "rank files", "verify rank_files", "canonical implementation"))


def target_label_for_task(
    task: str,
    profile: Optional[Dict[str, Any]],
    plan: Optional[Dict[str, Any]] = None,
) -> str:
    if plan and plan.get("recommended_first_edit_area"):
        return str(plan.get("recommended_first_edit_area"))
    if profile and is_planning_focused_self_hosting_task(task, profile, plan=plan):
        return PLANNER_FIRST_EDIT_AREA
    if profile and profile.get("repo_shape") == "python_tooling_repo" and is_self_hosting_single_file_task(task):
        return "scripts/repo_task_research.py"
    return "scripts/profile_to_docs_lookup.py"


def collect_brief_sources(selected_snippets: List[Dict[str, Any]], plan: Optional[Dict[str, Any]]) -> List[str]:
    sources: List[str] = []
    extend_unique_strings(sources, [snippet_source(snippet) for snippet in selected_snippets])
    extend_unique_strings(sources, plan_selected_sources(plan))
    return sources


def should_upgrade_profile_confidence(profile: Dict[str, Any], confidence: Optional[str]) -> bool:
    if confidence != "low":
        return False

    if str(profile.get("repo_shape") or "") != "python_app_repo":
        return False

    if str(profile.get("repo_shape_confidence") or "").lower() not in ("medium", "high"):
        return False

    return first_matching_item(normalize_profile_sequence(profile, "detected_languages"), ("py",)) or first_matching_item(
        normalize_profile_sequence(profile, "detected_runtime_targets"),
        ("python",),
    )


def confidence_ambiguity_notes(profile: Dict[str, Any]) -> List[str]:
    notes: List[str] = []
    for note in as_str_list(profile.get("confidence_notes")):
        lowered = note.lower()
        if "conflict" in lowered or "ambig" in lowered:
            notes.append(note)
    return notes


def determine_effective_confidence(
    profile: Optional[Dict[str, Any]],
    ambiguities: Dict[str, List[str]],
) -> Optional[str]:
    if not profile:
        return None

    confidence = str(profile.get("confidence_level") or "").lower() or None
    if should_upgrade_profile_confidence(profile, confidence):
        confidence = "medium"
        notes = as_str_list(profile.get("confidence_notes"))
        upgrade_note = "Local heuristics: upgraded brief confidence to 'medium' based on repo_shape and detected languages."
        if upgrade_note not in notes:
            notes.append(upgrade_note)
        profile["confidence_notes"] = notes

    if confidence == "low":
        ambiguities["stack"].append("Low profile confidence: few or no authoritative manifests detected.")

    ambiguities["stack"].extend(confidence_ambiguity_notes(profile))

    return confidence


def build_profile_implementation_considerations(profile: Optional[Dict[str, Any]]) -> List[str]:
    if not profile:
        return []

    languages = normalize_profile_sequence(profile, "detected_languages")
    runtimes = normalize_profile_sequence(profile, "detected_runtime_targets")
    frameworks = normalize_profile_sequence(profile, "detected_frameworks")

    considerations: List[str] = []
    if first_matching_item(languages, ("py",)) or first_matching_item(runtimes, ("python",)):
        considerations.append("Repository appears Pythonic: prefer virtualenv/venv, pin dependencies, and run unit tests locally before changes.")
    if first_matching_item(frameworks, ("next", "react")):
        considerations.append("Frontend framework detected: review bundler and SSR/SSG config; keep client/server boundaries explicit.")
    return considerations


def build_evidence_implementation_considerations(selected_snippets: List[Dict[str, Any]]) -> List[str]:
    for snippet in selected_snippets:
        text = snippet_text(snippet)
        if any(token in text for token in ("argparse", "subprocess", "pathlib", "json")):
            return ["Evidence discusses argparse/subprocess/pathlib/json tooling concerns; keep the first edit grounded in those signals."]
    return []


def synthesize_implementation_considerations(
    task: str,
    profile: Optional[Dict[str, Any]],
    selected_snippets: List[Dict[str, Any]],
    plan: Optional[Dict[str, Any]] = None,
) -> List[str]:
    considerations: List[str] = []
    if profile and is_planning_focused_self_hosting_task(task, profile, plan=plan):
        target = target_label_for_task(task, profile, plan)
        considerations.append(
            f"Planning-focused self-hosting path: keep the brief anchored to {target} and the argparse/subprocess/pathlib/json signals already present in the evidence."
        )
    elif profile and profile.get("repo_shape") == "python_tooling_repo" and is_self_hosting_single_file_task(task):
        target = target_label_for_task(task, profile, plan)
        considerations.append(f"Single-file self-hosting path: keep the brief anchored to {target} and the JACK artifacts before editing.")
    else:
        considerations.extend(build_profile_implementation_considerations(profile))

    considerations.extend(build_evidence_implementation_considerations(selected_snippets))
    if not considerations:
        considerations.append("No strong implementation-specific signals found; start by reading README, build files, and top docs sources.")
    return considerations


def synthesize_actionable_suggestions(
    task: str,
    profile: Optional[Dict[str, Any]],
    selected_snippets: List[Dict[str, Any]],
    plan: Optional[Dict[str, Any]] = None,
) -> List[str]:
    target = target_label_for_task(task, profile, plan)
    if profile and is_planning_focused_self_hosting_task(task, profile, plan=plan):
        return [
            f"Inspect {target} for argument parsing and subprocess invocation before editing.",
            f"Check {target} for path handling and JSON/file I/O paths for the single-file change.",
        ]
    if profile and profile.get("repo_shape") == "python_tooling_repo" and is_self_hosting_single_file_task(task):
        return [
            f"Inspect {target} for argument parsing and subprocess invocation before editing.",
            f"Check {target} for path handling and JSON/file I/O paths for the single-file change.",
        ]

    suggestions: List[str] = []
    for snippet in selected_snippets[:2]:
        title = str(snippet.get("title") or "").strip()
        if title:
            suggestions.append(title)
    return suggestions


def pick_top_snippets(
    evidence: List[Dict[str, Any]],
    task: str,
    max_snippets: int,
    plan: Optional[Dict[str, Any]] = None,
    profile: Optional[Dict[str, Any]] = None,
) -> List[Dict[str, Any]]:
    plan_queries = set(plan_selected_queries(plan))
    plan_sources = plan_selected_sources(plan)
    task_tokens = set(tokenize(task))
    profile_shape = str((profile or {}).get("repo_shape") or "")

    plan_aligned = [
        snippet
        for snippet in evidence
        if snippet_query(snippet) in plan_queries
        or any(
            snippet_source(snippet) == prefix or snippet_source(snippet).startswith(prefix) or prefix.startswith(snippet_source(snippet))
            for prefix in plan_sources
        )
    ]
    candidates = plan_aligned or evidence

    ranked: List[Tuple[int, int, Dict[str, Any]]] = [
        (score_snippet(snippet, task_tokens, plan_queries, plan_sources, profile_shape), index, snippet)
        for index, snippet in enumerate(candidates)
    ]
    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [snippet for _score, _index, snippet in ranked[:max_snippets]]


def build_recommended_questions(
    task: str,
    profile: Optional[Dict[str, Any]],
    plan: Optional[Dict[str, Any]] = None,
) -> List[str]:
    if profile and profile.get("repo_shape") == "python_tooling_repo" and (
        is_planning_focused_self_hosting_task(task, profile, plan=plan) or is_self_hosting_single_file_task(task)
    ):
        return []

    if profile and profile.get("repo_shape") == "python_app_repo":
        return [PYTHON_APP_QUESTION]

    if not profile:
        return [GENERIC_PYTHON_QUESTION, PYTHON_VERSION_QUESTION, PACKAGE_CONFIG_QUESTION]

    if profile.get("repo_shape") == "python_tooling_repo":
        return [PYTHON_TOOLING_QUESTION, PYTHON_VERSION_QUESTION, PACKAGE_CONFIG_QUESTION]

    return [GENERIC_PYTHON_QUESTION, PYTHON_VERSION_QUESTION, PACKAGE_CONFIG_QUESTION]


def flatten_ambiguities(ambiguities: Dict[str, List[str]]) -> List[str]:
    flattened: List[str] = []
    for key in ("stack", "task", "evidence"):
        extend_unique_strings(flattened, ambiguities.get(key, []))
    return flattened


def make_brief(
    repo_root: Path,
    task: str,
    profile: Optional[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
    selected_snippets: List[Dict[str, Any]],
    ambiguity_list: List[str],
    plan: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    task_plan = plan or load_task_plan(repo_root)
    profile_summary = summarize_profile(profile)
    sources = collect_brief_sources(selected_snippets, task_plan)

    ambiguities: Dict[str, List[str]] = {"stack": [], "task": [], "evidence": []}
    effective_confidence = determine_effective_confidence(profile, ambiguities)
    if not evidence:
        ambiguities["evidence"].append("No docs evidence available.")
    if ambiguity_list:
        ambiguities["task"].extend(ambiguity_list)

    impl_considerations = synthesize_implementation_considerations(task, profile, selected_snippets, task_plan)
    actionable_suggestions = synthesize_actionable_suggestions(task, profile, selected_snippets, task_plan)
    recommended_questions = build_recommended_questions(task, profile, task_plan)

    if effective_confidence is not None:
        confidence_level = effective_confidence
    elif profile:
        confidence_level = profile.get("confidence_level")
    else:
        confidence_level = "unknown"

    brief: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "repo_stack_summary": {
            "summary": profile_summary.get("summary"),
            "confidence_level": confidence_level,
            "confidence_notes": profile.get("confidence_notes") if profile else [],
        },
        "relevant_stack_signals": profile_summary.get("signals", {}),
        "relevant_docs_sources": sources,
        "relevant_evidence_snippets": [
            {
                "title": snippet.get("title"),
                "source_url": snippet.get("source_url"),
                "excerpt": (snippet.get("chunk_text") or snippet.get("excerpt") or "")[:800],
            }
            for snippet in selected_snippets
        ],
        "actionable_suggestions": actionable_suggestions,
        "implementation_considerations": impl_considerations,
        "ambiguities": flatten_ambiguities(ambiguities),
        "ambiguity_details": ambiguities,
        "recommended_next_questions": recommended_questions,
        "do_not_auto_apply": True,
    }
    return brief


def build_brief_markdown_lines(brief: Dict[str, Any]) -> List[str]:
    repo_stack_summary = as_dict(brief.get("repo_stack_summary"))
    lines: List[str] = ["# Repo Task Brief", "", f"**Task**: {brief.get('task', '(none)')}", "", "## Repo Stack Summary"]
    lines.append(str(repo_stack_summary.get("summary", "(none)")))
    lines.extend(["", f"**Profile confidence**: {repo_stack_summary.get('confidence_level', 'unknown')}", ""])
    lines.extend(render_confidence_notes(repo_stack_summary.get("confidence_notes")))
    lines.extend(render_mapping_section("## Relevant Stack Signals", as_dict(brief.get("relevant_stack_signals"))))
    lines.extend(render_bullet_section("## Selected Docs Sources", brief.get("relevant_docs_sources")))
    lines.append("## Top Evidence Snippets (prioritized)")
    for snippet in brief.get("relevant_evidence_snippets", []):
        lines.extend(render_snippet_block(cast(Dict[str, Any], snippet)))
    lines.extend(render_bullet_section("## Implementation Considerations", brief.get("implementation_considerations")))
    lines.extend(render_bullet_section("## Ambiguities (summary)", brief.get("ambiguities")))
    lines.extend(render_ambiguity_details(as_dict(brief.get("ambiguity_details"))))
    lines.extend(render_bullet_section("## Recommended Next Questions", brief.get("recommended_next_questions")))
    lines.extend(["", "**do_not_auto_apply: true**"])
    return lines


def determine_first_step(repo_root: Path, brief: Dict[str, Any]) -> str:
    default_step = "Read the top evidence sources listed in the brief and validate the repo runtime locally."
    task_text = str(brief.get("task", ""))
    profile_path = repo_root / "jack" / PROFILE_FILENAME
    profile = load_json(profile_path) if profile_path.exists() else None
    task_plan = load_task_plan(repo_root)

    if profile and profile.get("repo_shape") == "python_tooling_repo":
        if is_planning_focused_self_hosting_task(task_text, profile, plan=task_plan):
            return (
                "Inspect JACK artifacts (jack/repo-stack-profile.json, jack/repo-task-brief.json, jack/repo-task-plan.json), "
                "then open scripts/repo_task_plan.py and scripts/intake_to_lookup.py to confirm the planning-first path before editing."
            )
        if is_self_hosting_single_file_task(task_text):
            return (
                "Inspect JACK artifacts (jack/repo-stack-profile.json, jack/repo-task-brief.json), "
                "then open scripts/repo_task_research.py and scripts/profile_repo_stack.py to confirm signals and implement the single-file fix in the appropriate script."
            )

    return default_step


def build_next_steps_lines(repo_root: Path, brief: Dict[str, Any]) -> List[str]:
    lines: List[str] = ["# Next Steps", "", f"1. {determine_first_step(repo_root, brief)}"]
    sources = brief.get("relevant_docs_sources", [])[:2]
    if sources:
        lines.extend(["", "Recommended docs to read first:"])
        lines.extend([f"- {source}" for source in sources])
    lines.extend(["", "Highest-priority ambiguity to resolve before coding:"])
    ambiguities = brief.get("ambiguities", [])
    lines.append(ambiguities[0] if ambiguities else "None identified")
    lines.append("")
    return lines


def write_outputs(repo_root: Path, brief: Dict[str, Any], md_path: Path, json_path: Path, next_steps_path: Path) -> None:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(brief, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text("\n".join(build_brief_markdown_lines(brief)) + "\n", encoding="utf-8")

    next_steps_path.parent.mkdir(parents=True, exist_ok=True)
    next_steps_path.write_text("\n".join(build_next_steps_lines(repo_root, brief)) + "\n", encoding="utf-8")


def run_profile_if_missing(repo: Path) -> bool:
    profile_path = repo / "jack" / PROFILE_FILENAME
    if profile_path.exists():
        return True

    script = repo / "scripts" / PROFILE_REPO_STACK_SCRIPT
    if not script.exists():
        return False

    proc = subprocess.run([sys.executable, str(script), "--repo-root", str(repo)], capture_output=True, text=True)
    return proc.returncode == 0 and profile_path.exists()


def run_docs_lookup(repo_root: Path, query: str, stack: str, out_path: Path) -> bool:
    script = repo_root / "scripts" / DOCS_LOOKUP_SCRIPT
    if not script.exists():
        return False

    args = [sys.executable, str(script), "--query", query, "--out", str(out_path)]
    if stack:
        args.extend(["--stack", stack])
    proc = subprocess.run(args, capture_output=True, text=True)
    return proc.returncode == 0 and out_path.exists()


def should_use_fallback_lookup(evidence: List[Dict[str, Any]], task: str) -> bool:
    if len(evidence) < 3:
        return True

    tokens = tokenize(task)
    if not tokens:
        return False

    for entry in evidence:
        if any(token in snippet_text(entry) for token in tokens):
            return False
    return True


def build_fallback_queries(
    task: str,
    profile: Optional[Dict[str, Any]],
    docs_plan: Optional[Dict[str, Any]],
) -> Tuple[List[str], Dict[str, str]]:
    queries: List[str] = []
    stacks_by_query: Dict[str, str] = {}

    selected_queries = plan_selected_queries(docs_plan)
    if selected_queries:
        for query_text in selected_queries[:2]:
            queries.append(query_text)
            stacks_by_query[query_text] = plan_query_target(docs_plan, query_text)
        return queries, stacks_by_query

    stack = ""
    if profile:
        frameworks = normalize_profile_sequence(profile, "detected_frameworks")
        languages = normalize_profile_sequence(profile, "detected_languages")
        if frameworks:
            framework = frameworks[0]
            mapping = {
                NEXT_JS_NAME: "nextjs",
                "NextJS": "nextjs",
                "React": "react",
                "TypeScript": "typescript",
                "FastAPI": "fastapi",
                "Django": "django",
                "Python": "python",
            }
            stack = mapping.get(framework, "")
        elif first_matching_item(languages, ("py",)):
            stack = "python"

    queries = [task, f"{task} implementation guidance"][:2]
    for query in queries:
        stacks_by_query[query] = stack
    return queries, stacks_by_query


def refresh_evidence_with_fallback(
    repo: Path,
    task: str,
    profile: Optional[Dict[str, Any]],
    docs_plan: Optional[Dict[str, Any]],
    evidence: List[Dict[str, Any]],
) -> Tuple[List[Dict[str, Any]], List[str]]:
    ambiguity: List[str] = []
    if not should_use_fallback_lookup(evidence, task):
        return evidence, ambiguity

    queries, stacks_by_query = build_fallback_queries(task, profile, docs_plan)
    for index, query in enumerate(queries, start=1):
        out_path = repo / "jack" / f"repo-task-fallback-{index}.jsonl"
        stack = stacks_by_query.get(query, "")
        if run_docs_lookup(repo, query, stack, out_path):
            main_evidence = repo / "jack" / REPO_DOCS_EVIDENCE_FILENAME
            main_evidence.parent.mkdir(parents=True, exist_ok=True)
            with main_evidence.open("a", encoding="utf-8") as dst, out_path.open("r", encoding="utf-8") as src:
                for line in src:
                    dst.write(line)
            try:
                out_path.unlink()
            except Exception:
                pass

    evidence = collect_evidence(repo)
    if not evidence:
        ambiguity.append(NO_DOCS_EVIDENCE_AFTER_FALLBACK)
    return evidence, ambiguity


def collect_task_change_inputs(
    repo: Path,
    task: str,
) -> Tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
    profile_path = repo / "jack" / PROFILE_FILENAME
    if not profile_path.exists() and not run_profile_if_missing(repo):
        return None, None, [], ["repo profile missing and profiler failed to run"]

    profile = load_json(profile_path) if profile_path.exists() else None
    profile = supplement_profile_with_local_scan(repo, profile)
    docs_plan = load_docs_plan(repo)
    evidence = collect_evidence(repo)
    evidence, ambiguity = refresh_evidence_with_fallback(repo, task, profile, docs_plan, evidence)
    return profile, docs_plan, evidence, ambiguity


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--task", required=True)
    ap.add_argument("--out-json", default="jack/repo-task-brief.json")
    ap.add_argument("--out-md", default="jack/repo-task-brief.md")
    ap.add_argument("--out-next", default="jack/repo-task-next-steps.md")
    ap.add_argument("--max-snippets", type=int, default=DEFAULT_MAX_SNIPPETS)
    args = ap.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    profile, docs_plan, evidence, ambiguity = collect_task_change_inputs(repo, args.task)

    if profile is None and not evidence and ambiguity:
        brief = make_brief(repo, args.task, None, [], [], ambiguity)
        out_json = (repo / args.out_json).resolve()
        out_md = (repo / args.out_md).resolve()
        out_next = (repo / args.out_next).resolve()
        write_outputs(repo, brief, out_md, out_json, out_next)
        print(f"Wrote ambiguous brief: {out_json}")
        return 2

    selected = pick_top_snippets(evidence, args.task, args.max_snippets, plan=docs_plan, profile=profile) if evidence else []
    if not selected:
        ambiguity.append("No high-relevance evidence snippets found for the task")

    brief = make_brief(repo, args.task, profile, evidence, selected, ambiguity, plan=load_task_plan(repo))

    out_json = (repo / args.out_json).resolve()
    out_md = (repo / args.out_md).resolve()
    out_next = (repo / args.out_next).resolve()
    write_outputs(repo, brief, out_md, out_json, out_next)

    print(f"Wrote task brief: {out_json} and {out_md} and next-steps: {out_next}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
