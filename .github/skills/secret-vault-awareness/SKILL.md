---
name: secret-vault-awareness
description: Keep a hard line between secret material and ordinary configuration.
---

# secret-vault-awareness

## Purpose
Keep a hard line between secret material and ordinary configuration.

## When to use
- auth work
- provider credentials
- token or secret-adjacent tasks

## Inputs
- config fields
- storage path
- logging path

## Outputs
- secret-boundary note
- rotation reminder
- redaction actions

## What it checks
- Prefer encrypted stores.
- Do not persist secrets in general settings files.
- Keep credentials out of prompts when possible.

## Warnings
- Examples can normalize insecure handling if not reviewed.
- Screenshots and traces can leak more than code.

## Blocks on
- Unsafe persistence or exposure path.

## Evidence expected or emitted
- pii_detected

## Examples
- Warn if a config template includes a live API token field with sample contents.

## Limitations
- Falls back to: Manual secret review checklist.

## Boundary
- May warn and block unsafe secret handling. It may not expose secrets for convenience.

## Related docs
- `docs/jac/workflows/secret-handling.md`
- `docs/jac/secret-handling-model.md`
