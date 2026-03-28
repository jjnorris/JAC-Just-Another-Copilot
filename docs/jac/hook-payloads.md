# Hook payloads

This document explains how JAC uses hook event payloads and what `jac_hook.py` is expected to inspect.

## How hooks work in JAC

JAC hooks are JSON files under `.github/hooks/*.json`.
Each file declares one or more hook event types and a command to run when that event fires.
The command runs `jac_hook.py <hook-name>` and receives a JSON payload on stdin.

The script reads the payload, applies policy rules, and either:
- exits silently (allow)
- writes a structured deny response to stdout and exits 0 (deny)
- writes a warning to stderr (advisory)

## Payload fields used by jac_hook.py

| Field | Type | Used by |
|---|---|---|
| `cwd` | string | all — sets the working directory for log output |
| `toolArgs` | string or object | preToolUse hooks — contains the tool call arguments |
| `prompt` | string | preToolUse, sessionStart — contains the current prompt or session context |
| `toolResult` | string or object | postToolUse hooks — contains the tool output |
| `errorMessage` | string | errorOccurred hooks — contains the error text |
| `errorCode` | string or number | errorOccurred hooks — contains the error code if present |

## What the script inspects

The script lowercases and concatenates `toolArgs`, `prompt`, and `toolResult` into a single string for pattern matching.
This makes the matching simple and portable but means false positives are possible on legitimate content.

Pattern matching is used for:
- destructive command detection (`tool-guardian`)
- dependency install risk (`dependency-risk`)
- destructive action gate (`review-gate`)
- secret-like value detection (`secrets-scanner`)
- client-authority claim detection (`extension-surface-guard`)
- prompt size advisory (`context-budgeter`)
- assumption detection (`assumption-recorder`)
- piped-install command detection in network exfiltration checks

## Hook event types covered

| Event | Hooks using it |
|---|---|
| `preToolUse` | tool-guardian, dependency-risk, review-gate, secrets-scanner, extension-surface-guard, context-budgeter, assumption-recorder |
| `postToolUse` | structured-output, telemetry-emitter |
| `sessionStart` | session-start |
| `errorOccurred` | error-occurred |

## Deny response format

When a hook denies a tool use, the response written to stdout must be:

```json
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "short plain-text reason"
}
```

The script exits 0 after writing the deny response.

## Audit log

Every hook invocation appends a JSONL record to `.git/jac-hooks/<hook-name>.jsonl`.
This is local-only and not committed.
It is intended for manual review, not automated processing.

## Limitations

- The hook script runs as a subprocess and cannot observe session state between calls.
- Pattern matching on lowercased concatenated text is approximate and may produce false positives.
- Hooks are only active in environments where GitHub documents hook execution (agent-capable flows).

See `.github/hooks/scripts/jac_hook.py` for the implementation.
See `docs/jac/hook-contracts/` for the per-hook rationale.
