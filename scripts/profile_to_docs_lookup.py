#!/usr/bin/env python3
"""Bridge: profile -> docs lookup.

Consumes `jack/repo-stack-profile.json` and uses `scripts/docs_lookup.py`
to fetch a small set of official-docs pages for the repo's top queries.

Outputs (repo-local, recommendation-only):
- `jack/repo-docs-lookup-plan.json` (structured plan)
- `jack/repo-docs-lookup-plan.md` (human brief)
- `jack/repo-docs-evidence.jsonl` (appended JSONL evidence from docs_lookup)

This script is intentionally conservative: it selects at most 3 queries,
prefers official stacks known to `scripts/docs_lookup.py`, and records
ambiguities rather than guessing when signals are weak.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Tuple, cast


# Extend registry to include tooling docs for package managers and test tools
DEFAULT_REGISTRY: Dict[str, List[str]] = {
    "python": ["https://docs.python.org/3/"],
    "fastapi": ["https://fastapi.tiangolo.com/en/latest/"],
    "django": ["https://docs.djangoproject.com/en/stable/"],
    "typescript": ["https://www.typescriptlang.org/docs/"],
    "react": ["https://reactjs.org/docs/"],
    "nextjs": ["https://nextjs.org/docs/"],
    # Python packaging / environment tooling
    "poetry": ["https://python-poetry.org/docs/"],
    "pip": ["https://pip.pypa.io/en/stable/"],
    "pipenv": ["https://pipenv.pypa.io/en/latest/"],
    "uv": ["https://github.com/astral-sh/uv#documentation"],
    "setuptools": ["https://setuptools.pypa.io/en/latest/"],
    "pytest": ["https://docs.pytest.org/en/stable/"],
}

# map profile-detected framework/runtime names to docs_lookup registry keys
FRAMEWORK_TO_STACK = {
    "Next.js": "nextjs",
    "NextJS": "nextjs",
    "React": "react",
    "TypeScript": "typescript",
    "FastAPI": "fastapi",
    "Django": "django",
    "Python": "python",
}

# Framework -> conservative query templates (ordered by priority)
FRAMEWORK_QUERY_TEMPLATES = {
    "Next.js": [
        "Next.js app router data fetching",
        "Next.js middleware authentication",
    ],
    "React": [
        "React hooks best practices",
        "React performance optimization",
    ],
    "TypeScript": [
        "TypeScript project references",
        "TypeScript module resolution",
    ],
    "FastAPI": [
        "FastAPI dependency injection auth",
        "FastAPI async endpoints best practices",
    ],
    "Django": [
        "Django database migrations best practices",
        "Django deployment recommendations",
    ],
}


IMPLEMENTATION_TOOLING_QUERY = (
    "Python argparse, subprocess, pathlib, and JSON for tooling scripts"
)
IMPLEMENTATION_TOOLING_SOURCES = [
    "https://docs.python.org/3/library/argparse.html",
    "https://docs.python.org/3/library/pathlib.html",
    "https://docs.python.org/3/library/json.html",
    "https://docs.python.org/3/library/subprocess.html",
]

PACKAGING_TOOLING_QUERY = "Python packaging with pip/poetry"
PACKAGING_TOOLING_SOURCES = [
    "https://packaging.python.org/en/latest/",
    "https://pip.pypa.io/en/stable/",
    "https://python-poetry.org/docs/",
]

GENERIC_PYTHON_PACKAGING_QUERY = "Python packaging and dependency management"


def has_jack_self_hosting_signals(repo_root: Path | None) -> bool:
    if repo_root is None:
        return False
    signal_paths = [
        repo_root / "scripts" / "run_repo_task_flow.py",
        repo_root / "scripts" / "profile_to_docs_lookup.py",
        repo_root / "docs" / "jac" / "README.md",
    ]
    return sum(path.is_file() for path in signal_paths) >= 2


def source_urls_for_query(
    query: str, stack: str, repo_root: Path | None = None
) -> List[str]:
    if (
        stack == "python"
        and query == IMPLEMENTATION_TOOLING_QUERY
        and has_jack_self_hosting_signals(repo_root)
    ):
        return list(IMPLEMENTATION_TOOLING_SOURCES)
    if (
        stack == "python"
        and query == PACKAGING_TOOLING_QUERY
        and has_jack_self_hosting_signals(repo_root)
    ):
        return list(PACKAGING_TOOLING_SOURCES)
    return list(DEFAULT_REGISTRY.get(stack, []))


def _max_query_count(
    shape: str, shape_conf: str, base_conf: str, languages: List[str]
) -> int:
    if base_conf == "high" and shape_conf == "high":
        max_queries = 3
    elif base_conf == "medium" or shape_conf == "medium":
        max_queries = 2
    else:
        max_queries = 1

    if (
        shape == "python_tooling_repo"
        and shape_conf == "high"
        and any("py" in str(l).lower() for l in languages)
    ):
        max_queries = max(max_queries, 2)

    return max_queries


def _append_query_candidate(
    candidates: List[Dict[str, Any]],
    rationale: Dict[str, Dict[str, Any]],
    query: str,
    stack: str,
    why: str,
    signals: Dict[str, Any],
) -> None:
    candidates.append({"query": query, "stack": stack})
    rationale[query] = {"signals": signals, "target": stack, "why": why}


def _string_list(value: Any) -> List[str]:
    items = cast(List[Any], value or [])
    return [str(item) for item in items]


def _append_recommended_queries(
    profile: Dict[str, Any],
    frameworks: List[str],
    max_queries: int,
    candidates: List[Dict[str, Any]],
    rationale: Dict[str, Dict[str, Any]],
) -> bool:
    recommended = _string_list(profile.get("recommended_doc_queries"))
    if not recommended:
        return False

    stack = FRAMEWORK_TO_STACK.get(frameworks[0], "") if frameworks else ""
    for query in recommended[:max_queries]:
        _append_query_candidate(
            candidates, rationale, query, stack, "profile recommendation", {}
        )
    return True


def _append_framework_queries(
    frameworks: List[str],
    max_queries: int,
    candidates: List[Dict[str, Any]],
    rationale: Dict[str, Dict[str, Any]],
) -> None:
    for fw in frameworks:
        templates = FRAMEWORK_QUERY_TEMPLATES.get(fw, [])
        for query in templates:
            if len(candidates) >= max_queries:
                return
            stack = FRAMEWORK_TO_STACK.get(fw, "")
            _append_query_candidate(
                candidates,
                rationale,
                query,
                stack,
                "framework template",
                {"framework": fw},
            )


def _shape_query_candidates(
    shape: str, frameworks: List[str], repo_root: Path | None
) -> List[Tuple[str, str]]:
    if shape == "python_tooling_repo":
        if has_jack_self_hosting_signals(repo_root):
            return [
                (IMPLEMENTATION_TOOLING_QUERY, "python"),
                (PACKAGING_TOOLING_QUERY, "python"),
            ]
        return [
            ("Python virtualenv and environment management", "python"),
            (PACKAGING_TOOLING_QUERY, "python"),
        ]

    if shape == "python_library_repo":
        return [
            ("Python library packaging and publishing", "python"),
            ("Python testing with pytest", "python"),
        ]

    if shape == "python_app_repo":
        if frameworks:
            return [("Python web application deployment best practices", "python")]
        return [("Python web frameworks overview", "python")]

    if shape in ("mixed_utility_repo", "ambiguous"):
        return [(GENERIC_PYTHON_PACKAGING_QUERY, "python")]

    return []


def _append_shape_queries(
    shape_queries: List[Tuple[str, str]],
    shape: str,
    max_queries: int,
    candidates: List[Dict[str, Any]],
    rationale: Dict[str, Dict[str, Any]],
) -> None:
    for query, stack in shape_queries:
        if len(candidates) >= max_queries:
            return
        _append_query_candidate(
            candidates,
            rationale,
            query,
            stack,
            f"shape {shape} query",
            {"repo_shape": shape},
        )


def _append_language_fallback(
    languages: List[str],
    runtimes: List[str],
    candidates: List[Dict[str, Any]],
    rationale: Dict[str, Dict[str, Any]],
    ambiguity: List[str],
) -> None:
    if any(l.lower().startswith("py") for l in languages):
        query = GENERIC_PYTHON_PACKAGING_QUERY
        _append_query_candidate(
            candidates, rationale, query, "python", "language fallback", {}
        )
        return

    if any(l.lower().startswith("ts") for l in languages) or any(
        r.lower() == "node" for r in runtimes
    ):
        query = "Node/TypeScript module resolution"
        _append_query_candidate(
            candidates, rationale, query, "typescript", "runtime fallback", {}
        )
        return

    ambiguity.append(
        "No clear framework, language, or shape signals for query selection"
    )


def pick_queries(
    profile: Dict[str, Any], repo_root: Path | None = None
) -> Tuple[List[Dict[str, Any]], List[str], Dict[str, Dict[str, Any]]]:  # noqa: C901
    """Return selected queries (dicts), ambiguity notes, and per-query rationale.

    Shape‑aware selection: use repo_shape to guide query templates and source
    prioritisation while still respecting strong framework signals.
    """
    frameworks = _string_list(profile.get("detected_frameworks"))
    runtimes = _string_list(profile.get("detected_runtime_targets"))
    languages = _string_list(profile.get("detected_languages"))
    shape = str(profile.get("repo_shape", "ambiguous"))
    shape_conf = str(profile.get("repo_shape_confidence") or "low").lower()
    base_conf = str(profile.get("confidence_level") or "low").lower()
    max_queries = _max_query_count(shape, shape_conf, base_conf, languages)

    candidates: List[Dict[str, Any]] = []
    ambiguity: List[str] = []
    rationale: Dict[str, Dict[str, Any]] = {}

    if _append_recommended_queries(
        profile, frameworks, max_queries, candidates, rationale
    ):
        return candidates, ambiguity, rationale

    _append_framework_queries(frameworks, max_queries, candidates, rationale)

    if len(candidates) < max_queries:
        shape_queries = _shape_query_candidates(shape, frameworks, repo_root)
        _append_shape_queries(shape_queries, shape, max_queries, candidates, rationale)

    if not candidates:
        _append_language_fallback(languages, runtimes, candidates, rationale, ambiguity)

    return candidates, ambiguity, rationale


def write_plan(
    out_json: Path,
    out_md: Path,
    selected: List[Dict[str, Any]],
    profile: Dict[str, Any],
    ambiguity: List[str],
    rationale: Dict[str, Dict[str, Any]],
    repo_root: Path | None = None,
) -> None:  # noqa: C901
    """Write a concise plan JSON and markdown.

    The implementation is deliberately simple to keep cognitive complexity low.
    It records repo shape, selected queries, source mappings, and basic signals.
    """
    repo_shape = str(profile.get("repo_shape", "ambiguous"))
    repo_shape_confidence = str(profile.get("repo_shape_confidence", "low"))
    repo_shape_notes = _string_list(profile.get("repo_shape_notes"))
    selected_queries = [item["query"] for item in selected]
    selected_sources = {
        item["query"]: source_urls_for_query(
            item["query"], str(item.get("stack", "")), repo_root
        )
        for item in selected
    }
    stack_signals_used: Dict[str, Any] = {
        "detected_frameworks": _string_list(profile.get("detected_frameworks")),
        "detected_package_managers": _string_list(
            profile.get("detected_package_managers")
        ),
        "detected_build_tools": _string_list(profile.get("detected_build_tools")),
        "detected_runtime_targets": _string_list(
            profile.get("detected_runtime_targets")
        ),
    }
    ambiguity_notes = list(ambiguity)
    plan: Dict[str, Any] = {
        "repo_shape": repo_shape,
        "repo_shape_confidence": repo_shape_confidence,
        "repo_shape_notes": repo_shape_notes,
        "selected_queries": selected_queries,
        "selected_sources": selected_sources,
        "query_rationales": rationale,
        "stack_signals_used": stack_signals_used,
        "ambiguity_notes": ambiguity_notes,
        "do_not_auto_execute": True,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    md_lines: List[str] = []
    md_lines.append("# Repo Docs Lookup Plan")
    md_lines.append("")
    md_lines.append("## Repo shape")
    md_lines.append(f"- shape: {repo_shape}")
    md_lines.append(f"- confidence: {repo_shape_confidence}")
    if repo_shape_notes:
        md_lines.append("- notes:")
        for n in repo_shape_notes:
            md_lines.append(f"  - {n}")
    md_lines.append("")
    md_lines.append("## Selected queries")
    for item in selected:
        md_lines.append(f"- {item['query']} (stack: {item.get('stack', '')})")
    md_lines.append("")
    md_lines.append("## Query rationales")
    for q, r in rationale.items():
        md_lines.append(
            f"- {q}: target={r.get('target')}; why={r.get('why')}; signals={r.get('signals')}"
        )
    md_lines.append("")
    md_lines.append("## Stack signals used")
    for k, v in stack_signals_used.items():
        md_lines.append(f"- {k}: {v}")
    md_lines.append("")
    md_lines.append("## Ambiguity notes")
    if ambiguity:
        for a in ambiguity:
            md_lines.append(f"- {a}")
    else:
        md_lines.append("- (none)")
    md_lines.append("")
    md_lines.append("**do_not_auto_execute: true**")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def load_profile_json(profile_path: Path) -> Dict[str, Any] | None:
    try:
        return json.loads(profile_path.read_text(encoding="utf-8"))
    except Exception:
        return None


def load_existing_evidence_lines(out_evidence: Path) -> set[str]:
    existing_lines: set[str] = set()
    if not out_evidence.exists():
        return existing_lines

    try:
        with out_evidence.open("r", encoding="utf-8") as exf:
            for line in exf:
                stripped = line.strip()
                if stripped:
                    existing_lines.add(stripped)
    except Exception:
        return set()

    return existing_lines


def append_tmp_evidence(
    tmp_out: Path,
    out_evidence: Path,
    existing_lines: set[str],
    query: str,
    max_lines_per_query: int = 6,
) -> bool:
    if not tmp_out.exists():
        return False

    written_count = 0
    try:
        with tmp_out.open("r", encoding="utf-8") as src, out_evidence.open(
            "a", encoding="utf-8"
        ) as dst:
            for line in src:
                stripped = line.strip()
                if not stripped or stripped in existing_lines:
                    continue
                dst.write(stripped + "\n")
                existing_lines.add(stripped)
                written_count += 1
                if written_count >= max_lines_per_query:
                    break
    except Exception as exc:
        print(
            f"Warning: failed to append tmp evidence for '{query}': {exc}",
            file=sys.stderr,
        )
    finally:
        try:
            tmp_out.unlink()
        except Exception:
            pass

    return written_count > 0


def append_selected_evidence(
    repo: Path, selected: List[Dict[str, Any]], out_evidence: Path
) -> bool:
    docs_lookup_path = (Path(__file__).parent / "docs_lookup.py").resolve()
    out_evidence.parent.mkdir(parents=True, exist_ok=True)
    existing_lines = load_existing_evidence_lines(out_evidence)
    any_written = False

    for idx, item in enumerate(selected, start=1):
        query = item["query"]
        stack = item.get("stack") or ""
        source_urls = source_urls_for_query(query, stack, repo_root=repo)
        tmp_out = out_evidence.with_name(out_evidence.stem + f"-{idx}.jsonl")
        code = run_docs_lookup_for_query(
            docs_lookup_path, query, stack, source_urls, tmp_out
        )
        if code == 0:
            any_written = (
                append_tmp_evidence(tmp_out, out_evidence, existing_lines, query)
                or any_written
            )
            continue
        print(
            f"Warning: docs_lookup failed for query '{query}' (stack={stack})",
            file=sys.stderr,
        )

    return any_written


def run_docs_lookup_for_query(
    docs_lookup_path: Path,
    query: str,
    stack: str,
    source_urls: List[str],
    out_path: Path,
) -> int:
    registry_path: Path | None = None
    try:
        args = [
            sys.executable,
            str(docs_lookup_path),
            "--query",
            query,
            "--out",
            str(out_path),
        ]
        if stack:
            args += ["--stack", stack]

        default_urls = DEFAULT_REGISTRY.get(stack, [])
        if source_urls and source_urls != default_urls:
            with tempfile.NamedTemporaryFile(
                "w", delete=False, suffix=".json", encoding="utf-8"
            ) as fh:
                json.dump({stack: source_urls}, fh, ensure_ascii=False, indent=2)
                fh.write("\n")
                registry_path = Path(fh.name)
            args += ["--registry-file", str(registry_path)]

        # call the existing docs_lookup.py via the active Python interpreter
        proc = subprocess.run(args, capture_output=True, text=True)
        # forward some output for visibility
        if proc.stdout:
            print(proc.stdout)
        if proc.stderr:
            print(proc.stderr, file=sys.stderr)
        return proc.returncode
    finally:
        if registry_path is not None:
            try:
                registry_path.unlink()
            except Exception:
                pass


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--profile-json", default="jack/repo-stack-profile.json")
    ap.add_argument("--out-plan", default="jack/repo-docs-lookup-plan.json")
    ap.add_argument("--out-plan-md", default="jack/repo-docs-lookup-plan.md")
    ap.add_argument("--out-evidence", default="jack/repo-docs-evidence.jsonl")
    args = ap.parse_args(argv)

    repo = Path(args.repo_root).resolve()
    profile_path = (repo / args.profile_json).resolve()
    if not profile_path.exists():
        print(f"Profile not found: {profile_path}", file=sys.stderr)
        return 2

    profile = load_profile_json(profile_path)
    if profile is None:
        print(f"Failed to read profile: {profile_path}", file=sys.stderr)
        return 2

    selected, ambiguity, rationale = pick_queries(profile, repo_root=repo)

    out_plan = (repo / args.out_plan).resolve()
    out_plan_md = (repo / args.out_plan_md).resolve()
    out_evidence = (repo / args.out_evidence).resolve()

    write_plan(
        out_plan, out_plan_md, selected, profile, ambiguity, rationale, repo_root=repo
    )

    any_written = append_selected_evidence(repo, selected, out_evidence)

    if any_written:
        print(f"Wrote plan: {out_plan} and evidence: {out_evidence}")
        return 0
    else:
        print(
            "No evidence was written; check network or registry mappings",
            file=sys.stderr,
        )
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
