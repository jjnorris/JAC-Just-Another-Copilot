# Hook Regression Tests

This repository includes a small standard-library regression harness for the current hook runner behavior.

## What is covered

 - One deny-enforced case: `extension-surface-guard` denies a client-authority claim.
 - One advisory-only case: `assumption-recorder` records an advisory and does not deny.
 - Additional quiet case: `extension-surface-guard` stays quiet on a neutral prompt with no client-authority language.
 - Additional quiet case: `assumption-recorder` stays quiet on a neutral prompt with no assumption language.
 - Wrapper-plus-hook dual-surface coverage: `assumption-recorder` appends the incoming payload into `.git/jac-hooks/assumption-recorder.jsonl` when a Git directory is available and still records an advisory for an assumption-like prompt.
 - Wrapper-plus-hook dual-surface coverage: `assumption-recorder` appends the incoming payload into `.git/jac-hooks/assumption-recorder.jsonl` when a Git directory is available and stays quiet on a neutral prompt.
 - Wrapper-plus-hook dual-surface coverage: `extension-surface-guard` appends the incoming payload into `.git/jac-hooks/extension-surface-guard.jsonl` when a Git directory is available and still denies a client-authority claim.
 - Wrapper-plus-hook dual-surface coverage: `extension-surface-guard` appends the incoming payload into `.git/jac-hooks/extension-surface-guard.jsonl` when a Git directory is available and stays quiet on a neutral prompt.
 - One mixed case: `review-gate` denies a destructive shell command when `JACK_REVIEW_OK` is unset and allows the same command when `JACK_REVIEW_OK=1`.
 - Additional quiet case: `review-gate` stays quiet on a benign shell command.
 - Wrapper-plus-hook dual-surface coverage: `review-gate` appends the incoming payload into `.git/jack-hooks/review-gate.jsonl` when a Git directory is available and still denies a destructive shell command when `JACK_REVIEW_OK` is unset.
 - Wrapper-plus-hook dual-surface coverage: `review-gate` appends the incoming payload into `.git/jac-hooks/review-gate.jsonl` when a Git directory is available and stays quiet on a benign shell command.
 - Wrapper-plus-hook no-Git coverage: `review-gate` through the CLI wrapper without a Git directory denies a destructive shell command when `JACK_REVIEW_OK` is unset and does not write a `.git/jack-hooks/review-gate.jsonl` artifact.
 - Wrapper-plus-hook no-Git coverage: `review-gate` through the CLI wrapper without a Git directory stays quiet on a benign shell command and does not write a `.git/jac-hooks/review-gate.jsonl` artifact.
 - Additional quiet case: `dependency-risk` stays quiet on a benign install/update command.
 - Wrapper-plus-hook dual-surface coverage: `dependency-risk` appends the incoming payload into `.git/jac-hooks/dependency-risk.jsonl` when a Git directory is available and still blocks a piped install path that needs explicit review.
 - Wrapper-plus-hook dual-surface coverage: `dependency-risk` appends the incoming payload into `.git/jac-hooks/dependency-risk.jsonl` when a Git directory is available and stays quiet on a benign install/update command.
 - Additional deny-enforced case: `secrets-scanner` blocks token-like values or writes to secret-like paths.
 - Wrapper-plus-hook dual-surface coverage: `secrets-scanner` appends the incoming payload into `.git/jac-hooks/secrets-scanner.jsonl` when a Git directory is available and still denies a token-like prompt.
 - Wrapper-plus-hook dual-surface coverage: `secrets-scanner` appends the incoming payload into `.git/jac-hooks/secrets-scanner.jsonl` when a Git directory is available and stays quiet on a benign prompt and target path.
 - Additional advisory-only case: `structured-output` records an advisory when emitted JSON-like output does not parse cleanly.
 - Wrapper-plus-hook dual-surface coverage: `structured-output` appends the incoming payload into `.git/jac-hooks/structured-output.jsonl` when a Git directory is available and still emits its parse-failure advisory.
 - Wrapper-plus-hook dual-surface coverage: `structured-output` appends a valid-JSON incoming payload into `.git/jac-hooks/structured-output.jsonl` when a Git directory is available and stays quiet because the JSON parses cleanly.
 - Wrapper-plus-hook no-Git coverage: `structured-output` through the CLI wrapper without a Git directory emits its parse advisory for invalid JSON-like output and does not write a `.git/jac-hooks/structured-output.jsonl` artifact.
 - Wrapper-plus-hook no-Git coverage: `structured-output` through the CLI wrapper without a Git directory stays quiet for valid JSON output and does not write a `.git/jac-hooks/structured-output.jsonl` artifact.
 - Additional mixed case: `tool-guardian` blocks destructive git operations unless `JACK_REVIEW_OK=1` is set.
 - Additional deny-enforced case: `tool-guardian` blocks a suspected network exfiltration command.
 - Additional quiet case: `tool-guardian` stays quiet on a benign shell command.
 - Wrapper-plus-hook dual-surface coverage: `tool-guardian` appends the incoming payload into `.git/jac-hooks/tool-guardian.jsonl` when a Git directory is available and still denies a suspected network exfiltration command.
 - Wrapper-plus-hook dual-surface coverage: `tool-guardian` appends the incoming payload into `.git/jac-hooks/tool-guardian.jsonl` when a Git directory is available and stays quiet on a benign shell command.
 - Wrapper-plus-hook no-Git coverage: `tool-guardian` through the CLI wrapper without a Git directory denies a suspected network exfiltration command and does not write a `.git/jac-hooks/tool-guardian.jsonl` artifact.
 - Wrapper-plus-hook no-Git coverage: `tool-guardian` through the CLI wrapper without a Git directory stays quiet on a benign shell command and does not write a `.git/jac-hooks/tool-guardian.jsonl` artifact.
 - Additional deny-enforced case: `secrets-scanner` blocks a token-like value in the prompt.
 - Additional quiet case: `secrets-scanner` stays quiet on a benign prompt and target path.
 - Emitted payload assertion: `session-start` emits a `session_start` JSON payload containing `prompt_length` and other metadata.
 - Wrapper-plus-hook dual-surface coverage: `session-start` appends the incoming payload into `.git/jac-hooks/session-start.jsonl` when a Git directory is available and still emits its structured JSON and secret-prompt advisory behavior.
 - Wrapper-plus-hook no-Git coverage: `session-start` through the CLI wrapper without a Git directory emits its structured JSON payload and the secret-like advisory when appropriate, and does not write a `.git/jac-hooks/session-start.jsonl` artifact.
 - Wrapper-plus-hook no-Git coverage: `session-start` through the CLI wrapper without a Git directory emits its structured JSON payload for a benign prompt and does not write a `.git/jac-hooks/session-start.jsonl` artifact.
 - Wrapper-plus-hook dual-surface coverage: `session-start` appends a benign incoming payload into `.git/jac-hooks/session-start.jsonl` when a Git directory is available and still emits its structured JSON payload without a secret-like advisory.
 - Error payload and local-log coverage: `error-occurred` emits a structured JSON payload and appends a JSONL record when a Git directory is available.
 - Wrapper-plus-hook dual-surface coverage: `error-occurred` appends the incoming payload into `.git/jac-hooks/error-occurred.jsonl` when a Git directory is available and still emits its structured stderr JSON plus the hook's own JSONL artifact.
 - Wrapper-plus-hook no-Git coverage: `error-occurred` through the CLI wrapper without a Git directory emits structured stderr JSON and leaves no `.git/jac-hooks/error-occurred.jsonl` artifact.
 - CLI payload logging coverage: `telemetry-emitter` appends the original hook payload into `.git/jac-hooks/telemetry-emitter.jsonl` when a Git directory is available.
 - Advisory/logging edge: `telemetry-emitter` still emits its advisory when no Git directory is available and skips the JSONL write.
 - Additional quiet case: `structured-output` stays silent when emitted JSON parses cleanly.
 - Threshold edge case: `context-budgeter` stays quiet at the 12000-character prompt boundary.
 - Boundary advisory case: `context-budgeter` warns when the prompt exceeds the 12000-character threshold.
 - Additional mixed case: `dependency-risk` blocks a piped install path that needs explicit review.
 - Additional emitted/logging case: `session-start` warns on a secret-like prompt and still emits the structured `session_start` JSON payload.

## What is not covered yet

- Full end-to-end GitHub event payloads.
- Other hooks in the truth matrix beyond those covered above.
- Broader runner behavior that depends on real GitHub delivery or live Git metadata discovery.

## How to run

Run the harness from the repository root:

```bash
python3 scripts/hook_regression_tests.py
```

The harness uses only the Python standard library and imports the existing hook runner entrypoints directly.

## Combined local verification

For a single local check that runs both the hook regression harness and the repository
validator in sequence, run this command from the repository root:

```bash
python3 scripts/verify_local_checks.py
```

The combined command prints clear labeled output for each step and exits non-zero if
either the tests or the validator fail.
