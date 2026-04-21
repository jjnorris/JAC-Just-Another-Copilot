from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
import urllib.error
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Iterator, cast

from jac_hook_support import HookLogger


SHELL_TOOLS = {"bash", "shell", "sh", "powershell", "terminal"}
WRITE_TOOLS = {"edit", "write", "create", "replace"}
COMMAND_KEYS = ("command", "cmd", "script", "raw")
RESULT_TEXT_KEYS = ("textResultForLlm", "stdout", "stderr", "output", "text")
PATH_KEY_TOKENS = (
    "path",
    "file",
    "target",
    "destination",
    "source",
    "from",
    "to",
)
CLIENT_TRUTH_PATTERNS = (
    "".join((r"authoritative ", r"gate")),
    "".join((r"canonical ", r"truth in client")),
    "".join((r"ui state is ", r"canonical")),
)


@dataclass
class HookContext:
    hook: str
    payload: Dict[str, Any]
    cwd: Path
    git_dir: Path | None
    logger: HookLogger
    event: str
    prompt: str
    tool_name: str
    tool_args: Dict[str, Any]
    shell_command: str
    candidate_paths: tuple[str, ...]
    raw_text: str


def stringify(blob: object) -> str:
    if isinstance(blob, str):
        return blob
    return json.dumps(blob, ensure_ascii=False)


def prompt_text(payload: Dict[str, Any]) -> str:
    prompt = payload.get("initialPrompt")
    if prompt in (None, ""):
        prompt = payload.get("prompt")
    if prompt in (None, ""):
        prompt = payload.get("userPrompt")
    return stringify(prompt or "")


def error_details(payload: Dict[str, Any]) -> Dict[str, Any]:
    error = payload.get("error")
    if isinstance(error, dict):
        return cast(Dict[str, Any], error)

    details: Dict[str, Any] = {}
    if "errorMessage" in payload:
        details["message"] = payload.get("errorMessage", "")
    if "errorCode" in payload:
        details["name"] = payload.get("errorCode", "")
    return details


