#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
# Accept either docs/jack or docs/jac inventory for compatibility with rename
CANDIDATE_INVENTORY_PATHS = [ROOT / "docs/jack/inventory.json", ROOT / "docs/jac/inventory.json"]
INVENTORY_PATH = next((p for p in CANDIDATE_INVENTORY_PATHS if p.exists()), CANDIDATE_INVENTORY_PATHS[0])
FRONTMATTER_REQUIRED = {"name", "description"}
PATH_SUFFIXES = (".md", ".json")
STALE_PATH_SENTINELS = ("jac-copilot/", "jack-copilot/")
INVISIBLE_CHARS = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\ufeff",
    "\u200e",
    "\u200f",
    "\u202a",
    "\u202b",
    "\u202c",
    "\u202d",
    "\u202e",
    "\u2066",
    "\u2067",
    "\u2068",
    "\u2069",
}


class ValidationError(RuntimeError):
    pass


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def repo_files() -> Iterable[Path]:
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if ".git" in path.parts:
            continue
        # ignore virtualenv artifacts that may exist in local working copies
        if ".venv" in path.parts or "venv" in path.parts:
            continue
        yield path


def is_binary(data: bytes) -> bool:
    return b"\x00" in data


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_simple_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = read_text(path)
    if not text.startswith("---\n"):
        raise ValidationError(f"{rel(path)}: missing opening YAML frontmatter fence")

    closing = text.find("\n---\n", 4)
    if closing == -1:
        raise ValidationError(f"{rel(path)}: missing closing YAML frontmatter fence")

    header = text[4:closing]
    body = text[closing + 5 :].strip()
    if not body:
        raise ValidationError(f"{rel(path)}: missing Markdown body after frontmatter")

    parsed: dict[str, str] = {}
    for line in header.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if ":" not in stripped:
            raise ValidationError(f"{rel(path)}: unsupported frontmatter line {stripped!r}")
        key, value = stripped.split(":", 1)
        parsed[key.strip()] = value.strip().strip('"').strip("'")

    missing = sorted(key for key in FRONTMATTER_REQUIRED if not parsed.get(key))
    if missing:
        raise ValidationError(f"{rel(path)}: missing required frontmatter keys: {', '.join(missing)}")

    return parsed, body


def looks_like_local_path(value: str) -> bool:
    if value.startswith(("http://", "https://", "mailto:", "#")):
        return False
    if value.startswith(("$HOME/", "~/.copilot/")):
        return False
    if "*" in value:
        return False
    if not value.endswith(PATH_SUFFIXES):
        return False
    if " " in value or "\n" in value:
        return False
    return "/" in value or value in {"README.md", "install.md", "compatibility.md", "AGENTS.md"}


