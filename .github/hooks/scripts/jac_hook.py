#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, Iterable, cast

HOOK = sys.argv[1]
PAYLOAD = json.load(sys.stdin)


# ---------------------------------------------------------------------------
# Path and logging helpers
# ---------------------------------------------------------------------------


def _cwd() -> Path:
    raw = PAYLOAD.get("cwd") or os.getcwd()
    return Path(str(raw)).resolve()


CWD = _cwd()


def _resolve_git_dir(start: Path) -> Path:
    current = start
    for candidate in (current, *current.parents):
        dot_git = candidate / ".git"
        if dot_git.is_dir():
            return dot_git
        if dot_git.is_file():
            try:
                first = dot_git.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
            except Exception:
                continue
            if first.startswith("gitdir:"):
                target = first.split(":", 1)[1].strip()
                return (candidate / target).resolve()
    return start / ".git"


GIT_DIR = _resolve_git_dir(CWD)
LOG_DIR = GIT_DIR / "jac-hooks"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / f"{HOOK}.jsonl"


def _append_jsonl(path: Path, payload: Dict[str, Any]) -> None:
    with path.open("a", encoding="utf-8", errors="surrogatepass") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


# allow lone surrogates that may appear in incoming payloads
_append_jsonl(LOG_PATH, {"hook": HOOK, "payload": PAYLOAD})


# ---------------------------------------------------------------------------
# Basic helpers
# ---------------------------------------------------------------------------


def deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        )
    )
    sys.exit(0)


def advisory(message: str) -> None:
    sys.stderr.write(f"JAC {HOOK}: {message}\n")


def text(blob: object) -> str:
    if isinstance(blob, str):
        return blob
    return json.dumps(blob, ensure_ascii=False)


def prompt_text() -> str:
    prompt = PAYLOAD.get("initialPrompt")
    if prompt in (None, ""):
        prompt = PAYLOAD.get("prompt", "")
    return text(prompt)


def error_details() -> Dict[str, Any]:
    error = PAYLOAD.get("error")
    if isinstance(error, dict):
        return cast(Dict[str, Any], error)
    details: Dict[str, Any] = {}
    if "errorMessage" in PAYLOAD:
        details["message"] = PAYLOAD.get("errorMessage", "")
    if "errorCode" in PAYLOAD:
        details["name"] = PAYLOAD.get("errorCode", "")
    return details


def detect_event() -> str:
    if "error" in PAYLOAD or "errorMessage" in PAYLOAD:
        return "errorOccurred"
    if "toolResult" in PAYLOAD:
        return "postToolUse"
    if "toolName" in PAYLOAD or "toolArgs" in PAYLOAD:
        return "preToolUse"
    if "initialPrompt" in PAYLOAD:
        return "sessionStart"
    if "prompt" in PAYLOAD:
        return "userPromptSubmitted"
    return "unknown"


EVENT = detect_event()


def tool_name() -> str:
    return str(PAYLOAD.get("toolName") or "").strip().lower()


def parsed_tool_args() -> Dict[str, Any]:
    raw = PAYLOAD.get("toolArgs", {})
    if isinstance(raw, dict):
        return cast(Dict[str, Any], raw)
    if isinstance(raw, str):
        try:
            loaded = json.loads(raw)
            if isinstance(loaded, dict):
                return cast(Dict[str, Any], loaded)
        except Exception:
            return {"raw": raw}
        return {"raw": raw}
    return {}


TOOL_NAME = tool_name()
TOOL_ARGS = parsed_tool_args()

SHELL_TOOLS = {"bash", "shell", "sh", "powershell", "terminal"}
WRITE_TOOLS = {"edit", "write", "create", "replace"}


def shell_command() -> str:
    if TOOL_NAME not in SHELL_TOOLS:
        return ""
    for key in ("command", "cmd", "script", "raw"):
        value = TOOL_ARGS.get(key)
        if isinstance(value, str):
            return value
    return text(PAYLOAD.get("toolArgs", ""))


