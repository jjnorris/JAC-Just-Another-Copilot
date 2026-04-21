# Hook payloads

This document explains how JACK's native hooks are wired, what payload fields the hook runner actually reads, and where the hook notes stop.

## How JACK hooks are wired

- Native hook configs live in `.github/hooks/*.json`.
- The configs invoke `.github/hooks/scripts/jac_hook.py`.
- The hook runner reads JSON from stdin, applies a small set of policy checks, and then either:
  - exits silently and allows the action,
  - writes a deny response to stdout and exits successfully, or
  - writes an advisory message to stderr.

The design here is intentionally small:
- native config in `.github/hooks/`
- one shared runner script
- longer rationale in `docs/jack/hook-contracts/`

Note: The runner recognizes an operational environment flag `JACK_REVIEW_OK`. When set to `1`, checks in `review-gate` and `tool-guardian` treat the environment as review-approved (for example, allowing some destructive git or shell actions that would otherwise be denied). This flag is intended for trusted CI or administrator-controlled contexts; do not use it in untrusted interactive sessions.

## Payload fields the runner uses

| Field | Type | Used by |
|---|---|---|
| `cwd` | string | all events — used to resolve the effective working directory and Git log location |
| `toolName` | string | `preToolUse` — used to separate shell checks from file/path checks |
| `toolArgs` | string or object | `preToolUse` — parsed when possible for shell commands and path-aware checks |
| `prompt` | string | `userPromptSubmitted` — used for prompt-size and assumption advisories |
| `initialPrompt` | string | `sessionStart` — used for session-start inspection |
| `toolResult` | string or object | `postToolUse` — used for structured-output checks |
| `error` | object | `errorOccurred` — uses `message`, `name`, and `stack` when available |

## Compatibility fallback

The runner prefers the currently documented fields:
- `initialPrompt` for `sessionStart`
- `error.message` and `error.name` for `errorOccurred`

For compatibility, it can still fall back to older flat keys such as:
- `prompt`
- `errorMessage`
- `errorCode`

That fallback is there to keep the checks from failing hard when payload shapes vary.
It is not a claim that the older flat keys are the preferred current schema.

## What the runner actually inspects

JACK does **not** treat every hook payload as one giant undifferentiated blob anymore.
It now inspects payloads in a more structured way:

- shell-oriented checks read the shell command when the tool is a shell tool
- path-sensitive checks inspect candidate file paths when the tool is a write/edit style tool
- prompt advisories read `prompt` or `initialPrompt`
- structured-output checks inspect `toolResult`
- error logging reads the nested `error` object when present

A lowercased aggregate text form is still used for a few generic pattern checks, but the runner should prefer structured fields when they are available.

## Hook event coverage in JACK

| Event | JACK use |
|---|---|
| `sessionStart` | prompt-length logging, session-start secret advisory |
| `userPromptSubmitted` | prompt-size and assumption advisories |
| `preToolUse` | command, path, dependency, secret, review, and extension-boundary checks |
| `postToolUse` | structured-output validation and telemetry note |
| `errorOccurred` | compact error artifact logging |

## Deny response format

When a hook denies a tool use, the response written to stdout must be:

```json
{
  "permissionDecision": "deny",
  "permissionDecisionReason": "short plain-text reason"
}