def detect_event(payload: Dict[str, Any]) -> str:
    for key in ("eventName", "hookEventName"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    if "error" in payload or "errorMessage" in payload:
        return "errorOccurred"
    if "toolResult" in payload:
        return "postToolUse"
    if "toolName" in payload or "toolArgs" in payload:
        return "preToolUse"
    if "initialPrompt" in payload:
        return "sessionStart"
    if "prompt" in payload:
        return "userPromptSubmitted"
    return "unknown"


def normalized_tool_name(payload: Dict[str, Any]) -> str:
    name = payload.get("toolName")
    if not isinstance(name, str):
        return ""
    return name.strip().lower()


def parsed_tool_args(payload: Dict[str, Any]) -> Dict[str, Any]:
    raw = payload.get("toolArgs", {})
    if isinstance(raw, dict):
        return cast(Dict[str, Any], raw)
    if isinstance(raw, str):
        try:
            loaded = json.loads(raw)
        except Exception:
            return {"raw": raw}
        if isinstance(loaded, dict):
            return cast(Dict[str, Any], loaded)
        return {"raw": raw, "parsed": loaded}
    return {}


def shell_command(tool_name: str, tool_args: Dict[str, Any], payload: Dict[str, Any]) -> str:
    if tool_name not in SHELL_TOOLS:
        return ""
    for key in COMMAND_KEYS:
        value = tool_args.get(key)
        if isinstance(value, str):
            return value
    direct = payload.get("command")
    if isinstance(direct, str):
        return direct
    return stringify(payload.get("toolArgs", ""))


def iter_named_values(value: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, item in value.items():
            if isinstance(key, str):
                yield key, item
                yield from iter_named_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from iter_named_values(item)


def collect_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from collect_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from collect_strings(item)


def normalize_path(value: str) -> str:
    s = value.strip().strip("'\"")
    # Convert Windows backslashes to forward slashes for consistent matching
    s = s.replace('\\\\', '/').replace('\\', '/')
    # Collapse repeated slashes
    s = re.sub(r"/+", "/", s)
    # Remove trailing slash except for drive roots like 'C:/'
    if len(s) > 3 and s.endswith("/"):
        s = s.rstrip("/")
    return s


def regex_candidate_paths(text: str) -> Iterator[str]:
    # Match Windows drive-letter absolute paths like C:\\path\\to\\file
    for match in re.finditer(r"[A-Za-z]:\\\\(?:[^\\\\\n]+(?:\\\\[^\\\\\n]+)*)", text):
        yield normalize_path(match.group(0))
    # Match posix-like or backslash-separated paths with multiple segments
    for match in re.finditer(r"([A-Za-z0-9_.\s-]+(?:[\\/][A-Za-z0-9_.\s-]+)+)", text):
        yield normalize_path(match.group(1))


def candidate_paths(tool_name: str, tool_args: Dict[str, Any], command: str) -> tuple[str, ...]:
    found: list[str] = []
    seen: set[str] = set()

    for key, value in iter_named_values(tool_args):
        lower = key.lower()
        if not any(token in lower for token in PATH_KEY_TOKENS):
            continue
        for item in collect_strings(value):
            normalized = normalize_path(item)
            if normalized and normalized not in seen:
                seen.add(normalized)
                found.append(normalized)

    if not found and tool_name in WRITE_TOOLS:
        for item in regex_candidate_paths(stringify(tool_args)):
            if item not in seen:
                seen.add(item)
                found.append(item)

    if tool_name in SHELL_TOOLS:
        for item in regex_candidate_paths(command):
            if item not in seen:
                seen.add(item)
                found.append(item)

    return tuple(found)


def aggregate_text(
    payload: Dict[str, Any],
    prompt: str,
    tool_args: Dict[str, Any],
    command: str,
) -> str:
    parts = [
        prompt,
        stringify(payload.get("toolResult", {})),
        stringify(error_details(payload).get("message", "")),
        stringify(error_details(payload).get("name", "")),
        command or stringify(tool_args),
    ]
    return "\n".join(parts).lower()


def build_context(
    hook: str,
    payload: Dict[str, Any],
    cwd: Path,
    git_dir: Path | None,
    logger: HookLogger,
) -> HookContext:
    tool = normalized_tool_name(payload)
    args = parsed_tool_args(payload)
    command = shell_command(tool, args, payload)
    prompt = prompt_text(payload)
    return HookContext(
        hook=hook,
        payload=payload,
        cwd=cwd,
        git_dir=git_dir,
        logger=logger,
        event=detect_event(payload),
        prompt=prompt,
        tool_name=tool,
        tool_args=args,
        shell_command=command,
        candidate_paths=candidate_paths(tool, args, command),
        raw_text=aggregate_text(payload, prompt, args, command),
    )


def deny(reason: str) -> None:
    sys.stdout.write(
        json.dumps(
            {
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        )
    )
    raise SystemExit(0)


def matches_any(text_value: str, patterns: Iterable[str]) -> bool:
    return any(re.search(pattern, text_value, flags=re.IGNORECASE) for pattern in patterns)


def destructive_shell(ctx: HookContext) -> bool:
    if not ctx.shell_command:
        return False
    return matches_any(
        ctx.shell_command,
        [
            r"rm\s+-rf\b",
            r"\bmkfs\b",
            r"\bdd\s+if=",
            r"\bsudo\b",
            r"\brmdir\b\s+/s\s+/q",
            r"\bdel\b\s+/s\s+/q",
            r"\bformat\b\s+[a-z]:",
            r"remove-item\s+-recurse\s+-force",
        ],
    )


def piped_install(ctx: HookContext) -> bool:
    if not ctx.shell_command:
        return False
    return matches_any(
        ctx.shell_command,
        [
            r"curl[^|]*\|\s*(bash|sh)",
            r"wget[^|]*\|\s*(bash|sh)",
        ],
    )


def destructive_git(ctx: HookContext) -> bool:
    if not ctx.shell_command:
        return False
    return matches_any(
        ctx.shell_command,
        [
            r"git\s+push\s+.*--force(?!-with-lease)",
            r"git\s+reset\s+--hard",
            r"git\s+clean\s+-fd",
            r"git\s+reflog\s+delete",
            r"git\s+filter-branch",
            r"git\s+filter-repo",
            r"git\s+push\s+.*--delete",
        ],
    )


def network_exfiltration(ctx: HookContext) -> bool:
    if not ctx.shell_command:
        return False
    return piped_install(ctx) or matches_any(
        ctx.shell_command,
        [
            r"\bscp\b",
            r"\brsync\b.*@",
            r"curl\s+-T\b",
            r"nc\s+-[el]",
            r"base64.*http",
        ],
    )


def broad_write_scope(ctx: HookContext) -> bool:
    if ctx.tool_name in SHELL_TOOLS:
        return matches_any(
            ctx.shell_command,
            [
                r"rewrite.*everything",
                r"replace.*entire.*codebase",
                r"overwrite.*all",
            ],
        )
    if len(ctx.candidate_paths) > 25:
        return True
    if any(path in {"*", "**", ".", "./"} or "*" in path for path in ctx.candidate_paths):
        return True
    return matches_any(
        stringify(ctx.tool_args),
        [
            r'"paths"\s*:\s*\[.*\*',
            r'"targets"\s*:\s*\[.*\*',
        ],
    )


def secret_like_value(ctx: HookContext) -> bool:
    # Allow override via JACK_SECRET_PATTERNS env var (comma-separated regexes)
    env = os.environ.get("JACK_SECRET_PATTERNS")
    if env:
        patterns = [p.strip() for p in env.split(",") if p.strip()]
    else:
        patterns = [
            r"akia[0-9a-z]{16}",
            r"-----begin [a-z ]*private key-----",
            r"ghp_[0-9a-z]{36}",
            r"secret[_-]?key",
            r"api[_-]?key",
            r"xox[baprs]-",
        ]
    return matches_any(ctx.raw_text, patterns)


def secret_path_write(ctx: HookContext) -> bool:
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
    return any(matches_any(path, patterns) for path in ctx.candidate_paths)


def shell_secret_write(ctx: HookContext) -> bool:
    if not ctx.shell_command:
        return False
    return matches_any(
        ctx.shell_command,
        [
            r">\s*[^ \n]*(?:\.env|credentials\.json|secrets?\.ya?ml)\b",
            r"tee\s+[^ \n]*(?:\.env|credentials\.json|secrets?\.ya?ml)\b",
        ],
    )


def infra_or_migration_path(ctx: HookContext) -> bool:
    patterns = [
        r"(^|/)(migrations?|infra|terraform|helm|k8s|kubernetes|db|database|deployments?)(/|$)",
    ]
    return any(matches_any(path, patterns) for path in ctx.candidate_paths) or matches_any(
        ctx.shell_command,
        patterns,
    )


def client_truth_claim(ctx: HookContext) -> bool:
    return matches_any(ctx.raw_text, CLIENT_TRUTH_PATTERNS)


def parse_structured_output(ctx: HookContext) -> bool:
    result = ctx.payload.get("toolResult", {})
    snippets: list[str] = []
    if isinstance(result, dict):
        result_dict = cast(Dict[str, Any], result)
        for key in RESULT_TEXT_KEYS:
            value = result_dict.get(key)
            if isinstance(value, str):
                snippets.append(value)
    elif isinstance(result, str):
        snippets.append(result)
    else:
        snippets.append(stringify(result))

    for snippet in snippets:
        stripped = snippet.strip()
        if not stripped.startswith(("{", "[")):
            continue
        try:
            json.loads(stripped)
        except Exception:
            return False
    return True


def _verify_github_run(repo: str, run_id: int, token: str) -> bool:
    """Verify a GitHub Actions workflow run is successful using the API.

    Returns True when the run exists and its conclusion is 'success'.
    This is a best-effort check and will silently fail if the network or token
    are not available.
    """
    if not repo or not run_id or not token:
        return False
    try:
        url = f"https://api.github.com/repos/{repo}/actions/runs/{int(run_id)}"
        req = urllib.request.Request(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github+json", "User-Agent": "JACK-hook"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            payload = json.load(resp)
        conclusion = payload.get("conclusion")
        return conclusion == "success"
    except Exception:
        return False


def has_review_approval(ctx: HookContext) -> bool:
    """
    Detect a repository-local review approval artifact.
    Supports the standard '.git/jack-hooks' artifact directory as well as repo-level
    'jack/' (and legacy 'jac/') directories and fallback files.

    To reduce spoofing risk, prefer server-side verification when a GitHub Actions
    run_id and provider are present — this attempts to verify the workflow run
    via the GitHub API when a GITHUB_TOKEN and GITHUB_REPOSITORY are available.
    Otherwise the function falls back to presence of provenance keys.
    """
    provenance_keys = (
        "workflow",
        "run_id",
        "provider",
        "approval_signature",
        "signed_by",
        "pr_number",
        "ci_provider",
        "run_url",
        "source",
    )

    try:
        if ctx.git_dir:
            for hooks_name in ("jack-hooks",):
                hooks_dir = ctx.git_dir / hooks_name
                if not hooks_dir.exists():
                    continue
                # Check common artifact names for approval markers
                for name in ("review-approved.jsonl", "review-gate.jsonl", "review_ok.jsonl"):
                    candidate = hooks_dir / name
                    if not candidate.exists():
                        continue
                    try:
                        for line in candidate.read_text(encoding="utf-8").splitlines():
                            try:
                                data = json.loads(line)
                            except Exception:
                                continue
                            if not isinstance(data, dict):
                                continue
                            if data.get("approved") is not True:
                                continue

                            # If the artifact claims a GitHub provider and includes a run_id,
                            # require server-side verification: a run_id without a verifiable
                            # successful GitHub Actions run is not accepted as a bypass.
                            provider = str(data.get("provider", "")).lower()
                            run_id = data.get("run_id")
                            if provider in ("github", "github-actions", "github.com") and run_id:
                                repo_name = os.environ.get("GITHUB_REPOSITORY") or data.get("repo")
                                token = os.environ.get("GITHUB_TOKEN")
                                # Strict policy: only accept a GitHub-run approval when we can
                                # verify the run succeeded server-side with a token for this repo.
                                if repo_name and token:
                                    try:
                                        if _verify_github_run(repo_name, int(run_id), token):
                                            return True
                                    except Exception:
                                        pass
                                # If we cannot verify the claimed GitHub run, do NOT accept this artifact.
                                # Continue to the next artifact instead of falling back to weaker provenance.
                                continue

                            # Fallback acceptance when any provenance key is present
                            if any(k in data and data.get(k) for k in provenance_keys):
                                return True

                            # Allow structured approved_by with a login as provenance
                            approved_by = data.get("approved_by")
                            if isinstance(approved_by, dict) and approved_by.get("login"):
                                return True
                    except Exception:
                        continue

        # Some CI flows may place approval artifacts under repo/jack or repo/jac, or write fallback files.
        if ctx.cwd:
            for repo_dir in ("jack", "jac"):
                repo_level = ctx.cwd / repo_dir
                if repo_level.exists():
                    approved = repo_level / "review-approved.jsonl"
                    if approved.exists():
                        try:
                            for line in approved.read_text(encoding="utf-8").splitlines():
                                try:
                                    data = json.loads(line)
                                except Exception:
                                    continue
                                if not isinstance(data, dict):
                                    continue

                                provider = str(data.get("provider", "")).lower()
                                run_id = data.get("run_id")
                                if provider in ("github", "github-actions", "github.com") and run_id:
                                    repo_name = os.environ.get("GITHUB_REPOSITORY") or data.get("repo")
                                    token = os.environ.get("GITHUB_TOKEN")
                                    # Strict: only accept when the GitHub run can be verified server-side.
                                    if repo_name and token:
                                        try:
                                            if _verify_github_run(repo_name, int(run_id), token):
                                                return True
                                        except Exception:
                                            pass
                                    # Cannot verify claimed GitHub run: do not accept.
                                    continue

                                if data.get("approved") is True and any(k in data and data.get(k) for k in provenance_keys):
                                    return True
                        except Exception:
                            pass
            for fallback_name in (".jack-review.jsonl", ".jac-review.jsonl"):
                fallback = ctx.cwd / fallback_name
                if fallback.exists():
                    try:
                        for line in fallback.read_text(encoding="utf-8").splitlines():
                            try:
                                data = json.loads(line)
                            except Exception:
                                continue
                            if not isinstance(data, dict):
                                continue

                            provider = str(data.get("provider", "")).lower()
                            run_id = data.get("run_id")
                            if provider in ("github", "github-actions", "github.com") and run_id:
                                repo_name = os.environ.get("GITHUB_REPOSITORY") or data.get("repo")
                                token = os.environ.get("GITHUB_TOKEN")
                                # Strict: only accept when the GitHub run can be verified server-side.
                                if repo_name and token:
                                    try:
                                        if _verify_github_run(repo_name, int(run_id), token):
                                            return True
                                    except Exception:
                                        pass
                                # Cannot verify claimed GitHub run: do not accept.
                                continue

                            if data.get("approved") is True and any(k in data and data.get(k) for k in provenance_keys):
                                return True
                    except Exception:
                        pass
    except Exception:
        pass
    return False

def handle_session_start(ctx: HookContext) -> None:
    if secret_like_value(ctx):
        ctx.logger.advisory("initial session prompt may contain a secret-like value; do not echo or log.")
    ctx.logger.emit_json(
        {
            "event": "session_start",
            "hook": ctx.hook,
            "detectedEvent": ctx.event,
            "cwd": str(ctx.cwd),
            "gitDir": str(ctx.git_dir) if ctx.git_dir else None,
            "prompt_length": len(ctx.prompt),
        }
    )


def handle_pre_tool_use(ctx: HookContext) -> None:
    jack_review_env = os.environ.get("JACK_REVIEW_OK")
    review_ok_env = jack_review_env == "1"
    # Deprecation advisory: prefer server-verified review artifacts over env bypass.
    if review_ok_env:
        try:
            ctx.logger.advisory("DEPRECATED: environment variable JACK_REVIEW_OK is set. This env var is deprecated and will be removed. Migrate to server-verified review artifacts (see docs/jacks/deprecate_jack_review_ok.md).")
        except Exception:
            pass
    review_ok = review_ok_env or has_review_approval(ctx)


    if ctx.hook == "tool-guardian":
        if destructive_shell(ctx) or piped_install(ctx):
            deny("JACK tool guardian blocked a destructive or permission-escalating shell command.")
        if destructive_git(ctx) and not review_ok:
            deny("JACK tool guardian blocked a destructive git operation until a review artifact is in place.")
        if network_exfiltration(ctx):
            deny("JACK tool guardian blocked a suspected network exfiltration command.")
        if broad_write_scope(ctx):
            ctx.logger.advisory("broad write scope detected; prefer narrowing to specific paths.")
        return

    if ctx.hook == "dependency-risk":
        if ctx.shell_command and matches_any(
            ctx.shell_command,
            [
                r"npm\s+(install|add)\s+-g\b",
                r"pip\s+install\s+.*(git\+|https?://)",
                r"pnpm\s+add\s+-g\b",
                r"yarn\s+global\s+add\b",
            ],
        ):
            deny("JACK dependency risk blocked an install path that needs explicit review.")
        if piped_install(ctx):
            deny("JACK dependency risk blocked a piped install path that needs explicit review.")
        return

    if ctx.hook == "review-gate":
        if destructive_shell(ctx) and not review_ok:
            deny("JACK review gate blocked a destructive action until a review artifact is in place.")
        if (infra_or_migration_path(ctx) or broad_write_scope(ctx)) and not review_ok:
            ctx.logger.advisory("migration, infra, or broad write scope detected; a review flag is recommended.")
        if (secret_path_write(ctx) or shell_secret_write(ctx)) and not review_ok:
            deny("JACK review gate blocked a write to a secret-like or environment file.")
        return

    if ctx.hook == "secrets-scanner":
        if (secret_like_value(ctx) or secret_path_write(ctx) or shell_secret_write(ctx)) and not review_ok:
            deny("JACK secrets scanner blocked a token-like value or a secret-like target path.")
        return

    if ctx.hook == "extension-surface-guard":
        if client_truth_claim(ctx):
            deny("JACK extension surface guard blocked a client-authority claim.")
        return

    if ctx.hook == "context-budgeter":
        if len(ctx.prompt) > 12000:
            ctx.logger.advisory("prompt is large; prefer narrowing context before continuing.")
        return

    if ctx.hook == "assumption-recorder":
        if re.search(r"\b(assume|likely|probably|maybe)\b", ctx.prompt.lower()):
            ctx.logger.advisory("surface assumptions explicitly in the task record.")


def handle_post_tool_use(ctx: HookContext) -> None:
    if ctx.hook == "structured-output":
        if not parse_structured_output(ctx):
            ctx.logger.advisory("emitted JSON-looking output that did not parse cleanly.")
        return
    if ctx.hook == "telemetry-emitter":
        ctx.logger.advisory("recorded a trace event in .git/jack-hooks/ when a Git directory was available.")


def handle_error_occurred(ctx: HookContext) -> None:
    error = error_details(ctx.payload)
    error_message = stringify(error.get("message", ""))
    artifact = {
        "event": "error_occurred",
        "hook": ctx.hook,
        "detectedEvent": ctx.event,
        "toolName": ctx.tool_name or None,
        "error_name": str(error.get("name", "")) or "unknown",
        "error_snippet": error_message[:200],
        "cwd": str(ctx.cwd),
        "gitDirFound": ctx.git_dir is not None,
    }
    ctx.logger.emit_json(artifact)
    ctx.logger.append_jsonl("error-occurred.jsonl", artifact)


def run_hook(ctx: HookContext) -> None:
    if ctx.hook == "session-start":
        handle_session_start(ctx)
    elif ctx.hook in {
        "tool-guardian",
        "dependency-risk",
        "review-gate",
        "secrets-scanner",
        "extension-surface-guard",
        "context-budgeter",
        "assumption-recorder",
    }:
        handle_pre_tool_use(ctx)
    elif ctx.hook in {"structured-output", "telemetry-emitter"}:
        handle_post_tool_use(ctx)
    elif ctx.hook == "error-occurred":
        handle_error_occurred(ctx)

