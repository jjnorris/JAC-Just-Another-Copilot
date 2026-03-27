---
name: doublecheck
description: Re-run truth, correctness, reuse, and reporting checks before any strong claim.
---

# doublecheck

## Purpose
Re-run truth, correctness, reuse, and reporting checks before any strong claim.

## When to use
- before completion
- after non-trivial implementation
- after risky research conclusions

## Inputs
- correctness contract
- current diff or artifact set
- verification evidence
- report draft

## Outputs
- claim-status summary
- coverage miss note
- reduced overclaim risk

## What it checks
- Do not upgrade a claim without evidence.
- Flag wiring uncertainty explicitly.
- Prefer narrowing the claim over smoothing the language.

## Warnings
- Passing tests may still miss real wiring.
- Narrative confidence can hide missing proof.

## Blocks on
- Explicit wiring claim is contradicted.
- Critical claim has no evidence at all.

## Evidence expected or emitted
- coverage_miss
- wiring_claim_orphan
- usage_recorded

## Examples
- Check whether the package registry actually references newly added workflow docs.

## Limitations
- Falls back to: Manual verification checklist using `workflows/verify-before-claim.md`.

## Boundary
- May advise, warn, or narrow claims. It may not fabricate evidence or self-approve blocked work.

## Related docs
- `docs/jac/rules/10-correctness-contracts.md`
- `docs/jac/workflows/verify-before-claim.md`
