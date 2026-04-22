#!/usr/bin/env python3
"""Generate a conservative change outline for a repo task.

Consumes existing JACK artifacts (edit sketch, inspection, plan, brief) and
produces a JSON and markdown description of the first concrete change a human
or coding agent should make.

The outline is intentionally conservative: it never proposes code changes, it
only identifies the primary target file/section, a high‑level change intent,
constraints to preserve, likely touch points, and human acceptance checks.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
import re


PLAN_TARGET_FILE = "scripts/repo_task_plan.py"
OUTLINE_SCRIPT_PATH = "scripts/repo_task_change_outline.py"


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def normalize_repo_path(path_text: str) -> str:
    return path_text.replace("\\", "/").strip()


def synthesize_change_intent(
    edit_sketch: Dict[str, Any],
    plan: Dict[str, Any],
    target_file: Optional[str],
    target_symbol: Optional[str],
) -> str:
    if target_symbol and "rank_files" in target_symbol.lower():
        first_edit_area = (
            plan.get("recommended_first_edit_area") or target_file or PLAN_TARGET_FILE
        )
        return (
            f"Tighten `{target_symbol}` in `{target_file}` so `{first_edit_area}` stays first "
            "for the planning-focused self-hosting path."
        )

    # Prefer the suggested_change_shape from the edit sketch; fall back to a
    # generic description.
    return edit_sketch.get("suggested_change_shape", "refine existing logic")


def synthesize_constraints(edit_sketch: Dict[str, Any]) -> List[str]:
    # Use the constraints list from the edit sketch if present.
    constraints = edit_sketch.get("constraints_to_preserve")
    if isinstance(constraints, list):
        return constraints
    # Fallback generic constraint.
    return ["preserve existing bounded behavior"]


def synthesize_change_breakdown(
    edit_sketch: Dict[str, Any],
    plan: Dict[str, Any],
    target_file: Optional[str],
    target_symbol: Optional[str],
) -> List[str]:
    if target_symbol and "rank_files" in target_symbol.lower():
        first_edit_area = (
            plan.get("recommended_first_edit_area") or target_file or PLAN_TARGET_FILE
        )
        return [
            f"Keep `{first_edit_area}` first in the planning-focused candidate order.",
            "Weight `inspect_symbols` and stage-matching signals above generic helper names.",
            "Keep the candidate set bounded, deduplicated, and conservative.",
        ]

    shape = edit_sketch.get("suggested_change_shape", "") or ""
    numbered = re.findall(r"(?m)^[ \t]*\d+[\)\.\s]*\s*(.+)$", shape)
    if numbered:
        return [s.strip() for s in numbered[:3]]

    fallback_lines = [line.strip() for line in shape.splitlines() if line.strip()]
    if fallback_lines:
        return fallback_lines[:3]

    return ["Refine the existing logic in a conservative way."]


def append_touch_points_from_source(
    source_list: List[Any],
    touch_points: List[str],
    seen: set[str],
    normalized_target: str,
) -> None:
    for item in source_list:
        normalized = normalize_repo_path(str(item))
        if not normalized:
            continue
        if (
            normalized.endswith("repo_task_change_outline.py")
            and normalized != normalized_target
        ):
            continue
        if normalized in seen:
            continue
        touch_points.append(normalized)
        seen.add(normalized)


def synthesize_ordered_steps(
    edit_sketch: Dict[str, Any],
    plan: Dict[str, Any],
    target_file: Optional[str],
    target_symbol: Optional[str],
    acceptance_checks: List[str],
) -> List[str]:
    """Produce a short ordered list of concrete steps for the first edit.

    Prefer extracting numbered items from the edit sketch if present; otherwise
    synthesize a small, actionable sequence (pre-check, implement, verify).
    """
    if target_symbol and "rank_files" in target_symbol.lower():
        first_edit_area = (
            plan.get("recommended_first_edit_area") or target_file or PLAN_TARGET_FILE
        )
        return [
            f"Preflight: confirm `{target_file}` still exposes `{target_symbol}` and that `{first_edit_area}` is the first-edit target.",
            f"Implement: apply the change breakdown so `{first_edit_area}` stays first, `inspect_symbols` and stage-matching signals are weighted higher, and the candidate list stays bounded.",
            f"Validate: rerun the JACK flow and confirm the regenerated outline stays focused on `{first_edit_area}` with no new ambiguities.",
        ]

    shape = edit_sketch.get("suggested_change_shape", "") or ""

    # Extract numbered list items like "1) ..." or "1. ..."
    numbered = re.findall(r"(?m)^[ \t]*\d+[\)\.]\s*(.+)$", shape)
    if numbered:
        return [s.strip() for s in numbered]

    steps: List[str] = []
    if target_file:
        sym = target_symbol or "<no symbol listed>"
        steps.append(
            f"Open `{target_file}` and confirm the target symbol/signature: {sym}."
        )

    # First implementation step: perform the described change intent (concise).
    first_line = (
        shape.splitlines()[0].strip()
        if shape.splitlines()
        else "Implement the described change."
    )
    steps.append(f"Implement change: {first_line}")

    # Verification step: run checks and update artifacts
    verify = "Run the narrow unit test added for this change and re-generate the edit-sketch if ambiguities remain."
    steps.append(verify)

    # Include a final manual acceptance check summary for the human
    if acceptance_checks:
        steps.append(f"Manual checks: {acceptance_checks[0]}")

    return steps


def synthesize_likely_touch_points(
    inspect: Dict[str, Any], plan: Dict[str, Any], target_file: Optional[str]
) -> List[str]:
    normalized_target = normalize_repo_path(target_file) if target_file else ""
    touch_points: List[str] = []
    seen = set()

    source_lists: List[List[Any]] = []
    inspected_files = inspect.get("inspected_files")
    if isinstance(inspected_files, list):
        source_lists.append(inspected_files)

    planned_files = plan.get("likely_target_files")
    if isinstance(planned_files, list):
        source_lists.append(planned_files)

    for source_list in source_lists:
        append_touch_points_from_source(
            source_list, touch_points, seen, normalized_target
        )
    return touch_points


def select_primary_target(
    edit_sketch: Dict[str, Any], inspect: Dict[str, Any]
) -> tuple[Optional[str], Optional[str], List[str]]:
    target_file: Optional[str] = edit_sketch.get("target_file")
    target_symbol: Optional[str] = edit_sketch.get("target_symbol_or_section")
    ambiguities: List[str] = []

    if not target_file:
        inspected = inspect.get("inspected_files")
        if isinstance(inspected, list) and inspected:
            target_file = inspected[0]
        else:
            ambiguities.append("Unable to determine a primary target file.")

    if not target_symbol and "target_symbol_or_section" not in edit_sketch:
        ambiguities.append("No clear target symbol/section identified.")

    return target_file, target_symbol, ambiguities


def build_acceptance_checks(is_rank_files_target: bool) -> List[str]:
    if is_rank_files_target:
        return [
            "Confirm the target artifact is still generated by the pipeline.",
            f"Confirm the outline does not list {OUTLINE_SCRIPT_PATH} as a touch point unless it is the actual target.",
            "Verify the change stays bounded to the planning-focused rank_files path.",
        ]

    return [
        "Confirm the target artifact is still generated by the pipeline.",
        "Verify any ambiguities remain explicit before proceeding.",
    ]


def build_markdown_outline(outline: Dict[str, Any]) -> List[str]:
    target_file = outline.get("target_file")
    target_symbol = outline.get("target_symbol_or_section")
    change_intent = outline.get("change_intent", "")
    change_breakdown = outline.get("change_breakdown", [])
    constraints = outline.get("constraints_to_preserve", [])
    likely_touch_points = outline.get("likely_touch_points", [])
    ordered_steps = outline.get("ordered_steps", [])
    acceptance_checks = outline.get("acceptance_checks_for_human", [])
    ambiguities = outline.get("ambiguities", [])

    lines = [
        "# Change Outline",
        f"**Task**: {outline.get('task', '')}",
        "",
        "## Primary Target",
        (
            f"- **File**: `{target_file}`"
            if target_file
            else "- *No concrete file identified*"
        ),
        (
            f"- **Symbol/Section**: `{target_symbol}`"
            if target_symbol
            else "- *No explicit symbol/section*"
        ),
        f"- **Why first**: {outline.get('why_this_change_first', '')}",
        "",
        "## Change Intent",
        change_intent,
        "",
        "## Change Breakdown",
    ]
    for item in change_breakdown:
        lines.append(f"- {item}")
    lines.extend(["", "## Constraints to Preserve", ""])
    for constraint in constraints:
        lines.append(f"- {constraint}")
    lines.extend(["", "## Likely Touch Points", ""])
    for touch_point in likely_touch_points:
        lines.append(f"- {touch_point}")
    if ordered_steps:
        lines.extend(["", "## Ordered Steps", ""])
        for index, step in enumerate(ordered_steps, start=1):
            lines.append(f"{index}. {step}")
    lines.extend(["", "## Human Acceptance Checks", ""])
    for check in acceptance_checks:
        lines.append(f"- {check}")
    if ambiguities:
        lines.extend(["", "## Ambiguities", ""])
        for ambiguity in ambiguities:
            lines.append(f"- {ambiguity}")
    lines.append("\n**do_not_auto_apply: true**")
    return lines


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    jack_dir = repo_root / "jack"

    # Load required artifacts; missing ones are tolerated but will limit the
    # richness of the outline.
    edit_sketch = load_json(jack_dir / "repo-task-edit-sketch.json") or {}
    inspect = load_json(jack_dir / "repo-task-inspect.json") or {}
    plan = load_json(jack_dir / "repo-task-plan.json") or {}

    target_file, target_symbol, ambiguities = select_primary_target(
        edit_sketch, inspect
    )

    # Change intent synthesis
    change_intent = synthesize_change_intent(
        edit_sketch, plan, target_file, target_symbol
    )

    change_breakdown = synthesize_change_breakdown(
        edit_sketch, plan, target_file, target_symbol
    )

    # Constraints synthesis
    constraints = synthesize_constraints(edit_sketch)

    # Likely touch points – use inspected files list if present.
    likely_touch_points = synthesize_likely_touch_points(inspect, plan, target_file)

    is_rank_files_target = bool(target_symbol and "rank_files" in target_symbol.lower())

    # Human acceptance checks – short list.
    acceptance_checks = build_acceptance_checks(is_rank_files_target)

    # Ordered steps synthesized from the edit sketch to give a concrete
    # short sequence the human can follow (pre-check, implement, verify).
    ordered_steps = synthesize_ordered_steps(
        edit_sketch, plan, target_file, target_symbol, acceptance_checks
    )

    outline: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": args.task,
        "target_file": target_file,
        "target_symbol_or_section": target_symbol,
        "change_intent": change_intent,
        "change_breakdown": change_breakdown,
        "ordered_steps": ordered_steps,
        "why_this_change_first": edit_sketch.get("why_this_target_first", ""),
        "constraints_to_preserve": constraints,
        "likely_touch_points": likely_touch_points,
        "acceptance_checks_for_human": acceptance_checks,
        "ambiguities": ambiguities,
        "do_not_auto_apply": True,
    }

    json_path = jack_dir / "repo-task-change-outline.json"
    json_path.write_text(
        json.dumps(outline, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Markdown version
    md_path = jack_dir / "repo-task-change-outline.md"
    lines = build_markdown_outline(outline)
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote change outline JSON: {json_path}")
    print(f"Wrote change outline markdown: {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
