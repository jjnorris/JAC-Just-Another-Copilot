#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTS = {".json", ".jsonl", ".md", ".py", ".yaml", ".yml", ".txt", ".ini", ".cfg"}
processed = []

for p in ROOT.rglob("*"):
    if not p.is_file():
        continue
    if ".git" in p.parts:
        continue
    if p.suffix.lower() not in TEXT_EXTS:
        continue
    try:
        raw = p.read_bytes()
    except Exception:
        continue
    changed = False
    # BOM byte order mark
    if raw.startswith(b"\xef\xbb\xbf"):
        try:
            text = raw.decode("utf-8-sig")
            changed = True
        except Exception:
            try:
                text = raw.decode("utf-8", errors="replace")
                changed = True
            except Exception:
                continue
    else:
        try:
            text = raw.decode("utf-8")
        except Exception:
            try:
                text = raw.decode("utf-8-sig")
                changed = True
            except Exception:
                continue
    if "\ufeff" in text:
        text = text.replace("\ufeff", "")
        changed = True
    if changed:
        try:
            p.write_text(text, encoding="utf-8", newline="\n")
            processed.append(str(p.relative_to(ROOT)))
        except Exception:
            continue

print(f"Stripped BOM from {len(processed)} files")
for f in processed:
    print(f)