def extract_path_references(text: str) -> set[str]:
    refs: set[str] = set()
    patterns = [
        re.compile(r"`([^`\n]+\.(?:md|json))`"),
        re.compile(r"\[[^\]]+\]\(([^)]+)\)"),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            token = match.group(1).strip()
            token = token.split("#", 1)[0].split("?", 1)[0]
            if looks_like_local_path(token):
                refs.add(token)
    return refs


def resolve_local_path(source: Path, ref: str) -> Path:
    candidate = Path(ref)
    if candidate.is_absolute():
        return candidate
    if ref.startswith(("./", "../")):
        return (source.parent / candidate).resolve()
    repo_candidate = (ROOT / candidate).resolve()
    if repo_candidate.exists():
        return repo_candidate
    for docs_dir in ("docs/jack", "docs/jackk"):
        docs_candidate = (ROOT / docs_dir / candidate).resolve()
        if docs_candidate.exists():
            return docs_candidate
    return repo_candidate


def check_json_files(failures: list[str]) -> Any:
    inventory: Any = None
    for path in sorted(ROOT.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            parsed = load_json(path)
        except Exception as exc:
            failures.append(f"{rel(path)}: JSON parse failed: {exc}")
            continue
        if path == INVENTORY_PATH:
            inventory = parsed
    return inventory


def check_frontmatter_files(failures: list[str]) -> None:
    skill_paths = sorted((ROOT / ".github/skills").glob("*/SKILL.md"))
    agent_paths = sorted((ROOT / ".github/agents").glob("*.agent.md"))
    for path in [*skill_paths, *agent_paths]:
        try:
            parse_simple_frontmatter(path)
        except ValidationError as exc:
            failures.append(str(exc))


def check_inventory(inventory: Any, failures: list[str]) -> None:
    if not isinstance(inventory, dict):
        failures.append("docs/jack/inventory.json: did not parse into a JSON object")
        return

    anchor_files = inventory.get("anchor_files", {})
    if not isinstance(anchor_files, dict):
        failures.append("docs/jack/inventory.json: anchor_files must be an object")
    else:
        for name, value in sorted(anchor_files.items()):
            if not isinstance(value, str):
                failures.append(f"docs/jack/inventory.json: anchor_files.{name} must be a string")
                continue
            if not (ROOT / value).exists():
                failures.append(f"docs/jack/inventory.json: anchor file missing: {value}")

    patterns = inventory.get("patterns", {})
    if not isinstance(patterns, dict):
        failures.append("docs/jack/inventory.json: patterns must be an object")
    else:
        for name, values in sorted(patterns.items()):
            if not isinstance(values, list):
                failures.append(f"docs/jack/inventory.json: patterns.{name} must be an array")
                continue
            for pattern in values:
                if not isinstance(pattern, str):
                    failures.append(f"docs/jack/inventory.json: patterns.{name} contains a non-string entry")
                    continue
                matches = [path for path in ROOT.glob(pattern) if path.exists()]
                if not matches:
                    failures.append(f"docs/jack/inventory.json: pattern matched no files: {pattern}")


def check_path_references(inventory: Any, failures: list[str]) -> None:
    if not isinstance(inventory, dict):
        return

    validation_targets = inventory.get("validation_targets", {})
    if not isinstance(validation_targets, dict):
        failures.append("docs/jack/inventory.json: validation_targets must be an object")
        return

    doc_targets = validation_targets.get("path_reference_docs", [])
    json_patterns = validation_targets.get("path_reference_json_patterns", [])

    if not isinstance(doc_targets, list):
        failures.append("docs/jack/inventory.json: validation_targets.path_reference_docs must be an array")
        doc_targets = []
    if not isinstance(json_patterns, list):
        failures.append("docs/jack/inventory.json: validation_targets.path_reference_json_patterns must be an array")
        json_patterns = []

    targets: list[Path] = []
    for doc in doc_targets:
        if not isinstance(doc, str):
            failures.append("docs/jack/inventory.json: validation target doc entries must be strings")
            continue
        path = ROOT / doc
        if not path.exists():
            failures.append(f"docs/jack/inventory.json: validation target missing: {doc}")
            continue
        targets.append(path)

    for pattern in json_patterns:
        if not isinstance(pattern, str):
            failures.append("docs/jack/inventory.json: validation target JSON patterns must be strings")
            continue
        matched = list(ROOT.glob(pattern))
        if not matched:
            failures.append(f"docs/jack/inventory.json: validation target JSON pattern matched no files: {pattern}")
            continue
        targets.extend(sorted(path for path in matched if path.is_file()))

    for path in sorted({target.resolve() for target in targets}):
        text = read_text(path)
        for ref in sorted(extract_path_references(text)):
            resolved = resolve_local_path(path, ref)
            if not resolved.exists():
                failures.append(f"{rel(path)}: broken local reference: {ref}")


def check_stale_paths(failures: list[str]) -> None:
    for path in repo_files():
        try:
            data = path.read_bytes()
        except Exception as exc:
            failures.append(f"{rel(path)}: could not read file: {exc}")
            continue
        if is_binary(data):
            continue
        text = data.decode("utf-8")
        for sentinel in STALE_PATH_SENTINELS:
            if sentinel in text:
                failures.append(f"{rel(path)}: stale {sentinel} path reference found")


def check_text_hygiene(failures: list[str]) -> None:
    for path in repo_files():
        try:
            data = path.read_bytes()
        except Exception as exc:
            failures.append(f"{rel(path)}: could not read file: {exc}")
            continue
        if is_binary(data):
            continue
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError as exc:
            failures.append(f"{rel(path)}: not valid UTF-8 text: {exc}")
            continue

        if "\r" in text:
            failures.append(f"{rel(path)}: non-LF line ending detected")

        bad_chars = sorted({char for char in text if char in INVISIBLE_CHARS})
        if bad_chars:
            encoded = ", ".join(f"U+{ord(char):04X}" for char in bad_chars)
            failures.append(f"{rel(path)}: hidden or bidirectional Unicode character(s): {encoded}")


def check_hook_contract_keys(warnings: list[str]) -> None:
    """Warn (non-fatal) when hook contract files use inconsistent top-level keys.

    This is intentionally non-fatal: it surfaces drift without failing CI.
    """
    contract_paths = sorted(ROOT.glob("docs/jack/hook-contracts/*/hook.json"))
    if not contract_paths:
        return

    # Classify contracts into schema families by the presence of distinctive keys.
    # Family detection rules are intentionally small and conservative.
    families: dict[str, dict[Path, set[str]]] = {}

    def detect_family(keys: set[str]) -> str:
        # Event-style contracts (emit observational events): use 'event', 'intent', 'fires_on',
        # 'advisory_conditions', 'deny_conditions', 'emits', 'notes'.
        if any(k in keys for k in ("event", "intent", "fires_on", "advisory_conditions", "deny_conditions", "emits", "notes")):
            return "event-style"
        # Trigger-style contracts (preflight/inspection): use 'trigger', 'inspects', 'warns_on',
        # 'blocks_on', 'emitted_events', 'fallback_behavior', 'remediation'.
        if any(k in keys for k in ("trigger", "inspects", "warns_on", "blocks_on", "emitted_events", "fallback_behavior", "remediation")):
            return "trigger-style"
        return "unknown"

    for path in contract_paths:
        try:
            parsed = load_json(path)
        except Exception as exc:
            warnings.append(f"{rel(path)}: JSON parse failed: {exc}")
            continue
        if not isinstance(parsed, dict):
            warnings.append(f"{rel(path)}: top-level JSON value is not an object")
            continue
        keys = set(parsed.keys())
        family = detect_family(keys)
        families.setdefault(family, {})[path] = keys

    # For each detected family, verify per-contract consistency within that family only.
    for family, members in sorted(families.items()):
        if not members:
            continue
        if family == "unknown":
            # Warn about unknown family to attract attention (non-fatal)
            for path in members:
                warnings.append(f"{rel(path)}: could not assign a known hook-contract schema family; keys={sorted(members[path])}")
            continue
        union_keys = set().union(*members.values())
        for path, keys in sorted(members.items()):
            if keys != union_keys:
                missing = sorted(union_keys - keys)
                extra = sorted(keys - union_keys)
                if missing or extra:
                    warnings.append(f"{rel(path)}: missing={missing} extra={extra}")

    # Keep the historical mixed 'name' vs 'hook_name' check (still relevant across families).
    seen = set()
    for members in families.values():
        for keys in members.values():
            if "name" in keys:
                seen.add("name")
            if "hook_name" in keys:
                seen.add("hook_name")
    if len(seen) == 2:
        warnings.append("docs/jack/hook-contracts: mixed use of 'name' and 'hook_name' found; prefer 'name' consistently")


def main() -> int:
    failures: list[str] = []

    inventory = check_json_files(failures)
    check_frontmatter_files(failures)
    check_inventory(inventory, failures)
    check_path_references(inventory, failures)
    check_stale_paths(failures)
    check_text_hygiene(failures)

    warnings: list[str] = []
    check_hook_contract_keys(warnings)
    if warnings:
        print("JACK repository validation warnings:")
        for w in warnings:
            print(f"- {w}")

    if failures:
        print("JACK repository validation failed:")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("JACK repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())


