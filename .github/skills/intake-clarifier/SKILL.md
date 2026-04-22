---
name: intake-clarifier
description: Assess task readiness and produce clarification or assumption artifacts.
---

# intake-clarifier

## Purpose
Assess task readiness and produce clarification or assumption artifacts.

## When to use
- task start
- new ambiguity appears

## Inputs
- request text
- current repo facts

## Outputs
- ready-scope summary
- assumption record
- clarification request

## What it checks
- Assess task readiness, not user sophistication.
- Use blocking clarification only when needed.
- Keep tone direct and non-condescending.

## Warnings
- Unrecorded assumptions can mutate scope.
- Late ambiguity is still real ambiguity.

## Blocks on
- Security-sensitive ambiguity remains unresolved.

## Evidence expected or emitted
- assumption_added
- clarification_requested
- clarification_resolved

## Examples
- Assume a portable manifest format when no native schema is verified.

## Limitations
- Falls back to: Plain-text assumption and clarification notes.

## Boundary
- May classify uncertainty and ask for clarification. It may not hide ambiguity.

## Related docs
- `docs/jack/rules/04-ambiguity-policy.md`
- `docs/jack/workflows/intake-and-clarify.md`

