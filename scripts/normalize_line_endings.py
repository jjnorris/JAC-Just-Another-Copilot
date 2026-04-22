#!/usr/bin/env python3
from pathlib import Path

files = [
    Path("scripts/strip_bom.py"),
    Path("docs/jack/reconciliation_batch4_closeout.md"),
]
for p in files:
    try:
        t = p.read_text(encoding="utf-8")
    except Exception:
        try:
            t = p.read_text(encoding="utf-8-sig")
        except Exception:
            continue
    t = t.replace("\r\n", "\n")
    p.write_text(t, encoding="utf-8", newline="\n")
    print("rewrote", p)
