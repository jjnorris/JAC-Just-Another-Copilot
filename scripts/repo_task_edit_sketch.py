#!/usr/bin/env python3
"""Generate a conservative edit sketch for a repo task.

Consumes existing JACK artifacts and produces:
  - jack/repo-task-edit-sketch.json
  - jack/repo-task-edit-sketch.md

The sketch identifies a single primary edit target (file and symbol/section),
explains why it is first, suggests a high‑level change shape, lists constraints
to preserve, and enumerates manual checks before editing.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, cast


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    # Validate the path exists and is a regular file
    try:
        if not path or not path.exists() or not path.is_file():
            return None
    except Exception:
        return None

    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return None

    if not text or not text.strip():
        return None

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse JSON file {path!s}: {exc}. "
            "If this file is YAML, convert it to JSON or add YAML support."
        ) from exc

    if isinstance(parsed, dict):
        return cast(Dict[str, Any], parsed)
    return None


def yaml_dependency_present_in_file(path: Path) -> bool:
    if not path.exists():
        return False

    txt = path.read_text(encoding="utf-8", errors="ignore").lower()
    return "pyyaml" in txt or "ruamel" in txt


def yaml_import_present_in_repo(root: Path, skip_name: str) -> bool:
    for p in root.rglob("*.py"):
        if p.name == skip_name:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "import yaml" in t or "from yaml" in t:
            return True
    return False


def repo_has_yaml_support(root: Path) -> bool:
    # check common dependency files for yaml packages
    try:
        if yaml_dependency_present_in_file(root / "requirements.txt"):
            return True
        if yaml_dependency_present_in_file(root / "pyproject.toml"):
            return True
        # search for simple imports in python files
        if yaml_import_present_in_repo(root, Path(__file__).name):
            return True
    except Exception:
        # be conservative on error and report no YAML support
        return False
    return False


def extract_rank_files_snippet(lines: List[str], symbol_text: str) -> str:
    for i, line in enumerate(lines):
        if symbol_text not in line:
            continue

        start = max(0, i - 1)
        end = min(len(lines), i + 3)
        if "rank_files" in symbol_text.lower():
            body_limit = min(len(lines), i + 40)
            end = body_limit
            for j in range(i + 1, body_limit):
                candidate_line = lines[j]
                if candidate_line.startswith("def ") or candidate_line.startswith("class "):
                    end = j
                    break
        return "\n".join(lines[start:end])

    return ""


def normalize_string_list(value: Any) -> List[str]:
    items = cast(List[Any], value or [])
    normalized: List[str] = []
    for item in items:
        text = str(item).strip()
        if text:
            normalized.append(text)
    return normalized


def probe_symbol_in_file(candidate_path: Path, symbol_text: str) -> Optional[str]:
    try:
        txt = candidate_path.read_text(encoding="utf-8")
    except Exception:
        return None

    if symbol_text not in txt:
        return None

    return extract_rank_files_snippet(txt.splitlines(), symbol_text)


def find_primary_target_from_inspect(repo_root: Path, inspect: Optional[Dict[str, Any]]) -> tuple[Optional[str], Optional[str], Dict[str, Any]]:
    primary_file: Optional[str] = None
    primary_symbol: Optional[str] = None
    evidence: Dict[str, Any] = {}

    if inspect:
        symbols = normalize_string_list(inspect.get("key_symbols_or_sections", []))
        inspected_files = normalize_string_list(inspect.get("inspected_files", []))

        for sym in symbols:
            sym_text = sym
            for f in inspected_files:
                candidate_path = repo_root.joinpath(*f.split("\\"))
                snippet = probe_symbol_in_file(candidate_path, sym_text)
                if snippet is not None:
                    primary_file = f
                    primary_symbol = sym_text
                    evidence["file_snippet"] = snippet
                    try:
                        evidence["found_in"] = Path(f).as_posix()
                    except Exception:
                        evidence["found_in"] = f
                    break
            if primary_file:
                break

    return primary_file, primary_symbol, evidence


def describe_primary_target(primary_file: Optional[str], primary_symbol: Optional[str], plan: Optional[Dict[str, Any]]) -> str:
    if not primary_file and plan:
        return "Chosen from plan's recommended_first_edit_area as a fallback."
    elif primary_file and primary_symbol:
        return "Selected because the inspector reported symbol(s) and the first symbol was found inside this inspected file."
    else:
        return "No inspected files or plan hints available; target remains ambiguous."


def resolve_primary_target(repo_root: Path, inspect: Optional[Dict[str, Any]], plan: Optional[Dict[str, Any]]) -> tuple[Optional[str], Optional[str], str, Dict[str, Any]]:
    primary_file, primary_symbol, evidence = find_primary_target_from_inspect(repo_root, inspect)
    if not primary_file and plan:
        primary_file = plan.get("recommended_first_edit_area") or (plan.get("files_to_inspect_first") or [None])[0]

    why = describe_primary_target(primary_file, primary_symbol, plan)

    return primary_file, primary_symbol, why, evidence


def build_suggested_change_shape(primary_file: str, primary_symbol: str, current_snippet: str, repo_root: Path) -> str:
    if "rank_files" in primary_symbol.lower():
        return (
            f"Edit the function `{primary_symbol}` in `{primary_file}` so the planning-focused self-hosting path keeps the right first-edit file at the front.\n\n"
            + "Current implementation (excerpt):\n```\n"
            + current_snippet
            + "\n```\n\n"
            + "Recommended first change intent (human): replace the simple ranking heuristic with a planning-aware selector that:\n"
            + "1) keeps `scripts/repo_task_plan.py` first for the self-hosting planning single-file path;\n"
            + "2) boosts `inspect_symbols` and stage-matching signals over generic helpers;\n"
            + "3) keeps the candidate set bounded and deduplicated while preserving conservative behavior."
        )

    yaml_ok = repo_has_yaml_support(repo_root)
    if yaml_ok:
        fallback_phrase = (
            "2) wraps `json.loads(...)` in a try/except that on JSON decode attempts YAML parsing if available (safe fallback), otherwise raises a clear error explaining accepted formats;\n"
        )
    else:
        fallback_phrase = (
            "2) wraps `json.loads(...)` in a try/except and raises a clear error on decode failure instructing the human to convert YAML to JSON or add YAML support in a follow-up change;\n"
        )

    return (
        f"Edit the function `{primary_symbol}` in `{primary_file}`.\n\n"
        + "Current implementation (excerpt):\n```\n"
        + current_snippet
        + "\n```\n\n"
        + "Recommended first change intent (human): replace the one-line loader with a small, robust loader that:\n"
        + "1) validates that `path` exists and is readable;\n"
        + fallback_phrase
        + "3) asserts the parsed result is a `dict` and returns it; do not auto-fill missing fields — preserve conservative behavior."
    )


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    jack_dir = repo_root / "jack"

    # Load required artifacts (keep for evidence-backed decisions)
    plan = load_json(jack_dir / "repo-task-plan.json")
    inspect = load_json(jack_dir / "repo-task-inspect.json")
    primary_file, primary_symbol, why, evidence = resolve_primary_target(repo_root, inspect, plan)

    # Suggested change shape — produce a concrete, code-facing change intent (no diffs)
    # Use the actual current implementation where possible to make the instruction direct.
    primary_file_posix = Path(primary_file).as_posix() if primary_file else None
    suggested_shape = ""
    if primary_file_posix and primary_symbol and evidence.get("file_snippet"):
        # record the current simple implementation (if present) to refer to in the sketch
        current_snippet = evidence.get("file_snippet", "").strip()
        suggested_shape = build_suggested_change_shape(primary_file_posix, primary_symbol, current_snippet, repo_root)
    else:
        suggested_shape = "Identify a single concrete function or config block to harden; prefer loader functions like `load_spec` if present."

    # Constraints – preserve artifacts' stated constraints and codebase conservatism
    constraints = [
        "Preserve bounded query count (<= 3)",
        "Maintain official-docs preference in evidence handling",
        "Preserve the repository's conservative preference: prefer asking for missing info rather than guessing",
    ]

    # Manual checks before editing — concrete, actionable checks a human should run
    manual_checks: List[str] = []
    if primary_file_posix and primary_symbol:
        manual_checks.append(f"Open `{primary_file_posix}` and confirm the function signature and body for `{primary_symbol}` matches the excerpt below.")
        manual_checks.append(f"Search the repo for callers of `{primary_symbol.split()[-1]}` to assess impact (e.g., `git grep \"{primary_symbol.split()[-1]}\"`).")
    if plan:
        manual_checks.append("Confirm plan's recommended_first_edit_area is still valid: see `repo-task-plan.json`.")
    manual_checks.append("Keep `do_not_auto_apply` true and avoid introducing new runners or orchestration changes in this edit.")

    # Ambiguities
    ambiguities: List[str] = []
    if not primary_file:
        ambiguities.append("Unable to pinpoint a concrete file/symbol pairing from the inspector; human judgment required.")

    primary_file_posix = Path(primary_file).as_posix() if primary_file else None

    sketch: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": args.task,
        "primary_edit_target": primary_file_posix,
        "target_file": primary_file_posix,
        "target_symbol_or_section": primary_symbol,
        "why_this_target_first": why,
        "suggested_change_shape": suggested_shape,
        "first_change_intent": (
            suggested_shape.splitlines()[0] if suggested_shape else ""
        ),
        "constraints_to_preserve": constraints,
        "manual_checks_before_edit": manual_checks,
        "evidence": evidence,
        "ambiguities": ambiguities,
        "do_not_auto_apply": True,
    }

    json_path = jack_dir / "repo-task-edit-sketch.json"
    json_path.write_text(json.dumps(sketch, indent=2, ensure_ascii=False), encoding="utf-8")

    # Markdown version
    md_path = jack_dir / "repo-task-edit-sketch.md"
    md_lines = [
        "# Edit Sketch",
        f"**Task**: {args.task}",
        "",
        "## Primary Edit Target",
        f"- **File**: `{primary_file_posix}`" if primary_file_posix else "- *No concrete file identified*",
        f"- **Symbol/Section**: `{primary_symbol}`" if primary_symbol else "- *No obvious symbol*",
        f"- **Why first**: {why}",
        "",
        "## Suggested Change Shape",
        suggested_shape,
        "",
        "## Constraints to Preserve",
    ]
    for c in constraints:
        md_lines.append(f"- {c}")
    md_lines.extend(["", "## Manual Checks Before Editing", ""])
    for chk in manual_checks:
        md_lines.append(f"- {chk}")
    if ambiguities:
        md_lines.extend(["", "## Ambiguities", ""])
        for a in ambiguities:
            md_lines.append(f"- {a}")
    md_lines.append("\n**do_not_auto_apply: true**")
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"Wrote edit sketch JSON: {json_path}")
    print(f"Wrote edit sketch markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