def candidate_paths() -> Iterable[str]:
    keys = ("path", "paths", "file", "files", "target", "targets")
    for key in keys:
        value = TOOL_ARGS.get(key)
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, str):
                    yield item


def raw_for_pattern_matching() -> str:
    parts = [
        prompt_text(),
        text(PAYLOAD.get("toolResult", {})),
        text(error_details().get("message", "")),
        text(error_details().get("name", "")),
    ]
    if TOOL_NAME in SHELL_TOOLS:
        parts.append(shell_command())
    else:
        parts.append(text(TOOL_ARGS))
    return "\n".join(parts).lower()


RAW = raw_for_pattern_matching()


# ---------------------------------------------------------------------------
# Pattern helpers
# ---------------------------------------------------------------------------


def _matches_any(text_value: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text_value, flags=re.IGNORECASE) for pattern in patterns)


def _destructive_shell() -> bool:
    command = shell_command()
    if not command:
        return False
    patterns = [
        r"rm\s+-rf\b",
        r"\bmkfs\b",
        r"\bdd\s+if=",
        r"\bsudo\b",
        r"\brmdir\b\s+/s\s+/q",
        r"\bdel\b\s+/s\s+/q",
        r"\bformat\b\s+[a-z]:",
        r"remove-item\s+-recurse\s+-force",
    ]
    return _matches_any(command, patterns)


def _piped_install() -> bool:
    command = shell_command()
    if not command:
        return False
    patterns = [
        r"curl[^|]*\|\s*(bash|sh)",
        r"wget[^|]*\|\s*(bash|sh)",
    ]
    return _matches_any(command, patterns)


def _destructive_git() -> bool:
    command = shell_command()
    if not command:
        return False
    patterns = [
        r"git\s+push\s+.*--force(?!-with-lease)",
        r"git\s+reset\s+--hard",
        r"git\s+clean\s+-fd",
        r"git\s+reflog\s+delete",
        r"git\s+filter-branch",
        r"git\s+filter-repo",
        r"git\s+push\s+.*--delete",
    ]
    return _matches_any(command, patterns)


def _network_exfiltration() -> bool:
    command = shell_command()
    if not command:
        return False
    patterns = [
        r"\bscp\b",
        r"\brsync\b.*@",
        r"curl\s+-T\b",
        r"nc\s+-[el]",
        r"base64.*http",
    ]
    return _matches_any(command, patterns) or _piped_install()


def _broad_write_scope() -> bool:
    if TOOL_NAME in SHELL_TOOLS:
        return _matches_any(
            shell_command(),
            [
                r"rewrite.*everything",
                r"replace.*entire.*codebase",
                r"overwrite.*all",
            ],
        )
    return _matches_any(
        text(TOOL_ARGS),
        [
            r"\*\*",
            r'"paths"\s*:\s*\[.*\*',
            r'"targets"\s*:\s*\[.*\*',
        ],
    )


def _secret_like_value() -> bool:
    patterns = [
        r"akia[0-9a-z]{16}",
        r"-----begin [a-z ]*private key-----",
        r"ghp_[0-9a-z]{36}",
        r"secret[_-]?key",
        r"api[_-]?key",
        r"xox[baprs]-",
    ]
    return _matches_any(RAW, patterns)


def _secret_path_write() -> bool:
    if TOOL_NAME not in WRITE_TOOLS:
        return False
    patterns = [
        r"\.env\b",
        r"\.env\.local\b",
        r"\.env\.prod\b",
        r"secrets?\.ya?ml\b",
        r"credentials?\.json\b",
        r"\.aws/credentials\b",
        r"\.ssh/id_rsa\b",
        r"token\b",
        r"private[-_]?key\b",
    ]
    return any(_matches_any(path, patterns) for path in candidate_paths())


def _infra_or_migration_path() -> bool:
    patterns = [
        r"(^|/)(migrations?|infra|terraform|helm|k8s|kubernetes|db|database|deployments?)(/|$)",
    ]
    return any(_matches_any(path, patterns) for path in candidate_paths())


