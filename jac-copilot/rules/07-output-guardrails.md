# Output guardrails

## intent
Prevent secret leakage, malformed structured output lies, and false success claims.

## applies_when
- Producing text, JSON, reports, traces, or generated code snippets.

## non-negotiables
- Scan for secrets, credentials, tokens, and obvious PII.
- Redact and continue by default.
- Retry malformed structured output once.
- Stay honest about schema validity and unresolved dependencies.

## warnings
- Silent coercion hides real failures.
- Over-redaction can erase important reasoning if not summarized clearly.

## blockers
- Sensitive data would be exposed.
- Structured output corruption would break downstream logic.
- A claim is provably false.

## examples
- Good: redact token-like strings and note that redaction occurred.
- Bad: replace invalid JSON with a prose success message and hope it passes.

## interplay
Works with `hooks/secrets-scanner/hook.json`, `hooks/structured-output/hook.json`, and `09-compliance-security-license.md`.
