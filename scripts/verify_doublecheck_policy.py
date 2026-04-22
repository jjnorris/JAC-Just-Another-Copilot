#!/usr/bin/env python3
"""Verify the `doublecheck` SKILL.md contains required governance headings.

This is a narrow, non-invasive check intended to validate that the
recent governance additions are present in the repository.

Exit codes:
 - 0: OK (all required phrases found)
 - 1: Missing required phrase(s)
 - 2: SKILL.md not found
"""
import sys
from pathlib import Path

REQ_PHRASES = [
    "evidence trust order",
    "never claim",
    "verified_facts",
    "inferences",
    "unknowns",
    "assumptions",
    "validation_report",
    "anti-theater",
    "reorient trigger",
    "completion gate",
]


def main() -> int:
    p = Path(".github/skills/doublecheck/SKILL.md")
    if not p.exists():
        print("MISSING: .github/skills/doublecheck/SKILL.md", file=sys.stderr)
        return 2
    txt = p.read_text(encoding="utf-8").lower()
    missing = [q for q in REQ_PHRASES if q not in txt]
    if missing:
        print("MISSING PHRASES:")
        for m in missing:
            print(f" - {m}")
        return 1
    print("OK: doublecheck SKILL.md contains required governance headings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
