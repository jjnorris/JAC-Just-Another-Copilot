#!/usr/bin/env python3
"""Inspect top target files from repo-task plan and produce a code‑aware brief.

Consumes existing JACK artifacts and generates:
  - jack/repo-task-inspect.json
  - jack/repo-task-inspect.md
  - jack/repo-task-edit-brief.md

Usage:
  python -u scripts/repo_task_inspect.py --repo-root . \
       --task "<task description>"
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def read_limited(path: Path, max_bytes: int = 4096) -> str:
    """Read up to max_bytes from a file, returning decoded text."""
    try:
        with path.open("rb") as f:
            data = f.read(max_bytes)
        return data.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def extract_symbols(text: str) -> List[str]:
    """Very light extraction of function and class names from Python files."""
    symbols: List[str] = []
    for line in text.splitlines():
        m = re.match(r"\s*(def|class)\s+(\w+)", line)
        if m:
            symbols.append(f"{m.group(1)} {m.group(2)}")
    return symbols


def first_matching_symbol(symbols: List[str], terms: List[str]) -> Optional[str]:
    for term in terms:
        for symbol in symbols:
            if term in symbol.lower():
                return symbol
    return None


def choose_primary_symbol(
    symbols: List[str], task: str, rel_path: str
) -> Optional[str]:
    if not symbols:
        return None

    task_lower = task.lower()
    rel_lower = rel_path.lower()
    # Use a broader planning-focused matcher (align with planner detection)
    planning_tokens = [
        "planning",
        "synthesis",
        "planner",
        "planner-first",
        "planner first",
        "planner-first guarantee",
        "planner ranking",
        "planner-ranking",
        "ranking",
        "rank_files",
        "rank files",
        "rank",
        "inspect",
        "single-file",
        "single file",
    ]
    planning_focus = any(tok in task_lower for tok in planning_tokens)

    if planning_focus and rel_lower.endswith("repo_task_plan.py"):
        preferred = first_matching_symbol(
            symbols,
            [
                "rank_files",
                "choose_recommended_first_edit_area",
                "main",
                "collect_candidate_files",
                "load_json",
            ],
        )
        if preferred:
            return preferred

    if planning_focus and rel_lower.endswith("repo_task_edit_sketch.py"):
        preferred = first_matching_symbol(symbols, ["main", "load_json"])
        if preferred:
            return preferred

    return symbols[0]


def append_unique(target: List[str], values: List[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def select_inspected_files(repo_root: Path, plan: Dict[str, Any]) -> List[str]:
    candidate_files = plan.get("likely_target_files", [])[:10]
    recommended = plan.get("recommended_first_edit_area")

    if not recommended:
        return candidate_files[:3]

    rec_path = repo_root / recommended
    if not rec_path.exists():
        return candidate_files[:3]

    inspected_files_list: List[str] = [recommended]
    module_name = Path(recommended).stem
    for rel_path in candidate_files:
        if rel_path == recommended:
            continue
        abs_path = repo_root / rel_path
        txt = read_limited(abs_path)
        if f"import {module_name}" in txt or f"from {module_name}" in txt:
            inspected_files_list.append(rel_path)

    if len(inspected_files_list) == 1 and candidate_files:
        for candidate in candidate_files:
            if candidate != recommended:
                inspected_files_list.append(candidate)
                break

    return inspected_files_list


def collect_inspection_details(
    repo_root: Path, task: str, inspected_files_list: List[str]
) -> tuple[List[str], List[str], List[str]]:
    relevance_reasons: List[str] = []
    key_symbols: List[str] = []
    likely_changes: List[str] = []

    for rel_path in inspected_files_list:
        abs_path = repo_root / rel_path
        content = read_limited(abs_path)
        symbols = extract_symbols(content)
        primary_symbol = choose_primary_symbol(symbols, task, rel_path)

        ordered_symbols: List[str] = []
        if primary_symbol:
            ordered_symbols.append(primary_symbol)
        for symbol in symbols:
            if symbol != primary_symbol:
                ordered_symbols.append(symbol)

        relevance_reasons.append(
            "File name matches task keywords or common config patterns."
        )
        append_unique(key_symbols, ordered_symbols)

        if primary_symbol:
            likely_changes.append(f"Modify or extend {primary_symbol}")
        elif symbols:
            likely_changes.append(f"Modify or extend {symbols[0]}")
        else:
            likely_changes.append("Review top of file for configuration sections.")

    return relevance_reasons, key_symbols, likely_changes


def write_inspection_artifacts(
    jack_dir: Path,
    task: str,
    inspected_files_list: List[str],
    relevance_reasons: List[str],
    key_symbols: List[str],
    likely_changes: List[str],
    brief: Optional[Dict[str, Any]],
) -> None:
    inspection: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": task,
        "inspected_files": inspected_files_list,
        "file_relevance_reasons": relevance_reasons,
        "key_symbols_or_sections": key_symbols,
        "likely_change_areas": likely_changes,
        "change_risks": brief.get("ambiguities") if brief else [],
        "recommended_first_code_edit_area": (
            inspected_files_list[0] if inspected_files_list else None
        ),
        "do_not_auto_apply": True,
    }

    json_path = jack_dir / "repo-task-inspect.json"
    json_path.write_text(
        json.dumps(inspection, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    md_path = jack_dir / "repo-task-inspect.md"
    md_lines = [
        "# Repo Task Inspection",
        f"**Task**: {task}",
        "",
        "## Inspected Files",
    ]
    for inspected_file in inspected_files_list:
        md_lines.append(f"- `{inspected_file}`")
    md_lines.extend(["", "## Relevance Reasons", ""])
    for reason in relevance_reasons:
        md_lines.append(f"- {reason}")
    md_lines.extend(["", "## Key Symbols / Sections", ""])
    for symbol in key_symbols:
        md_lines.append(f"- {symbol}")
    md_lines.extend(["", "## Likely Change Areas", ""])
    for change in likely_changes:
        md_lines.append(f"- {change}")
    md_lines.extend(["", "**do_not_auto_apply: true**"])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    edit_path = jack_dir / "repo-task-edit-brief.md"
    edit_lines = [
        "# First Edit Recommendation",
        (
            f"**File**: `{inspection['recommended_first_code_edit_area']}`"
            if inspection["recommended_first_code_edit_area"]
            else "*No concrete file identified*"
        ),
        "",
        "**Why**: This file was top-ranked by the plan and contains symbols relevant to the task.",
        "",
        "**Section to inspect first**:",
        f"- {key_symbols[0]}" if key_symbols else "- (no obvious symbols)",
        "",
        "**Key risk**:",
        (
            f"- {inspection['change_risks'][0]}"
            if inspection["change_risks"]
            else "- None identified"
        ),
    ]
    edit_path.write_text("\n".join(edit_lines), encoding="utf-8")


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    jack_dir = repo_root / "jack"

    plan = load_json(jack_dir / "repo-task-plan.json")
    brief = load_json(jack_dir / "repo-task-brief.json")
    _ = load_json(jack_dir / "repo-stack-profile.json")

    if not plan:
        print("No repo-task-plan.json found; cannot inspect.")
        return 1

    inspected_files_list = select_inspected_files(repo_root, plan)
    relevance_reasons, key_symbols, likely_changes = collect_inspection_details(
        repo_root, args.task, inspected_files_list
    )
    write_inspection_artifacts(
        jack_dir,
        args.task,
        inspected_files_list,
        relevance_reasons,
        key_symbols,
        likely_changes,
        brief,
    )

    print(f"Wrote inspection JSON: {jack_dir / 'repo-task-inspect.json'}")
    print(f"Wrote inspection markdown: {jack_dir / 'repo-task-inspect.md'}")
    print(f"Wrote edit brief: {jack_dir / 'repo-task-edit-brief.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
