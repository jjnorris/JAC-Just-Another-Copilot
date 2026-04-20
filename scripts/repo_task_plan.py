#!/usr/bin/env python3
"""Repo-task implementation planner for JACK.

Consumes existing JACK artifacts and produces a concrete, code‑facing
implementation plan.

Outputs:
  - jack/repo-task-plan.json
  - jack/repo-task-plan.md
  - jack/repo-task-first-edit.md

Usage:
  python -u scripts/repo_task_plan.py --repo-root . \
       --task "Improve JACK's repo profiling and docs selection flow for real-world repositories"
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, cast
import re

# ---------------------------------------------------------------------------
# Helper functions to load existing artifacts
# ---------------------------------------------------------------------------


PLANNER_FILENAME = "repo_task_plan.py"


def rank_files(candidates: List[str], task: str, inspect_symbols: Optional[List[str]] = None) -> List[str]:
    """Rank candidate files with small, conservative heuristics.

    Improvements over the prior simple heuristic:
      - Deduplicate candidate paths (preserve first-seen string form).
      - Prefer files that match task tokens, stage keywords, and inspector
        reported symbols.
      - When the repo profile indicates a self-hosting, planning-focused
        run, prefer `scripts/repo_task_plan.py` strongly.
      - Return a bounded top-N list to avoid noisy long recommendations.
    """
    # Tokenize on word characters to avoid accidental substring matches
    tokens: set[str] = _tokenize_task(task)

    # Deduplicate candidate strings while preserving the original string
    # representation (tests expect the same string values back).
    candidates = _dedupe_candidates(candidates)

    # Stage-preference keywords
    stage_keywords = {
        "inspect",
        "edit-sketch",
        "edit",
        "change-outline",
        "change",
        "plan",
        "research",
        "intake",
        "lookup",
        "profile",
        "docs",
    }
    active_stages = [sk for sk in stage_keywords if sk in tokens]

    # Attempt to detect self-hosting planning profiles; this is conservative
    # and only applies when a profile file explicitly signals the repo shape.
    profile = None
    try:
        profile = load_json(Path("jack") / "repo-stack-profile.json")
    except Exception:
        profile = None

    self_hosting_planning = False
    try:
        if profile and is_self_hosting_python_tooling_task(task, profile) and is_planning_focus_task(task):
            self_hosting_planning = True
    except Exception:
        self_hosting_planning = False

    # Normalize inspector symbols to identifier names when possible so symbol
    # matching is robust across variants like 'def load_json', 'load_json()',
    # or 'load_json(path)'. These identifiers are used below for stronger
    # content-based boosts.
    _normalize_inspect_symbols(inspect_symbols)

    scored: List[tuple[int, int, str]] = []
    for f in candidates:
        scored.append(_score_file(f, tokens, active_stages, self_hosting_planning, inspect_symbols, PLANNER_FILENAME))

    # Sort by score desc, prefer planner file for ties, then name
    scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
    # If this is a planning-focused self-hosting run, consider promoting the
    # planner file to the front — but only when its evidence is reasonably
    # close to the top score. This prevents the guarantee from forcibly
    # overriding materially stronger evidence in other files while still
    # preserving planner-first behavior when scores are similar.
    scored = _maybe_promote_planner(scored, PLANNER_FILENAME)

    # Bound the returned list to avoid noisy long outputs
    max_results = min(25, len(scored))
    return [f for _, _, f in scored][:max_results]


def _dedupe_candidates(candidates: List[str]) -> List[str]:
    """Deduplicate candidate paths while preserving first-seen string form."""
    seen_keys: set[str] = set()
    deduped: List[str] = []
    for f in candidates:
        key = os.path.normcase(os.path.normpath(str(f)))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(f)
    return deduped


def _tokenize_task(task: str) -> set[str]:
    return set(re.findall(r"\w+", task.lower()))


def _normalize_inspect_symbols(inspect_symbols: Optional[List[str]]) -> set[str]:
    symbol_ids: set[str] = set()
    if inspect_symbols:
        for sym in inspect_symbols:
            try:
                s = str(sym)
            except Exception:
                continue
            m = re.search(r"\bdef\s+([A-Za-z_]\w*)", s)
            if m:
                symbol_ids.add(m.group(1))
                continue
            m = re.search(r"\bclass\s+([A-Za-z_]\w*)", s)
            if m:
                symbol_ids.add(m.group(1))
                continue
            toks = re.findall(r"\w+", s)
            if toks:
                symbol_ids.add(toks[-1])
    return symbol_ids


def _score_path_features(f: str, tokens: set[str], active_stages: List[str], self_hosting_planning: bool, planner_filename: str) -> tuple[int, int, Optional[Path], str]:
    score = sum(1 for tok in tokens if tok in f.lower())
    if f.endswith((".yml", ".yaml", ".toml", ".txt", ".md")):
        score += 1

    lower_f = f.lower()
    for sk in active_stages:
        if sk in lower_f:
            score += 50

    try:
        p = Path(f)
        fname = p.name
    except Exception:
        p = None
        fname = os.path.basename(f)

    if self_hosting_planning and (fname == planner_filename or planner_filename in fname):
        score += 100

    try:
        prefer = 1 if planner_filename in os.path.basename(f) or planner_filename in str(f) else 0
    except Exception:
        prefer = 0

    return score, prefer, p, fname


def _score_code_tokens(text: str) -> int:
    code_tokens = [
        "def load_spec",
        "load_spec",
        "spec_intake",
        "plan_requests_from_spec",
        "intake",
        "lookup",
        "inspect",
        "edit_sketch",
        "change_outline",
    ]
    return sum(1 for token in code_tokens if token in text)


def _score_active_stage_matches(text: str, text_lower: str, active_stages: List[str]) -> int:
    score = 0
    stage_content_boost = 50
    for sk in active_stages:
        sk_esc = re.escape(sk)
        pattern_def = rf"\bdef\s+\w*{sk_esc}\w*\s*\("
        pattern_class = rf"\bclass\s+\w*{sk_esc}\w*\b"
        pattern_call = rf"\b{sk_esc}\w*\s*\("
        if re.search(pattern_def, text, flags=re.IGNORECASE) or re.search(pattern_class, text, flags=re.IGNORECASE):
            score += stage_content_boost
        elif re.search(pattern_call, text, flags=re.IGNORECASE):
            score += stage_content_boost // 2
        elif sk in text_lower:
            score += stage_content_boost // 6
    return score


def _score_inspect_symbol_matches(text: str, active_stages: List[str], inspect_symbols: Optional[List[str]]) -> int:
    score = 0
    if not inspect_symbols:
        return score

    for sym in inspect_symbols:
        if not sym:
            continue
        sym_lower = sym.lower()
        if active_stages:
            if any(sk in sym_lower for sk in active_stages) and sym in text:
                score += 12
            elif sym in text:
                score += 8
        elif sym in text:
            score += 8
    return score


def _score_stage_matches(text: str, text_lower: str, active_stages: List[str], inspect_symbols: Optional[List[str]]) -> int:
    score = _score_active_stage_matches(text, text_lower, active_stages)
    score += _score_inspect_symbol_matches(text, active_stages, inspect_symbols)
    return score


def _score_content_features(p: Optional[Path], f: str, active_stages: List[str], inspect_symbols: Optional[List[str]]) -> int:
    if p is None:
        return 0

    try:
        if not p.exists():
            p = Path.cwd() / f
        if p.exists() and p.is_file():
            text = p.read_text(encoding="utf-8", errors="ignore")
            text_lower = text.lower()
            return _score_code_tokens(text) + _score_stage_matches(text, text_lower, active_stages, inspect_symbols)
    except Exception:
        return 0
    return 0


def _score_file(f: str, tokens: set[str], active_stages: List[str], self_hosting_planning: bool, inspect_symbols: Optional[List[str]], planner_filename: str) -> tuple[int, int, str]:
    score, prefer, p, _fname = _score_path_features(f, tokens, active_stages, self_hosting_planning, planner_filename)
    score += _score_content_features(p, f, active_stages, inspect_symbols)
    return (score, prefer, f)


def _maybe_promote_planner(scored: List[tuple[int, int, str]], planner_filename: str) -> List[tuple[int, int, str]]:
    try:
        planner_idx = None
        planner_score = None
        for i, (s, _pref, path_str) in enumerate(scored):
            try:
                if planner_filename in os.path.basename(path_str):
                    planner_idx = i
                    planner_score = s
                    break
            except Exception:
                continue
        if planner_idx is not None:
            other_scores = [s for j, (s, _p, _f) in enumerate(scored) if j != planner_idx]
            top_other = max(other_scores) if other_scores else None
            if planner_score is not None:
                raw_planner_score = planner_score - 100
                PROMOTION_THRESHOLD = 5
                if top_other is None or raw_planner_score >= top_other - PROMOTION_THRESHOLD:
                    chosen = scored.pop(planner_idx)
                    scored.insert(0, chosen)
    except Exception:
        pass
    return scored

def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None





def read_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append(json.loads(line))
                except Exception:
                    continue
    except Exception:
        pass
    return records


def collect_candidate_files(repo_root: Path) -> List[str]:
    """Return a small, relevant set of file paths (relative to repo_root).

    Heuristics:
      * Common config / manifest files.
      * Top‑level Python scripts.
      * Files referenced in the repo‑stack‑profile (if any).
    The list is deliberately bounded to avoid full repo crawl.
    """
    candidates: List[str] = []
    common = ["pyproject.toml", "requirements.txt", "setup.cfg", "setup.py", "README.md", "LICENSE"]
    candidates.extend([name for name in common if (repo_root / name).exists()])

    scripts_dir = repo_root / "scripts"
    if scripts_dir.is_dir():
        candidates.extend(
            str(p.relative_to(repo_root))
            for p in scripts_dir.iterdir()
            if p.is_file()
            and p.suffix == ".py"
            and not p.name.startswith("test_")
            and not p.name.endswith("_test.py")
        )

    workflows = repo_root / ".github" / "workflows"
    if workflows.is_dir():
        candidates.extend(str(p.relative_to(repo_root)) for p in workflows.rglob("*.yml"))

    return candidates





def is_self_hosting_python_tooling_task(task: str, profile: Optional[Dict[str, Any]]) -> bool:
    # Conservative detection: require profile signal for python tooling
    # repos, and recognize a variety of self-hosting synonyms. Previously
    # this required an explicit 'single-file' phrase which made the
    # planning-focused branch brittle for equivalent wording variants.
    if not profile or profile.get("repo_shape") != "python_tooling_repo":
        return False
    task_lower = task.lower()
    self_host_phrases = ("self-host", "self host", "self-hosting", "selfhost", "self-hosted", "self hosted")
    return any(p in task_lower for p in self_host_phrases)


def is_planning_focus_task(task: str) -> bool:
    task_lower = task.lower()
    # Recognize a broader set of planning-focused wording variants so
    # equivalent phrasings (e.g. 'planner-first guarantee', 'ranking fix',
    # 'planner ranking', 'rank_files') still trigger the planning path.
    # This matcher remains conservative because it is used together with
    # `is_self_hosting_python_tooling_task` which requires a repo profile
    # signal (self-hosting) before the planning branch activates.
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
    ]
    for tok in planning_tokens:
        if tok in task_lower:
            return True
    return False


def extract_brief_themes(brief: Optional[Dict[str, Any]]) -> List[str]:
    if not brief:
        return []
    suggestions = cast(List[Any], brief.get("actionable_suggestions") or [])
    suggestion_text = " ".join(str(suggestion).lower() for suggestion in suggestions)
    themes: List[str] = []
    if "argument parsing" in suggestion_text or "subprocess" in suggestion_text:
        themes.append("argument parsing and subprocess invocation")
    if (
        "path handling" in suggestion_text
        or "json/file i/o" in suggestion_text
        or "file i/o" in suggestion_text
        or "json" in suggestion_text
    ):
        themes.append("path handling and JSON/file I/O")
    return themes


def choose_recommended_first_edit_area(task: str, profile: Optional[Dict[str, Any]], likely_targets: List[str]) -> Optional[str]:
    if is_self_hosting_python_tooling_task(task, profile) and is_planning_focus_task(task):
        preferred = "scripts/repo_task_plan.py"
        return preferred
    return likely_targets[0] if likely_targets else None


def prioritize_first_edit_area(likely_targets: List[str], first_edit_area: Optional[str]) -> List[str]:
    if not first_edit_area:
        return likely_targets
    reordered: List[str] = []
    seen: set[str] = set()
    for target in [first_edit_area] + likely_targets:
        normalized = Path(target).as_posix()
        if normalized in seen:
            continue
        seen.add(normalized)
        reordered.append(normalized)
    return reordered[:5]


def build_planning_focus_steps(target: str, likely_targets: List[str], brief: Optional[Dict[str, Any]]) -> List[str]:
    themes = extract_brief_themes(brief)
    steps: List[str] = []
    # For the planner file, prefer an explicit symbol-level first-change
    # anchor so downstream edit-sketch generators pick `def rank_files`
    # instead of a generic helper symbol that appears earlier in the file.
    if target and target.endswith("repo_task_plan.py"):
        if themes:
            steps.append(
                f"Modify or extend `def rank_files` in {target} to ensure the planning-focused candidate selection and prioritisation of inspector-reported symbols while keeping the brief anchored to {themes[0]} guidance and the argparse/subprocess/pathlib/json signals already present in the evidence."
            )
        else:
            steps.append(f"Modify or extend `def rank_files` in {target} to ensure the planning-focused candidate selection and prioritisation of inspector-reported symbols.")
    if themes:
        steps.append(
            f"Inspect {target} and rewrite its implementation steps so they explicitly carry the brief's {themes[0]} guidance."
        )
    else:
        steps.append(f"Inspect {target} and rewrite its implementation steps so they carry the brief's synthesized guidance.")

    if len(themes) > 1:
        steps.append(
            f"Use the brief's {themes[1]} guidance to keep the first-edit note concrete instead of saying 'the target script'."
        )
    elif themes:
        steps.append(f"Keep the first-edit note concrete by naming {target} and the brief's evidence themes.")

    if len(likely_targets) > 1:
        steps.append(f"Review {likely_targets[1]} as a handoff check so the plan stays aligned with {target}.")

    steps.append(
        f"Regenerate jack/repo-task-plan.json and jack/repo-task-first-edit.md, then confirm recommended_first_edit_area remains {target}."
    )
    return steps


def build_generic_steps(likely_targets: List[str]) -> List[str]:
    steps: List[str] = []
    if likely_targets:
        steps.append(f"Inspect the file `{likely_targets[0]}` to confirm current configuration.")
        if len(likely_targets) > 1:
            steps.append(f"Review `{likely_targets[1]}` for related settings or entry points.")
        steps.append("Based on the inspection, propose concrete code or config changes.")
    else:
        steps.append("Unable to identify concrete target files; resolve ambiguity first.")
    return steps


def synthesize_implementation_steps(
    task: str,
    profile: Optional[Dict[str, Any]],
    brief: Optional[Dict[str, Any]],
    likely_targets: List[str],
    first_edit_area: Optional[str],
) -> List[str]:
    if is_self_hosting_python_tooling_task(task, profile) and is_planning_focus_task(task):
        target = first_edit_area or (likely_targets[0] if likely_targets else None)
        if target:
            return build_planning_focus_steps(target, likely_targets, brief)

    return build_generic_steps(likely_targets)


def synthesize_first_edit_reason(task: str, profile: Optional[Dict[str, Any]], brief: Optional[Dict[str, Any]], first_edit_area: Optional[str]) -> str:
    if is_self_hosting_python_tooling_task(task, profile) and is_planning_focus_task(task):
        themes = extract_brief_themes(brief)
        if themes:
            return f"This file is the planning stage that should turn the brief's {themes[0]} guidance into concrete file-level steps."
        return "This file is the planning stage that should turn the brief's synthesized guidance into concrete file-level steps."
    if first_edit_area:
        return "This file is most directly related to the task based on its name and repo signals."
    return "No concrete file identified yet."


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--task", required=True)
    args = parser.parse_args(argv)

    repo_root = Path(args.repo_root).resolve()
    jack_dir = repo_root / "jack"

    # Load required artifacts
    profile = load_json(jack_dir / "repo-stack-profile.json")
    # docs_plan and raw evidence are not needed directly for the simple planner;
    # they are consumed indirectly via the task brief.
    brief = load_json(jack_dir / "repo-task-brief.json")

    # Determine candidate files and rank them
    candidates = collect_candidate_files(repo_root)
    # Load inspector symbols if available to prefer files that contain
    # the exact symbols the inspector reported (this improves alignment
    # between planner and edit-sketch outputs).
    inspect_artifact = load_json(jack_dir / "repo-task-inspect.json")
    inspect_symbols: Optional[List[str]] = None
    if isinstance(inspect_artifact, dict):
        inspect_symbols = inspect_artifact.get("key_symbols_or_sections", None)
    ranked = rank_files(candidates, args.task, inspect_symbols)
    planning_focus_self_host = bool(profile) and is_self_hosting_python_tooling_task(args.task, profile) and is_planning_focus_task(args.task)
    # Keep the shortlist bounded. Planning-focused self-hosting tasks only
    # need the first-edit pair; broader tasks keep a slightly wider shortlist.
    likely_target_limit = 2 if planning_focus_self_host else 5
    likely_targets = ranked[:likely_target_limit]
    recommended_first_edit_area = choose_recommended_first_edit_area(args.task, profile, likely_targets)
    likely_targets = prioritize_first_edit_area(likely_targets, recommended_first_edit_area)

    # Build implementation plan structure
    plan: Dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "task": args.task,
        "repo_shape": profile.get("repo_shape") if profile else None,
        "likely_target_files": likely_targets,
        "files_to_inspect_first": likely_targets[:2],
        "implementation_steps": [],
        "risks_and_ambiguities": brief.get("ambiguities") if brief else [],
        "recommended_first_edit_area": recommended_first_edit_area,
        "supporting_evidence": brief.get("relevant_evidence_snippets") if brief else [],
        "do_not_auto_apply": True,
    }

    plan["implementation_steps"] = synthesize_implementation_steps(args.task, profile, brief, likely_targets, recommended_first_edit_area)

    # Write JSON plan
    json_path = jack_dir / "repo-task-plan.json"
    json_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")

    # Write markdown plan
    md_path = jack_dir / "repo-task-plan.md"
    md_lines = [
        "# Repo Task Implementation Plan",
        f"**Task**: {args.task}",
        "",
        "## Likely Target Files",
    ]
    for f in likely_targets:
        md_lines.append(f"- `{f}`")
    md_lines.extend([
        "",
        "## First Files to Inspect",
    ])
    for f in plan["files_to_inspect_first"]:
        md_lines.append(f"- `{f}`")
    md_lines.extend([
        "",
        "## Implementation Steps",
    ])
    for i, s in enumerate(plan["implementation_steps"], 1):
        md_lines.append(f"{i}. {s}")
    md_lines.extend([
        "",
        "## Risks & Ambiguities",
        "- " + (plan["risks_and_ambiguities"][0] if plan["risks_and_ambiguities"] else "None identified"),
        "",
           "**do-not-auto-apply: true**",
    ])
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    # Write first-edit concise artifact
    first_edit_path = jack_dir / "repo-task-first-edit.md"
    first_edit_lines = [
        "# First Edit Recommendation",
        f"**File**: `{plan['recommended_first_edit_area']}`" if plan["recommended_first_edit_area"] else "*No concrete file identified*",
        "",
        f"**Why**: {synthesize_first_edit_reason(args.task, profile, brief, plan['recommended_first_edit_area'])}",
        "",
        "**Key uncertainty to resolve**:",
        f"- {plan['risks_and_ambiguities'][0] if plan['risks_and_ambiguities'] else 'None'}",
    ]
    first_edit_path.write_text("\n".join(first_edit_lines), encoding="utf-8")

    print(f"Wrote plan: {json_path}")
    print(f"Wrote markdown: {md_path}")
    print(f"Wrote first-edit note: {first_edit_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
