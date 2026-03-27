---
name: correctness-contract
description: Create and enforce the pre-write behavioral contract for non-trivial work.
---

# correctness-contract

## Purpose
Create and enforce the pre-write behavioral contract for non-trivial work.

## When to use
- before non-trivial edits
- before bugfix or refactor

## Inputs
- task scope
- repo context
- expected behavior

## Outputs
- contract artifact
- verification checklist

## What it checks
- Require given, must, must_not, wiring_claim.
- No non-trivial work without a contract.
- Tie verification back to each contract field.

## Warnings
- Compile success is not enough.
- Unverified wiring makes a contract incomplete.

## Blocks on
- Wiring claim is false or unprovable.

## Evidence expected or emitted
- coverage_miss
- wiring_claim_orphan

## Examples
- State that the manifest must register every workflow and hook path that exists.

## Limitations
- Falls back to: Manual correctness checklist in markdown or JSON.

## Boundary
- May state and validate behavioral obligations. It may not waive them for convenience.

## Related docs
- `docs/jac/rules/10-correctness-contracts.md`
- `docs/jac/templates/correctness-contract.json`
