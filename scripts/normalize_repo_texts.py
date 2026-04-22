#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INVISIBLE = {
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

processed = []
for p in ROOT.rglob("*"):
    try:
        if not p.is_file():
            continue
        if ".git" in p.parts:
            continue
        if ".venv" in p.parts or "venv" in p.parts:
            continue
        raw = p.read_bytes()
    except Exception:
        continue
    if b"\x00" in raw:
        continue
    try:
        text = raw.decode("utf-8-sig")
    except Exception:
        try:
            text = raw.decode("utf-8")
        except Exception:
            try:
                text = raw.decode("latin-1")
            except Exception:
                continue
    new = text.replace("\r\n", "\n").replace("\r", "\n")
    for ch in INVISIBLE:
        if ch in new:
            new = new.replace(ch, "")
    if new != text:
        try:
            p.write_text(new, encoding="utf-8", newline="\n")
            processed.append(str(p.relative_to(ROOT)))
        except Exception:
            continue

print(f"Normalized {len(processed)} files")
for f in processed:
    print(f)
