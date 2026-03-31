#!/usr/bin/env python3
from __future__ import annotations

import sys

from jac_hook_rules import build_context, run_hook
from jac_hook_support import HookLogger, load_payload, resolve_cwd, resolve_git_dir


def main(argv: list[str]) -> int:
    hook = argv[1] if len(argv) > 1 else ""
    payload, warning = load_payload(sys.stdin)
    cwd = resolve_cwd(payload)
    git_dir = resolve_git_dir(cwd)
    logger = HookLogger(hook=hook or "unknown", git_dir=git_dir)

    if warning:
        logger.advisory(warning)

    logger.append_hook_payload(payload)

    context = build_context(
        hook=hook,
        payload=payload,
        cwd=cwd,
        git_dir=git_dir,
        logger=logger,
    )
    run_hook(context)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
