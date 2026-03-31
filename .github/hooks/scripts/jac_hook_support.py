from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, TextIO, cast


def load_payload(stream: TextIO) -> tuple[Dict[str, Any], Optional[str]]:
    try:
        raw = stream.read()
    except Exception as exc:
        return {}, f"could not read hook payload: {exc}"

    if not raw.strip():
        return {}, None

    try:
        payload = json.loads(raw)
    except Exception as exc:
        return {}, f"payload did not parse as JSON: {exc}"

    if isinstance(payload, dict):
        return cast(Dict[str, Any], payload), None

    return {"rawPayload": payload}, "payload was not a JSON object; wrapped raw payload for compatibility"


def resolve_cwd(payload: Dict[str, Any]) -> Path:
    raw = payload.get("cwd") or os.getcwd()
    return Path(str(raw)).resolve()


def resolve_git_dir(start: Path) -> Optional[Path]:
    for candidate in (start, *start.parents):
        dot_git = candidate / ".git"
        if dot_git.is_dir():
            return dot_git
        if not dot_git.is_file():
            continue
        try:
            first = dot_git.read_text(encoding="utf-8", errors="ignore").splitlines()[0].strip()
        except Exception:
            continue
        if not first.startswith("gitdir:"):
            continue
        target = (candidate / first.split(":", 1)[1].strip()).resolve()
        if target.exists():
            return target
    return None


@dataclass
class HookLogger:
    hook: str
    git_dir: Optional[Path]

    def advisory(self, message: str) -> None:
        try:
            print(f"JAC {self.hook}: {message}", file=sys.stderr)
        except Exception:
            return

    def emit_json(self, payload: Dict[str, Any]) -> None:
        try:
            print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
        except Exception:
            return

    def append_jsonl(self, file_name: str, payload: Dict[str, Any]) -> None:
        if self.git_dir is None:
            return
        try:
            log_dir = self.git_dir / "jac-hooks"
            log_dir.mkdir(parents=True, exist_ok=True)
            with (log_dir / file_name).open("a", encoding="utf-8", errors="surrogatepass") as handle:
                handle.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            return

    def append_hook_payload(self, payload: Dict[str, Any]) -> None:
        self.append_jsonl(f"{self.hook or 'unknown'}.jsonl", {"hook": self.hook, "payload": payload})
