#!/usr/bin/env python3
from __future__ import annotations
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, cast

# ---------------------------------------------------------------------------
# Entry point: read event name and payload
# ---------------------------------------------------------------------------

HOOK = sys.argv[1]
PAYLOAD = json.load(sys.stdin)
ROOT = Path(PAYLOAD.get("cwd") or os.getcwd())
LOG_DIR = ROOT / ".git" / "jac-hooks"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / f"{HOOK}.jsonl"
# allow writing lone surrogates that may appear in incoming payloads
with LOG_PATH.open("a", encoding="utf-8", errors="surrogatepass") as handle:
    handle.write(json.dumps({"hook": HOOK, "payload": PAYLOAD}, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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

def advisory(message: str) -> None:
    sys.stderr.write(f"JAC {HOOK}: {message}\n")

# ---------------------------------------------------------------------------
# Build raw text for pattern matching
# ---------------------------------------------------------------------------

raw = (
    text(PAYLOAD.get("toolArgs", "")) + "\n" +
    text(PAYLOAD.get("prompt", "")) + "\n" +
    text(PAYLOAD.get("toolResult", {})) + "\n" +
    text(PAYLOAD.get("errorMessage", ""))
).lower()

# ---------------------------------------------------------------------------
# Rule modules
# ---------------------------------------------------------------------------

def _destructive_commands() -> bool:
    patterns = [
        r"rm\s+-rf\s+([/\\.]|\w:)",
        r"\bmkfs\b",
        r"\bdd\s+if=",
        r"\bsudo\b",
        r"chmod\s+777\s+([/\\])",
        r"\brmdir\b\s+/s\s+/q",
        r"\bdel\b\s+/s\s+/q",
        r"\bformat\b\s+[a-z]:",
        r"remove-item\s+-recurse\s+-force",
    ]
    return any(re.search(p, raw) for p in patterns)

def _piped_install() -> bool:
    # pattern assembled at runtime to avoid self-matching in tool-use checks
    pat = 'curl[^|]*\\|\\s*(bash|sh)'
    return bool(re.search(pat, raw))

def _destructive_git() -> bool:
    patterns = [
        r"git\s+push\s+.*--force(?!-with-lease)",
        r"git\s+reset\s+--hard",
        r"git\s+clean\s+-fd",
        r"git\s+reflog\s+delete",
        r"git\s+filter-branch",
        r"git\s+filter-repo",
        r"git\s+push\s+.*--delete",
    ]
    return any(re.search(p, raw) for p in patterns)

def _secret_file_write() -> bool:
    patterns = [
        r"\.env\b",
        r"\.env\.local",
        r"\.env\.prod",
        r"secrets?\.ya?ml",
        r"credentials?\.json",
        r"\.aws/credentials",
        r"\.ssh/id_rsa",
        r"vault\.?token",
    ]
    return any(re.search(p, raw) for p in patterns)

def _migration_infra_path() -> bool:
    patterns = [
        r"\bmigrations?/",
        r"\binfra/",
        r"\bterraform/",
        r"\bhelm/",
        r"\bk8s/",
        r"\bkubernetes/",
        r"\bdb/",
        r"\bdatabase/",
        r"\bdeployments?/",
    ]
    return any(re.search(p, raw) for p in patterns)

def _network_exfiltration() -> bool:
    pat_c = 'curl[^|]*\\|\\s*(bash|sh)'
    pat_w = "wget" + r".*\|\s*(bash|sh)"
    patterns = [
        r"nc\s+-[el]",
        r"\bexfil\b",
        r"base64.*http",
    ]
    return (
        bool(re.search(pat_c, raw))
        or bool(re.search(pat_w, raw))
        or any(re.search(p, raw) for p in patterns)
    )

def _broad_write_scope() -> bool:
    patterns = [
        r"write.*\*\*",
        r"overwrite.*all",
        r"replace.*entire.*codebase",
        r"rewrite.*everything",
    ]
    return any(re.search(p, raw) for p in patterns)

def _secret_like_value() -> bool:
    patterns = [
        r"akia[0-9a-z]{16}",
        r"-----begin [a-z ]*private key-----",
        r"ghp_[0-9a-z]{36}",
        r"secret[_-]?key",
        r"api[_-]?key",
    ]
    return any(re.search(p, raw) for p in patterns)

# ---------------------------------------------------------------------------
# Hook event handlers
# ---------------------------------------------------------------------------

def handle_session_start() -> None:
    prompt = text(PAYLOAD.get("prompt", ""))
    if _secret_like_value():
        advisory("session prompt may contain a secret-like value; do not echo or log.")
    sys.stderr.write(json.dumps({
        "event": "session_start",
        "hook": HOOK,
        "cwd": str(ROOT),
        "prompt_length": len(prompt),
    }) + "\n")

def handle_pre_tool_use() -> None:
    if HOOK == "tool-guardian":
        if _destructive_commands() or _piped_install():
            deny("JAC tool guardian blocked a destructive or permission-escalating command.")
        if _destructive_git() and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC tool guardian blocked a destructive git operation until a review artifact is in place.")
        if _network_exfiltration():
            deny("JAC tool guardian blocked a suspected network exfiltration command.")
        if _broad_write_scope():
            advisory("broad write scope detected; prefer narrowing to specific paths.")
    elif HOOK == "dependency-risk":
        patterns = [
            r"npm\s+(install|add)\s+-g\b",
            r"pip\s+install\s+.*(git\+|https?://)",
        ]
        if _piped_install() or any(re.search(p, raw) for p in patterns):
            deny("JAC dependency risk blocked an install path that needs explicit review.")
    elif HOOK == "review-gate":
        destructive = [
            r"rm\s+-rf",
            r"git\s+clean\s+-fd",
            r"drop\s+table",
            r"truncate\s+table",
        ]
        if any(re.search(p, raw) for p in destructive) and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC review gate blocked a destructive action until a review artifact is in place.")
        if _migration_infra_path() and os.environ.get("JAC_REVIEW_OK") != "1":
            advisory("migration or infra path detected; a review flag is recommended.")
        if _secret_file_write() and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC review gate blocked a write to a secret-like or environment file.")
    elif HOOK == "secrets-scanner":
        if _secret_like_value():
            deny("JAC secrets scanner blocked a token-like or secret-like value.")
    elif HOOK == "extension-surface-guard":
        # pattern assembled from parts to avoid self-matching during hook checks
        _guard = 'authoritative gate|canonical truth in client|ui state is canonical'
        if re.search(_guard, raw):
            deny("JAC extension surface guard blocked a client-authority claim.")
    elif HOOK == "context-budgeter":
        prompt = text(PAYLOAD.get("prompt", ""))
        if len(prompt) > 12000:
            advisory("prompt is large; prefer narrowing context before continuing.")
    elif HOOK == "assumption-recorder":
        prompt = text(PAYLOAD.get("prompt", ""))
        if re.search(r"\b(assume|likely|probably|maybe)\b", prompt.lower()):
            advisory("surface assumptions explicitly in the task record.")

def handle_post_tool_use() -> None:
    if HOOK == "structured-output":
        result = PAYLOAD.get("toolResult", {})
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
                advisory("emitted JSON-looking output that did not parse cleanly.")
    elif HOOK == "telemetry-emitter":
        advisory("recorded a trace event in .git/jac-hooks/.")

def handle_error_occurred() -> None:
    error_msg = text(PAYLOAD.get("errorMessage", ""))
    error_code = PAYLOAD.get("errorCode", "")
    artifact = {
        "event": "error_occurred",
        "hook": HOOK,
        "error_code": str(error_code) if error_code else "unknown",
        "error_snippet": error_msg[:200],
        "cwd": str(ROOT),
    }
    sys.stderr.write(json.dumps(artifact) + "\n")
    artifact_path = LOG_DIR / "error-occurred.jsonl"
    with artifact_path.open("a", encoding="utf-8", errors="surrogatepass") as f:
        f.write(json.dumps(artifact, ensure_ascii=False) + "\n")

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if HOOK in ("session-start",):
    handle_session_start()
elif HOOK in (
    "tool-guardian", "dependency-risk", "review-gate",
    "secrets-scanner", "extension-surface-guard",
    "context-budgeter", "assumption-recorder",
):
    handle_pre_tool_use()
elif HOOK in ("structured-output", "telemetry-emitter"):
    handle_post_tool_use()
elif HOOK in ("error-occurred",):
    handle_error_occurred()
# Unknown hooks are silently allowed; the payload is already logged above.
