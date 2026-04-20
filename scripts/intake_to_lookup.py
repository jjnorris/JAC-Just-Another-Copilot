#!/usr/bin/env python3
"""Bridge: convert a spec-intake artifact into docs lookup requests and optionally run them.

Usage examples:
  # plan-only from an existing spec file
  python3 scripts/intake_to_lookup.py --spec-file spec.json --out plan.json

  # from freeform text and execute lookups against a registry
  python3 scripts/intake_to_lookup.py --text "FastAPI upload service" --execute --registry-file registry.json --out plan.json --evidence-dir ./evidence

This script is intentionally conservative: it prefers to ask for missing
information rather than guess when the stack is ambiguous.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SPEC_INTAKE = REPO_ROOT / "scripts" / "spec_intake.py"
DOCS_LOOKUP = REPO_ROOT / "scripts" / "docs_lookup.py"


def load_spec(spec_file: Path) -> Dict[str, Any]:
    """Load a spec file from disk and return a parsed JSON object.

    Behavior changes (bounded hardening):
    - Validate that `spec_file` exists and is a file.
    - Read file contents with a clear IO error on failure.
    - Parse JSON with clear, actionable errors.
    - Ensure the parsed value is a `dict` (JSON object); otherwise raise TypeError.

    Note: YAML fallback is intentionally NOT added here because this repository
    does not currently import or depend on a YAML library. If needed, add
    YAML support in a follow-up change that also updates dependencies.
    """

    spec_path = Path(spec_file)
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    if not spec_path.is_file():
        raise IsADirectoryError(f"Spec path is not a file: {spec_path}")

    try:
        text = spec_path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - IO failure path
        raise IOError(f"Unable to read spec file {spec_path}: {exc}") from exc

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        # No YAML fallback: be explicit about expected format.
        raise ValueError(
            f"Spec file {spec_path} is not valid JSON: {exc}.\n"
            "Accepted format: JSON (object). If your spec is YAML, convert it to JSON "
            "or add YAML parsing support in a separate change.") from exc

    if not isinstance(parsed, dict):
        raise TypeError(
            f"Spec file {spec_path} parsed to {type(parsed).__name__}; expected a JSON object/dict.")

    return parsed


def run_spec_intake(text: str, out_file: Path) -> Dict[str, Any]:
    proc = subprocess.run([sys.executable, str(SPEC_INTAKE), "--text", text, "--out", str(out_file)], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"spec_intake failed: {proc.stderr}")
    return load_spec(out_file)


def sanitize_filename(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "item"


def collect_priority_topics(normalized_goal: str, missing: List[str]) -> List[str]:
    priority_topics: List[str] = []
    mapping = {
        "auth": "authentication",
        "storage": "data storage",
        "secrets_handling": "secrets",
        "deployment_target": "deployment",
        "observability": "observability",
        "privacy_or_regulated_data": "privacy",
        "licensing": "licensing",
        "abuse_misuse": "abuse",
    }

    for item in missing:
        if item in mapping:
            priority_topics.append(mapping[item])

    words = [word for word in re.findall(r"\w+", normalized_goal.lower()) if len(word) > 4]
    seen = set(priority_topics)
    for word in words:
        if word in seen:
            continue
        seen.add(word)
        priority_topics.append(word)
        if len(priority_topics) >= 5:
            break

    return priority_topics


def build_recommended_lookup_requests(candidate_stack: str | None, priority_topics: List[str]) -> List[Dict[str, Any]]:
    recommended_lookup_requests: List[Dict[str, Any]] = []
    if not candidate_stack:
        return recommended_lookup_requests

    recommended_lookup_requests.append(
        {
            "stack": candidate_stack,
            "query": f"getting started {candidate_stack} docs",
            "out": f"{sanitize_filename(candidate_stack)}-getting-started.jsonl",
        }
    )
    for topic in priority_topics:
        query = f"{topic} {candidate_stack} docs"
        recommended_lookup_requests.append(
            {
                "stack": candidate_stack,
                "query": query,
                "out": f"{sanitize_filename(candidate_stack)}-{sanitize_filename(topic)}.jsonl",
            }
        )
    return recommended_lookup_requests


def plan_requests_from_spec(spec: Dict[str, Any], stack_override: str | None) -> Dict[str, Any]:
    normalized_goal = spec.get("normalized_goal", "").strip()
    candidate_stack = stack_override or spec.get("candidate_stack")
    if candidate_stack == "unspecified":
        candidate_stack = None

    missing = spec.get("missing_required_details", []) or []
    priority_topics = collect_priority_topics(normalized_goal, missing)
    recommended_lookup_requests = build_recommended_lookup_requests(candidate_stack, priority_topics)

    planner: Dict[str, Any] = {
        "normalized_goal": normalized_goal,
        "candidate_stack": candidate_stack or "unspecified",
        "priority_topics": priority_topics,
        "recommended_lookup_requests": recommended_lookup_requests,
        "missing_info_that_limits_research": [] if candidate_stack else ["candidate_stack"],
    }
    return planner


def execute_requests(requests: List[Dict[str, Any]], registry_file: Path | None, out_dir: Path) -> List[str]:
    generated: List[str] = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for req in requests:
        out_path = out_dir / req.get("out", sanitize_filename(req.get("query", "req")) + ".jsonl")
        cmd = [sys.executable, str(DOCS_LOOKUP), "--query", req["query"], "--stack", req["stack"], "--out", str(out_path)]
        if registry_file:
            cmd.extend(["--registry-file", str(registry_file)])
        proc = subprocess.run(cmd, capture_output=True, text=True)
        if proc.returncode != 0:
            # surface warning but continue
            print(f"Warning: docs_lookup failed for {req['query']}: {proc.stderr}", file=sys.stderr)
            continue
        if out_path.exists() and out_path.stat().st_size > 0:
            generated.append(str(out_path))
    return generated


def load_spec_from_args(args: argparse.Namespace) -> tuple[Dict[str, Any] | None, Path | None, int | None]:
    if args.spec_file:
        return load_spec(Path(args.spec_file)), None, None

    if not args.text:
        print("Error: --text or --spec-file required", file=sys.stderr)
        return None, None, 2

    tf = tempfile.NamedTemporaryFile(suffix=".json", delete=False)
    tmp_spec = Path(tf.name)
    tf.close()
    return run_spec_intake(args.text, tmp_spec), tmp_spec, None


def maybe_execute_requests(args: argparse.Namespace, planner: Dict[str, Any]) -> tuple[str, List[str]]:
    execution_mode = "plan_only"
    generated_files: List[str] = []

    if not args.execute:
        return execution_mode, generated_files

    if planner.get("candidate_stack") in (None, "unspecified"):
        planner["missing_info_that_limits_research"].append("candidate_stack")
        return execution_mode, generated_files

    evidence_dir = Path(args.evidence_dir) if args.evidence_dir else Path(tempfile.mkdtemp(prefix="evidence_"))
    registry = Path(args.registry_file) if args.registry_file else None
    generated_files = execute_requests(planner.get("recommended_lookup_requests", []), registry, evidence_dir)
    return "executed", generated_files


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec-file", help="Existing spec intake JSON file")
    ap.add_argument("--text", help="Freeform project description text (if spec-file omitted)")
    ap.add_argument("--stack", help="Optional explicit stack override")
    ap.add_argument("--execute", action="store_true", help="Execute docs lookup requests instead of only planning")
    ap.add_argument("--registry-file", help="Optional registry JSON for docs_lookup (used when executing)")
    ap.add_argument("--evidence-dir", help="Directory to write evidence files when executing")
    ap.add_argument("--out", help="Output JSON plan file", default="intake_plan.json")
    args = ap.parse_args(argv)

    tmp_spec = None
    try:
        spec, tmp_spec, error_code = load_spec_from_args(args)
        if error_code is not None:
            return error_code
        assert spec is not None

        planner = plan_requests_from_spec(spec, args.stack)

        execution_mode, generated_files = maybe_execute_requests(args, planner)

        output = {
            "normalized_goal": planner.get("normalized_goal"),
            "candidate_stack": planner.get("candidate_stack"),
            "priority_topics": planner.get("priority_topics"),
            "recommended_lookup_requests": planner.get("recommended_lookup_requests"),
            "missing_info_that_limits_research": planner.get("missing_info_that_limits_research"),
            "execution_mode": execution_mode,
            "generated_evidence_files": generated_files,
        }

        # write output JSON
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(output, fh, ensure_ascii=False, indent=2)

        # human summary
        print(f"Plan for: {output['normalized_goal']}")
        print(f"Stack: {output['candidate_stack']}")
        print(f"Mode: {output['execution_mode']}")
        if output['generated_evidence_files']:
            print("Generated evidence:")
            for f in output['generated_evidence_files']:
                print("-", f)

        return 0
    finally:
        if tmp_spec and tmp_spec.exists():
            try:
                tmp_spec.unlink()
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
