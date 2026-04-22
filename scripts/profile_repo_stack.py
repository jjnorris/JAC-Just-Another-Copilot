#!/usr/bin/env python3
"""Profile repository stack: languages, frameworks, package managers, docs.

Conservative, recommendation-only. Writes:
- `jack/repo-stack-profile.json`
- `jack/repo-stack-profile.md`
- `jack/repo-research-brief.md`

Do not perform network lookups. Detection is based on manifest/config files
and obvious file presence or dependency mentions in manifests. Avoid guessing
from random text.
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple, Set, cast
import re


PACKAGE_JSON = "package.json"
TSCONFIG_JSON = "tsconfig.json"
NEXT_CONFIG_JS = "next.config.js"
NEXT_CONFIG_CJS = "next.config.cjs"
NEXT_CONFIG_MJS = "next.config.mjs"
PYPROJECT_TOML = "pyproject.toml"
REQUIREMENTS_TXT = "requirements.txt"
CARGO_TOML = "Cargo.toml"
GO_MOD = "go.mod"
DOCKERFILE = "Dockerfile"
NEXT_JS_NAME = "Next.js"
NONE_DETECTED_NOTE = "- (none detected)"
SOURCE_SCAN_DIR_EXCLUDES = {"node_modules", ".git"}
SOURCE_SIGNAL_PATTERNS = {
    "FastAPI": [
        r"\b(?:from|import)\s+fastapi\b",
        r"\bFastAPI\s*\(",
        r"@app\.(?:get|post|put|delete)\b",
    ],
    "Django": [r"\b(?:from|import)\s+django\b", r"\bdjango\."],
    "Flask": [r"\b(?:from|import)\s+flask\b", r"Flask\s*\("],
    "React": [r"\bfrom\s+[\'\"]react[\'\"]", r"\bimport\s+React\b"],
    NEXT_JS_NAME: [
        r"\bfrom\s+[\'\"]next(?:/|\b)",
        r"\bgetServerSideProps\b",
        r"\bgetStaticProps\b",
        r"\bgetStaticPaths\b",
    ],
}


MANIFEST_FILES = [
    PACKAGE_JSON,
    TSCONFIG_JSON,
    NEXT_CONFIG_JS,
    NEXT_CONFIG_CJS,
    NEXT_CONFIG_MJS,
    PYPROJECT_TOML,
    REQUIREMENTS_TXT,
    CARGO_TOML,
    GO_MOD,
    DOCKERFILE,
]

# Source scanning limits and extensions (secondary, bounded signal)
SOURCE_EXTS = [".py", ".ts", ".tsx", ".js", ".jsx"]
MAX_SOURCE_FILES_SCANNED = 200


def should_skip_source_path(path: Path) -> bool:
    return any(part in SOURCE_SCAN_DIR_EXCLUDES for part in path.parts)


def iter_source_files(repo: Path, exts: List[str]):
    for ext in exts:
        for fp in repo.rglob(f"*{ext}"):
            if should_skip_source_path(fp):
                continue
            yield fp


def read_source_text(path: Path, limit: int = 10000) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except Exception:
        return ""


def append_unique(items: List[str], value: str) -> None:
    if value not in items:
        items.append(value)


def file_matches_any_extension(name: str, exts: List[str]) -> bool:
    return any(name.endswith(ext) for ext in exts)


def matching_extensions(name: str, exts: List[str]) -> List[str]:
    return [ext for ext in exts if name.endswith(ext)]


def scan_source_text(
    text: str, compiled_patterns: Dict[str, List[re.Pattern]]
) -> List[str]:
    matched: List[str] = []
    for signal, regexes in compiled_patterns.items():
        if any(pattern.search(text) for pattern in regexes):
            matched.append(signal)
    return matched


def scan_source_signals(
    repo: Path, exts: List[str], max_files: int = MAX_SOURCE_FILES_SCANNED
) -> Dict[str, List[str]]:
    """
    Scan a bounded set of source files for explicit import/use patterns.
    Returns a mapping: signal_name -> list of relative file paths where it was seen.

    Conservative: stops after `max_files` files scanned and skips common vendor dirs.
    """
    compiled = {
        signal: [re.compile(pattern) for pattern in patterns]
        for signal, patterns in SOURCE_SIGNAL_PATTERNS.items()
    }
    matches: Dict[str, List[str]] = {signal: [] for signal in compiled}

    scanned = 0
    for fp in iter_source_files(repo, exts):
        rel = fp.relative_to(repo).as_posix()
        text = read_source_text(fp)
        for signal in scan_source_text(text, compiled):
            append_unique(matches[signal], rel)
        scanned += 1
        if scanned >= max_files:
            return matches
    return matches


def read_json(path: Path) -> Dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def find_files(repo: Path, patterns: List[str]) -> List[Path]:
    found = []
    for p in patterns:
        for f in repo.glob(p):
            found.append(f)
    return sorted(found)


def scan_repo_for_extensions(
    repo: Path, exts: List[str], max_scan: int = 20000
) -> Dict[str, int]:
    counts: Dict[str, int] = cast(Dict[str, int], dict.fromkeys(exts, 0))
    scanned = 0
    for root, dirs, files in os.walk(repo):
        # skip .git and node_modules for performance
        if should_skip_source_path(Path(root)):
            continue
        for fn in files:
            scanned += 1
            name = fn.lower()
            for ext in matching_extensions(name, exts):
                counts[ext] += 1
            if scanned >= max_scan:
                return counts
    return counts


def detect_from_package_json(pjson: Dict) -> Tuple[List[str], List[str], List[str]]:
    detected = []
    frameworks = []
    build_tools = []
    deps = {}
    deps.update(pjson.get("dependencies", {}) or {})
    deps.update(pjson.get("devDependencies", {}) or {})
    keys = set(map(str.lower, deps.keys()))
    if "next" in keys or any(k.startswith("next") for k in keys):
        frameworks.append(NEXT_JS_NAME)
    if "react" in keys or any(k.startswith("react") for k in keys):
        frameworks.append("React")
    if "vue" in keys:
        frameworks.append("Vue")
    if "express" in keys:
        frameworks.append("Express")
    if "nestjs" in keys:
        frameworks.append("NestJS")
    if "fastify" in keys:
        frameworks.append("Fastify")
    # build tools
    for tool in (
        "webpack",
        "vite",
        "rollup",
        "parcel",
        "esbuild",
        "typescript",
        "babel",
    ):
        if tool in keys:
            build_tools.append(tool)
    # package managers inferred by lockfiles elsewhere
    return detected, frameworks, build_tools


def detect_python_from_requirements(text: str) -> List[str]:
    frameworks = []
    lower = text.lower()
    if "fastapi" in lower:
        frameworks.append("FastAPI")
    if "django" in lower:
        frameworks.append("Django")
    if "flask" in lower:
        frameworks.append("Flask")
    return frameworks


def detect_from_pyproject(text: str) -> List[str]:
    frameworks = []
    lower = text.lower()
    if "fastapi" in lower:
        frameworks.append("FastAPI")
    if "django" in lower:
        frameworks.append("Django")
    if "flask" in lower:
        frameworks.append("Flask")
    if "tool.poetry" in lower:
        frameworks.append("Poetry")
    return frameworks


def detect_from_cargo(text: str) -> List[str]:
    frameworks = []
    lower = text.lower()
    if "rocket" in lower or "actix" in lower:
        frameworks.append("Rust web framework (rocket/actix)")
    return frameworks


def recommend_docs(for_list: List[str]) -> List[str]:
    mapping = {
        NEXT_JS_NAME: "https://nextjs.org/docs/",
        "React": "https://reactjs.org/docs/",
        "TypeScript": "https://www.typescriptlang.org/docs/",
        "FastAPI": "https://fastapi.tiangolo.com/en/latest/",
        "Django": "https://docs.djangoproject.com/en/stable/",
        "Rust": "https://doc.rust-lang.org/book/",
        "Python": "https://docs.python.org/3/",
        "Node": "https://nodejs.org/en/docs/",
    }
    out = []
    for k in for_list:
        if k in mapping:
            out.append(mapping[k])
    return out


def generate_doc_queries(frameworks: List[str], runtimes: List[str]) -> List[str]:
    """Generate a short, high-confidence list of queries (max 3).

    Prefer framework-derived queries, fall back to runtime-level queries.
    """
    queries: List[str] = []
    # prefer the first (most prominent) framework only to avoid noisy lists
    if frameworks:
        primary = frameworks[0]
        if primary == NEXT_JS_NAME:
            queries = [
                f"{NEXT_JS_NAME} app router data fetching",
                f"{NEXT_JS_NAME} middleware authentication",
            ]
        elif primary == "React":
            queries = [
                "React hooks best practices",
                "React performance optimization",
            ]
        elif primary == "TypeScript":
            queries = [
                "TypeScript project references",
                "TypeScript module resolution",
            ]
        elif primary == "FastAPI":
            queries = [
                "FastAPI dependency injection auth",
                "FastAPI async endpoints best practices",
            ]
        elif primary == "Django":
            queries = [
                "Django database migrations best practices",
                "Django deployment recommendations",
            ]
        elif primary == "Rust":
            queries = [
                "Rust async web frameworks",
            ]
    # if still empty, use runtime-level gentle queries
    if not queries and runtimes:
        rt = runtimes[0]
        if rt == "Python":
            queries = ["Python packaging and dependency management"]
        elif rt == "Node":
            queries = ["Node module resolution and package management"]

    # cap to 3 queries max, but prefer 2 for conservatism
    return queries[:2]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo-root", default=".")
    ap.add_argument("--out-json", default="jack/repo-stack-profile.json")
    ap.add_argument("--out-md", default="jack/repo-stack-profile.md")
    ap.add_argument("--brief-md", default="jack/repo-research-brief.md")
    args = ap.parse_args(argv)

    repo = Path(args.repo_root)
    repo = repo.resolve()

    evidence_files = []
    for mf in MANIFEST_FILES:
        p = repo / mf
        if p.exists():
            evidence_files.append(p.relative_to(repo).as_posix())

    # next.config.*
    for f in repo.glob("next.config.*"):
        evidence_files.append(f.relative_to(repo).as_posix())

    # workflows
    for wf in repo.glob(".github/workflows/*.yml"):
        evidence_files.append(wf.relative_to(repo).as_posix())

    # lockfiles
    for lf in (
        "yarn.lock",
        "pnpm-lock.yaml",
        "package-lock.json",
        "poetry.lock",
        "Pipfile",
    ):
        p = repo / lf
        if p.exists():
            evidence_files.append(p.relative_to(repo).as_posix())

    # detect languages by extension
    exts = [".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".java", ".php", ".rb"]
    ext_counts = scan_repo_for_extensions(repo, exts)
    detected_languages = [e.lstrip(".") for e, c in ext_counts.items() if c > 0]

    detected_frameworks = []
    detected_package_managers = []
    detected_build_tools = []
    detected_runtime_targets = []
    manifest_frameworks: List[str] = []

    # Node / package.json
    pjson = repo / "package.json"
    if pjson.exists():
        pj = read_json(pjson)
        _, frameworks, build_tools = detect_from_package_json(pj)
        for f in frameworks:
            if f not in detected_frameworks:
                detected_frameworks.append(f)
            if f not in manifest_frameworks:
                manifest_frameworks.append(f)
        for b in build_tools:
            if b not in detected_build_tools:
                detected_build_tools.append(b)
        # package managers from lockfiles
        if (repo / "yarn.lock").exists():
            detected_package_managers.append("yarn")
        if (repo / "pnpm-lock.yaml").exists():
            detected_package_managers.append("pnpm")
        if (repo / "package-lock.json").exists():
            detected_package_managers.append("npm")
        if (
            "typescript" in (pj.get("devDependencies", {}) or {})
            or (repo / TSCONFIG_JSON).exists()
        ):
            if "TypeScript" not in detected_frameworks:
                detected_frameworks.append("TypeScript")
        detected_runtime_targets.append("Node")

    # TypeScript config
    if (repo / TSCONFIG_JSON).exists():
        if "TypeScript" not in detected_frameworks:
            detected_frameworks.append("TypeScript")
        if "TypeScript" not in manifest_frameworks:
            manifest_frameworks.append("TypeScript")

    # Next.js explicit config
    for f in repo.glob("next.config.*"):
        if NEXT_JS_NAME not in detected_frameworks:
            detected_frameworks.append(NEXT_JS_NAME)
        if NEXT_JS_NAME not in manifest_frameworks:
            manifest_frameworks.append(NEXT_JS_NAME)
        if "Node" not in detected_runtime_targets:
            detected_runtime_targets.append("Node")

    # Python tooling detection (authoritative files first)
    python_version = None
    # .python-version – simple version string
    if (repo / ".python-version").exists():
        python_version = read_text(repo / ".python-version").strip().split()[0]

    # pyproject.toml – may contain Poetry config, version, and dependencies
    if (repo / PYPROJECT_TOML).exists():
        txt = read_text(repo / PYPROJECT_TOML)
        pfs = detect_from_pyproject(txt)
        for f in pfs:
            if f not in detected_frameworks:
                detected_frameworks.append(f)
            if f not in manifest_frameworks:
                manifest_frameworks.append(f)
        # Detect Poetry as package manager
        if "tool.poetry" in txt:
            detected_package_managers.append("poetry")
        else:
            detected_package_managers.append("pip")
        # Extract a version constraint if present
        import re as _re

        m = _re.search(r"^\s*python\s*=\s*['\"]([^'\"]+)['\"]", txt, _re.MULTILINE)
        if m and not python_version:
            python_version = m.group(1)
        if "Python" not in detected_runtime_targets:
            detected_runtime_targets.append("Python")
    # requirements.txt – fallback for pip projects
    elif (repo / REQUIREMENTS_TXT).exists():
        txt = read_text(repo / REQUIREMENTS_TXT)
        pfs = detect_python_from_requirements(txt)
        for f in pfs:
            if f not in detected_frameworks:
                detected_frameworks.append(f)
            if f not in manifest_frameworks:
                manifest_frameworks.append(f)
        detected_package_managers.append("pip")
        if "Python" not in detected_runtime_targets:
            detected_runtime_targets.append("Python")
    # requirements-dev.txt – may hint at test tools like pytest
    if (repo / "requirements-dev.txt").exists():
        txt = read_text(repo / "requirements-dev.txt")
        if "pytest" in txt.lower() and "pytest" not in detected_frameworks:
            detected_frameworks.append("pytest")
    # Pipfile – indicates pipenv usage
    if (repo / "Pipfile").exists():
        detected_package_managers.append("pipenv")
    # poetry.lock – confirms Poetry usage
    if (repo / "poetry.lock").exists():
        detected_package_managers.append("poetry")
    # uv.lock – indicates uv usage
    if (repo / "uv.lock").exists():
        detected_package_managers.append("uv")
    # setup.cfg / setup.py – classic setuptools projects
    if (repo / "setup.cfg").exists() or (repo / "setup.py").exists():
        detected_package_managers.append("setuptools")
        if "Python" not in detected_runtime_targets:
            detected_runtime_targets.append("Python")

    # Rust
    if (repo / CARGO_TOML).exists():
        txt = read_text(repo / CARGO_TOML)
        pfs = detect_from_cargo(txt)
        for f in pfs:
            if f not in detected_frameworks:
                detected_frameworks.append(f)
            if f not in manifest_frameworks:
                manifest_frameworks.append(f)
        if "Rust" not in detected_runtime_targets:
            detected_runtime_targets.append("Rust")
        if "cargo" not in detected_package_managers:
            detected_package_managers.append("cargo")

    # Go
    if (repo / "go.mod").exists():
        if "Go" not in detected_runtime_targets:
            detected_runtime_targets.append("Go")
        if "go modules" not in detected_package_managers:
            detected_package_managers.append("go modules")

    # Docker
    if (repo / "Dockerfile").exists():
        if "Docker" not in detected_build_tools:
            detected_build_tools.append("Docker")
        if "Docker" not in detected_runtime_targets:
            detected_runtime_targets.append("Docker")

    # CI workflows
    if any(repo.glob(".github/workflows/*.yml")):
        evidence_files.append(".github/workflows/*")

    # --- bounded source-signal scanning (secondary, lower-trust signals) ---
    source_matches = scan_source_signals(
        repo, SOURCE_EXTS, max_files=MAX_SOURCE_FILES_SCANNED
    )
    # consistent source hints are those seen in multiple files
    source_consistent = [
        sig for sig, files in source_matches.items() if len(files) >= 2
    ]
    # If manifests absent, allow repeated source hints to seed detected frameworks (lower trust)
    if not manifest_frameworks and source_consistent:
        for s in source_consistent:
            if s not in detected_frameworks:
                detected_frameworks.append(s)

    # If manifests present, treat source hints as supporting evidence; add if consistent and not conflicting
    if manifest_frameworks and source_consistent:
        # if source hints add new frameworks not in manifests, note them (do not override manifests)
        extra = [s for s in source_consistent if s not in manifest_frameworks]
        if extra:
            for s in extra:
                if s not in detected_frameworks:
                    detected_frameworks.append(s)

    # Record which source files contributed to source-based hints in confidence notes below

    # Deduplicate lists
    detected_frameworks = sorted(set(detected_frameworks))
    detected_package_managers = sorted(set(detected_package_managers))
    detected_build_tools = sorted(set(detected_build_tools))
    detected_runtime_targets = sorted(set(detected_runtime_targets))

    # Build improved confidence notes including manifest vs source contributions
    confidence_notes = []
    if evidence_files:
        confidence_notes.append(
            f"Manifests/configs present: {', '.join(evidence_files)}"
        )
    if manifest_frameworks:
        confidence_notes.append(
            f"Manifest-detected frameworks: {', '.join(manifest_frameworks)}"
        )
    if any(source_matches.values()):
        # summarize up to 3 files per signal
        for sig, files in source_matches.items():
            if files:
                sample = files[:3]
                confidence_notes.append(
                    f"Source hint: {sig} seen in {len(files)} file(s) (examples: {', '.join(sample)})"
                )

    # detect conflicts between manifests and source hints
    if manifest_frameworks and any(source_matches.values()):
        src_set = {s for s, files in source_matches.items() if files}
        man_set = set(manifest_frameworks)
        conflict = src_set - man_set
        if conflict:
            confidence_notes.append(
                f"Conflicting signals: manifests indicate {', '.join(man_set)} but source hints include {', '.join(conflict)}; confidence reduced"
            )
    # recommended doc sources and queries
    doc_sources = recommend_docs(detected_frameworks + detected_runtime_targets)
    doc_queries = generate_doc_queries(detected_frameworks, detected_runtime_targets)

    # confidence level: high when manifest frameworks present, medium when consistent source hints exist,
    # low when only sparse signals found
    if manifest_frameworks:
        confidence_level = "high"
    elif source_consistent:
        confidence_level = "medium"
    else:
        confidence_level = "low"

    # If the repo shape later determines a high-confidence tooling/scripts repo
    # (many standalone scripts and no packaging manifest), the absence of
    # manifest-detected frameworks should not force the overall profile
    # confidence to remain 'low'. Elevate to 'medium' conservatively.
    # This adjustment is intentionally minimal and limited to the
    # python_tooling_repo high-confidence case.

    # ------------------------------------------------------------
    # Repo‑shape classification (conservative, explicit signals only)
    # ------------------------------------------------------------
    # Heuristics:
    #   * tooling/scripts – many .py files (>20) and no packaging manifest
    #   * library – packaging manifest present (pyproject.toml with [project] or [tool.poetry], or setup.cfg/setup.py) and no app framework
    #   * app – framework detected or entry‑point script (if __name__ == "__main__")
    #   * mixed_utility – both packaging and many scripts
    #   * ambiguous – none of the above
    script_count = sum(1 for _ in repo.rglob("*.py"))
    has_packaging = any(
        (repo / f).exists() for f in ("pyproject.toml", "setup.cfg", "setup.py")
    )
    has_entrypoint = False
    for fp in repo.rglob("*.py"):
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
            if "if __name__ == '__main__'" in txt or 'if __name__ == "__main__"' in txt:
                has_entrypoint = True
                break
        except Exception:
            continue
    # Determine shape
    # default values to ensure variables are always defined
    repo_shape = "ambiguous"
    shape_conf = "low"
    shape_notes = []
    if detected_frameworks:
        repo_shape = "python_app_repo"
        shape_conf = "high"
        shape_notes = [
            "Framework imports detected, indicating an application/service repository."
        ]
    # If the repo is script-heavy (many .py files) and there is no packaging manifest,
    # prefer tooling/scripts classification even if an entrypoint exists. This avoids
    # misclassifying script-heavy tooling repositories that happen to include
    # `if __name__ == '__main__'` guards as applications.
    elif script_count > 20 and not has_packaging:
        repo_shape = "python_tooling_repo"
        shape_conf = "high"
        shape_notes = ["Large number of standalone scripts and no packaging manifest."]
    elif has_entrypoint:
        repo_shape = "python_app_repo"
        shape_conf = "medium"
        shape_notes = ["Entry‑point script detected (if __name__ == '__main__')."]
    elif has_packaging and script_count > 20:
        repo_shape = "mixed_utility_repo"
        shape_conf = "medium"
        shape_notes = ["Both packaging manifest and many scripts present."]
    elif has_packaging:
        repo_shape = "python_library_repo"
        shape_conf = "high"
        shape_notes = [
            "Packaging manifest present without clear application framework."
        ]

    # Minimal adjustment: if we conclusively classified the repo as a
    # high-confidence `python_tooling_repo` (many standalone scripts with
    # no packaging manifests), conservatively raise the overall
    # `confidence_level` to `medium` when it would otherwise be `low`.
    if repo_shape == "python_tooling_repo" and shape_conf == "high":
        if confidence_level == "low":
            confidence_level = "medium"
            confidence_notes.append(
                "Overall confidence elevated to 'medium' for high-confidence tooling repo despite missing manifests."
            )

    out = {
        "detected_languages": detected_languages,
        "detected_frameworks": detected_frameworks,
        "detected_package_managers": detected_package_managers,
        "detected_build_tools": detected_build_tools,
        "detected_runtime_targets": detected_runtime_targets,
        "python_version": python_version,
        "repo_shape": repo_shape,
        "repo_shape_confidence": shape_conf,
        "repo_shape_notes": shape_notes,
        "confidence_notes": confidence_notes,
        "evidence_files": evidence_files,
        "recommended_doc_sources": doc_sources,
        "recommended_doc_queries": doc_queries,
        "confidence_level": confidence_level,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "do_not_auto_execute": True,
    }

    out_json = repo / args.out_json
    out_md = repo / args.out_md
    brief_md = repo / args.brief_md

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # write human readable md
    lines: List[str] = []
    lines.append("# JACK Repo Stack Profile")
    lines.append("")
    lines.append("## Detected languages")
    if detected_languages:
        for l in detected_languages:
            lines.append(f"- {l}")
    else:
        lines.append(NONE_DETECTED_NOTE)
    lines.append("")

    lines.append("## Detected frameworks")
    if detected_frameworks:
        for f in detected_frameworks:
            lines.append(f"- {f}")
    else:
        lines.append(NONE_DETECTED_NOTE)
    lines.append("")

    lines.append("## Detected package managers")
    if detected_package_managers:
        for p in detected_package_managers:
            lines.append(f"- {p}")
    else:
        lines.append(NONE_DETECTED_NOTE)
    lines.append("")

    lines.append("## Detected build tools / runtime targets & evidence files")
    if detected_build_tools:
        lines.append("Build tools:")
        for b in detected_build_tools:
            lines.append(f"- {b}")
    if detected_runtime_targets:
        lines.append("Runtime targets:")
        for r in detected_runtime_targets:
            lines.append(f"- {r}")
    lines.append("")

    lines.append("## Evidence files")
    if evidence_files:
        for e in evidence_files:
            lines.append(f"- {e}")
    else:
        lines.append("- (no clear manifests found)")
    lines.append("")

    lines.append("## Recommended official docs to consult first")
    if doc_sources:
        for d in doc_sources:
            lines.append(f"- {d}")
    else:
        lines.append("- (none recommended)")
    lines.append("")

    lines.append("## Recommended doc queries")
    if doc_queries:
        for q in doc_queries:
            lines.append(f"- {q}")
    else:
        lines.append("- (no queries generated)")
    lines.append("")

    lines.append("## Confidence notes")
    if confidence_notes:
        for n in confidence_notes:
            lines.append(f"- {n}")
    else:
        lines.append("- (no confidence notes)")
    lines.append("")
    lines.append("**do_not_auto_execute: true**")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # brief for researchers
    brief_lines: List[str] = []
    brief_lines.append("# Repo Research Brief")
    brief_lines.append("")
    brief_lines.append("## Inferred stack")
    brief_lines.append(
        ", ".join(detected_frameworks + detected_runtime_targets) or "(none clear)"
    )
    brief_lines.append("")
    brief_lines.append("## Preferred official docs")
    for s in doc_sources:
        brief_lines.append(f"- {s}")
    brief_lines.append("")
    brief_lines.append("## Recommended next research queries")
    for q in doc_queries[:8]:
        brief_lines.append(f"- {q}")
    brief_lines.append("")
    brief_lines.append("## Main ambiguities")
    if not evidence_files:
        brief_lines.append(
            "- No clear manifest files; language/framework inference is low confidence."
        )
    else:
        brief_lines.append("- See confidence notes in the full profile for specifics.")

    brief_md.parent.mkdir(parents=True, exist_ok=True)
    brief_md.write_text("\n".join(brief_lines) + "\n", encoding="utf-8")

    print(f"Wrote profile: {out_json} and {out_md} and brief: {brief_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
