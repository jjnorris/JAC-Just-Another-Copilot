#!/usr/bin/env python3
"""Generate a conservative patch sketch from existing JACK artifacts.

This stage is recommendation-only: it prints a structured JSON sketch to
stdout and does not apply any repository changes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    try:
        parsed = json.loads(text)
    except Exception:
        return None

    if isinstance(parsed, dict):
        return parsed
    return None


def normalize_repo_path(path_text: str) -> str:
    return path_text.replace("\\", "/").strip()


def build_patch_steps(plan: Dict[str, Any], edit_sketch: Dict[str, Any], change_outline: Dict[str, Any]) -> List[str]:
    target_file = (
        change_outline.get("target_file")
        or edit_sketch.get("target_file")
        or plan.get("recommended_first_edit_area")
        or ""
    )
    target_symbol = (
        change_outline.get("target_symbol_or_section")
        or edit_sketch.get("target_symbol_or_section")
        or "<no symbol listed>"
    )

    focus_files: List[str] = []
    first_edit_files = plan.get("files_to_inspect_first")
    if isinstance(first_edit_files, list):
        focus_files = [normalize_repo_path(str(item)) for item in first_edit_files if str(item).strip()]

    if not focus_files and target_file:
        focus_files = [normalize_repo_path(str(target_file))]

    steps = [
        f"Edit {target_file}::{target_symbol} using the planning-first change outline.",
    ]
    if focus_files:
        steps.append(f"Keep the immediate patch scoped to {', '.join(focus_files[:2])}.")
    steps.append("Re-run the focused planner and edit-sketch regressions, then rerun the JACK flow once.")
    return steps


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    jack_dir = repo_root / "jack"

    plan = load_json(jack_dir / "repo-task-plan.json") or {}
    edit_sketch = load_json(jack_dir / "repo-task-edit-sketch.json") or {}
    change_outline = load_json(jack_dir / "repo-task-change-outline.json") or {}

    required_artifacts = {
        "repo-task-plan.json": plan,
        "repo-task-edit-sketch.json": edit_sketch,
        "repo-task-change-outline.json": change_outline,
    }
    missing_artifacts = [name for name, data in required_artifacts.items() if not data]

    target_file = (
        change_outline.get("target_file")
        or edit_sketch.get("target_file")
        or plan.get("recommended_first_edit_area")
    )
    target_symbol = (
        change_outline.get("target_symbol_or_section")
        or edit_sketch.get("target_symbol_or_section")
    )

    report: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": args.task,
        "status": "ready" if not missing_artifacts else "blocked",
        "target_file": target_file,
        "target_symbol_or_section": target_symbol,
        "patch_steps": build_patch_steps(plan, edit_sketch, change_outline) if not missing_artifacts else [],
        "missing_artifacts": missing_artifacts,
        "do_not_auto_apply": True,
    }

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
