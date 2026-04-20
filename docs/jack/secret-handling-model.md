# Secret handling model

## Boundary
JACK draws a hard boundary between secret material and ordinary configuration.
Secret material includes tokens, provider credentials, signing keys, session secrets, and anything that grants access or impersonation.
Ordinary configuration includes non-sensitive feature flags, hostnames, ports, and file paths.

## Storage preference
1. dedicated secret manager or encrypted local vault
2. environment injection through trusted local tooling
3. short-lived manual input when unavoidable

General settings files, examples, screenshots, logs, and prompts are poor secret storage locations and should be treated as hostile by default.

## Prompt rules
Do not place live credentials into prompts unless absolutely necessary.
If a credential must be referenced, minimize it, redact it, and justify why it was needed.

## Rotation awareness
Every token-handling task should consider:
- who can rotate it
- how compromise is detected
- what must be revoked
- how local examples avoid normalizing insecure persistence

## Anonymous-compatible pass-through
If a workflow can operate without user credentials, prefer that design.
This is only a concept-level preference. Do not claim a secure anonymous mode exists unless it has actually been built and verified.

