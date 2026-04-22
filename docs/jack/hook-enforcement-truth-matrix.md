# Hook Enforcement Truth Matrix

The runner truth here comes from the current tree: every `.github/hooks/*.json` config dispatches to `.github/hooks/scripts/jac_hook.py <hook>`, the enforcement logic lives in `.github/hooks/scripts/jac_hook_rules.py`, and the shared helper is `.github/hooks/scripts/jac_hook_support.py`.

No `jac_hook_common.py` exists in the current tree.

Legend for current enforcement class:
- `deny-enforced` = the runner can deny matching actions.
- `advisory-only` = the runner only warns or records notes.
- `adapter-required` = durable effect depends on external adapter/manual artifact support.
- `mixed` = the runner has a mix of deny and advisory behavior, or behavior gated by `JACK_REVIEW_OK`.

| Hook | Contract path | Actual enforcement class today | Evidence from runner/config | Current contract wording |
| --- | --- | --- | --- | --- |
| `session-start` | `docs/jack/hook-contracts/session-start/hook.json` | `advisory-only` | `.github/hooks/session-start.json` dispatches `python3 .github/hooks/scripts/jac_hook.py session-start`; `handle_session_start()` only logs an advisory on secret-like input and emits a JSON note. | accurate |
| `error-occurred` | `docs/jack/hook-contracts/error-occurred/hook.json` | `advisory-only` | `.github/hooks/error-occurred.json` dispatches the shared runner; `handle_error_occurred()` emits structured JSON and JSONL, with no deny path. | accurate |
| `context-budgeter` | `docs/jack/hook-contracts/context-budgeter/hook.json` | `advisory-only` | `.github/hooks/context-budgeter.json` dispatches the shared runner; `handle_pre_tool_use()` only calls `logger.advisory()` when the prompt is large. | accurate |
| `assumption-recorder` | `docs/jack/hook-contracts/assumption-recorder/hook.json` | `advisory-only` | `.github/hooks/assumption-recorder.json` dispatches the shared runner; `handle_pre_tool_use()` only calls `logger.advisory()` on assumption language. | accurate |
| `structured-output` | `docs/jack/hook-contracts/structured-output/hook.json` | `advisory-only` | `.github/hooks/structured-output.json` dispatches the shared runner; `handle_post_tool_use()` only calls `logger.advisory()` on parse failures. | accurate |
| `telemetry-emitter` | `docs/jack/hook-contracts/telemetry-emitter/hook.json` | `advisory-only` | `.github/hooks/telemetry-emitter.json` dispatches the shared runner; `handle_post_tool_use()` only calls `logger.advisory()`, and `HookLogger.append_jsonl()` writes local JSONL only when a Git directory is available. | accurate |
| `dependency-risk` | `docs/jack/hook-contracts/dependency-risk/hook.json` | `mixed` | `.github/hooks/dependency-risk.json` dispatches the shared runner; `handle_pre_tool_use()` denies global install paths and piped installs, but the runner does not inspect license compatibility. | accurate |
| `extension-surface-guard` | `docs/jack/hook-contracts/extension-surface-guard/hook.json` | `deny-enforced` | `.github/hooks/extension-surface-guard.json` dispatches the shared runner; `handle_pre_tool_use()` calls `deny()` when a client-side truth claim is detected. | accurate |
| `review-gate` | `docs/jack/hook-contracts/review-gate/hook.json` | `mixed` | `.github/hooks/review-gate.json` dispatches the shared runner; `handle_pre_tool_use()` denies destructive shell and secret-like writes when `JACK_REVIEW_OK != 1`, and only warns on broad writes or migration-like scopes. | accurate |
| `secrets-scanner` | `docs/jack/hook-contracts/secrets-scanner/hook.json` | `deny-enforced` | `.github/hooks/secrets-scanner.json` dispatches the shared runner; `handle_pre_tool_use()` calls `deny()` for token-like values and secret-like paths. | accurate |
| `tool-guardian` | `docs/jack/hook-contracts/tool-guardian/hook.json` | `mixed` | `.github/hooks/tool-guardian.json` dispatches the shared runner; `handle_pre_tool_use()` denies destructive shell, piped installs, destructive git without `JACK_REVIEW_OK`, and suspected exfiltration, while broad write scope only warns. | accurate |

Notes

- The matrix reflects the current runner code, not aspirational contract policy.
- The main truthfulness repairs were to remove or narrow false `blocks_on` claims and to correct enforcement labels where the runner really denies behavior.
- `telemetry-emitter` remains durability-sensitive: the runner is advisory-only, but durable local logging still depends on a Git-backed context or manual artifact support.