def _client_authority_claim() -> bool:
    return _matches_any(
        RAW,
        [
            r"authoritative gate",
            r"canonical truth in client",
            r"ui state is canonical",
        ],
    )


# ---------------------------------------------------------------------------
# Hook handlers
# ---------------------------------------------------------------------------


def handle_session_start() -> None:
    prompt = prompt_text()
    if _secret_like_value():
        advisory("initial session prompt may contain a secret-like value; do not echo or log.")
    sys.stderr.write(
        json.dumps(
            {
                "event": "session_start",
                "hook": HOOK,
                "detectedEvent": EVENT,
                "cwd": str(CWD),
                "gitDir": str(GIT_DIR),
                "prompt_length": len(prompt),
            }
        )
        + "\n"
    )


def handle_pre_tool_use() -> None:
    if HOOK == "tool-guardian":
        if _destructive_shell() or _piped_install():
            deny("JAC tool guardian blocked a destructive or permission-escalating shell command.")
        if _destructive_git() and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC tool guardian blocked a destructive git operation until a review artifact is in place.")
        if _network_exfiltration():
            deny("JAC tool guardian blocked a suspected network exfiltration command.")
        if _broad_write_scope():
            advisory("broad write scope detected; prefer narrowing to specific paths.")

    elif HOOK == "dependency-risk":
        if TOOL_NAME in SHELL_TOOLS and _matches_any(
            shell_command(),
            [
                r"npm\s+(install|add)\s+-g\b",
                r"pip\s+install\s+.*(git\+|https?://)",
                r"pnpm\s+add\s+-g\b",
                r"yarn\s+global\s+add\b",
            ],
        ):
            deny("JAC dependency risk blocked an install path that needs explicit review.")
        if _piped_install():
            deny("JAC dependency risk blocked a piped install path that needs explicit review.")

    elif HOOK == "review-gate":
        if _destructive_shell() and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC review gate blocked a destructive action until a review artifact is in place.")
        if _infra_or_migration_path() and os.environ.get("JAC_REVIEW_OK") != "1":
            advisory("migration or infra path detected; a review flag is recommended.")
        if _secret_path_write() and os.environ.get("JAC_REVIEW_OK") != "1":
            deny("JAC review gate blocked a write to a secret-like or environment file.")

    elif HOOK == "secrets-scanner":
        if _secret_like_value() or _secret_path_write():
            deny("JAC secrets scanner blocked a token-like value or a secret-like target path.")

    elif HOOK == "extension-surface-guard":
        if _client_authority_claim():
            deny("JAC extension surface guard blocked a client-authority claim.")

    elif HOOK == "context-budgeter":
        prompt = prompt_text()
        if len(prompt) > 12000:
            advisory("prompt is large; prefer narrowing context before continuing.")

    elif HOOK == "assumption-recorder":
        prompt = prompt_text()
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
        advisory(f"recorded a trace event for {EVENT} in .git/jac-hooks/.")


def handle_error_occurred() -> None:
    error = error_details()
    error_msg = text(error.get("message", ""))
    error_name = error.get("name", "")
    artifact = {
        "event": "error_occurred",
        "hook": HOOK,
        "error_name": str(error_name) if error_name else "unknown",
        "error_snippet": error_msg[:200],
        "cwd": str(CWD),
    }
    sys.stderr.write(json.dumps(artifact) + "\n")
    _append_jsonl(LOG_DIR / "error-occurred.jsonl", artifact)


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

if HOOK == "session-start":
    handle_session_start()
elif HOOK in {
    "tool-guardian",
    "dependency-risk",
    "review-gate",
    "secrets-scanner",
    "extension-surface-guard",
    "context-budgeter",
    "assumption-recorder",
}:
    handle_pre_tool_use()
elif HOOK in {"structured-output", "telemetry-emitter"}:
    handle_post_tool_use()
elif HOOK == "error-occurred":
    handle_error_occurred()
# Unknown hooks are allowed silently; the payload is already logged above.
