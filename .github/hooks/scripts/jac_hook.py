#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, cast

HOOK = sys.argv[1]
PAYLOAD = json.load(sys.stdin)
ROOT = Path(PAYLOAD.get("cwd") or os.getcwd())
LOG_DIR = ROOT / ".git" / "jac-hooks"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / f"{HOOK}.jsonl"
# allow writing lone surrogates that may appear in incoming payloads
# use surrogatepass so the UTF-8 encoder will accept surrogate code points
with LOG_PATH.open("a", encoding="utf-8", errors="surrogatepass") as handle:
    handle.write(json.dumps({"hook": HOOK, "payload": PAYLOAD}, ensure_ascii=False) + "\n")

def deny(reason: str) -> None:
    sys.stdout.write(json.dumps({
        "permissionDecision": "deny",
        "permissionDecisionReason": reason,
    }))
    sys.exit(0)

def text(blob: object) -> str:
    if isinstance(blob, str):
        return blob
    return json.dumps(blob, ensure_ascii=False)

raw = (text(PAYLOAD.get("toolArgs", "")) + "\n" + text(PAYLOAD.get("prompt", "")) + "\n" + text(PAYLOAD.get("toolResult", {}))).lower()

if HOOK == "tool-guardian":
    # broaden destructive-command detection to cover common Unix and Windows forms
    patterns = [
        r"rm\s+-rf\s+([/\\.]|\w:)",            # rm -rf / or rm -rf . or rm -rf C:\\
        r"\bmkfs\b",
        r"\bdd\s+if=",
        r"\bsudo\b",
        r"chmod\s+777\s+([/\\])",
        r"curl[^|]*\|\s*(bash|sh)",               # curl ... | bash
        r"\brmdir\b\s+/s\s+/q",
        r"\bdel\b\s+/s\s+/q",
        r"\bformat\b\s+[a-z]:",
        r"remove-item\s+-recurse\s+-force",
    ]
    if any(re.search(p, raw) for p in patterns):
        deny("JAC tool guardian blocked a destructive or permission-escalating command.")
elif HOOK == "dependency-risk":
    patterns = [r"curl[^|]*\|\s*(bash|sh)", r"npm\s+(install|add)\s+-g\b", r"pip\s+install\s+.*(git\+|https?://)"]
    if any(re.search(p, raw) for p in patterns):
        deny("JAC dependency risk blocked an install path that needs explicit review.")
elif HOOK == "review-gate":
    destructive = [r"rm\s+-rf", r"git\s+clean\s+-fd", r"drop\s+table", r"truncate\s+table"]
    if any(re.search(p, raw) for p in destructive) and os.environ.get("JAC_REVIEW_OK") != "1":
        deny("JAC review gate blocked a destructive action until a review artifact is in place.")
elif HOOK == "secrets-scanner":
    patterns = [r"akia[0-9a-z]{16}", r"-----begin [a-z ]*private key-----", r"ghp_[0-9a-z]{36}", r"secret[_-]?key", r"api[_-]?key"]
    if any(re.search(p, raw) for p in patterns):
        deny("JAC secrets scanner blocked a token-like or secret-like value.")
elif HOOK == "extension-surface-guard":
    if re.search(r"authoritative gate|canonical truth in client|ui state is canonical", raw):
        deny("JAC extension surface guard blocked a client-authority claim.")
elif HOOK == "context-budgeter":
    prompt = text(PAYLOAD.get("prompt", ""))
    if len(prompt) > 12000:
        sys.stderr.write("JAC context budgeter: prompt is large; prefer narrowing context before continuing.\n")
elif HOOK == "assumption-recorder":
    prompt = text(PAYLOAD.get("prompt", ""))
    if re.search(r"\b(assume|likely|probably|maybe)\b", prompt.lower()):
        sys.stderr.write("JAC assumption recorder: surface assumptions explicitly in the task record.\n")
elif HOOK == "structured-output":
    result = PAYLOAD.get("toolResult", {})
    # normalize and type-cast to help static analyzers understand dict.get usage
    if isinstance(result, dict):
        result_dict = cast(Dict[str, Any], result)
        text_result = text(result_dict.get("textResultForLlm", ""))
    else:
        text_result = text(result)
    stripped = text_result.strip()
    if stripped.startswith(("{", "[")):
        try:
            json.loads(stripped)
        except Exception:
            sys.stderr.write("JAC structured output: emitted JSON-looking output that did not parse cleanly.\n")
elif HOOK == "telemetry-emitter":
    sys.stderr.write("JAC telemetry emitter: recorded a trace event in .git/jac-hooks/.\n")
