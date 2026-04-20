---
name: pattern-library
description: Prefer canonical patterns and warn about duplicate abstractions or premature generalization.
---

# pattern-library

## Purpose
Prefer canonical patterns and warn about duplicate abstractions or premature generalization.

## When to use
- before adding new structures
- during refactor or design work

## Inputs
- existing file layout
- candidate symbols or patterns

## Outputs
- reuse recommendation
- duplicate-abstraction warning

## What it checks
- Prefer curated canonical patterns.
- Do not auto-harvest business logic as a pattern library.
- Avoid premature abstraction.

## Warnings
- Clean and extensible variants both matter, but only with one clear home.
- Near-duplicate names signal drift.

## Blocks on
- A new abstraction duplicates existing ownership without justification.

## Evidence expected or emitted
- duplicate_abstraction_candidate

## Examples
- Warn if a new policy file duplicates memory rules already owned by `05-memory-policy.md`.

## Limitations
- Falls back to: Manual pattern comparison against the current tree.

## Boundary
- May recommend reuse and consolidation. It may not invent a second competing home.

## Related docs
- `docs/jack/rules/00-core-role.md`
- `docs/jack/rules/02-boundaries.md`

