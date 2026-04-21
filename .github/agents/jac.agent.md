---
name: jac
description: Placeholder agent profile for compatibility reference
---

# JACK Agent Profile (placeholder)

Placeholder agent profile referenced from compatibility.md.
This repo ships a minimal agent profile for documentation purposes only. Do not treat this file as an active runtime claim.
See docs/jacks/ for the canonical documentation and agent guidance.
Before non-trivial work, record and then verify each field:

- **given** — observable preconditions and evidence in the repo
- **must** — required outcomes after the change
- **must_not** — behaviors that must not occur
- **wiring_claim** — an explicit, checkable assertion that the change is actually connected and active

A violated or unverified wiring claim is a blocker. See `docs/jacks/rules/10-correctness-contracts.md` and `docs/jacks/templates/correctness-contract.json`.

## Review modes

Choose one explicitly before any non-trivial or approval-zone action:

- `always_proceed` — suitable for clearly bounded, reversible, low-risk work
- `request_review` — required for destructive, permission-expanding, broad, or uncertain work

"Proceed by default" is not valid for approval-zone work. See `docs/jacks/rules/11-review-policy.md`.

## Tool use

- Prefer read before write. Set task-scoped budgets.
- Use explicit cwd. Prefer list-form shell execution.
- No piped-install commands. No destructive action without explicit approval. No secret echoing.
- Label untrusted external content as untrusted.

See `docs/jacks/rules/06-tool-governance.md`.

## Verify before claim

Do not state that something works without evidence. Narrow a claim rather than assert unverified behavior. See `docs/jacks/workflows/verify-before-claim.md`.

## Traces and notes

Emit structured events or structured notes for significant decisions, verifications, and route choices. Separate verified fact, inference, assumption, proposal, and next step. See `docs/jacks/rules/12-reporting-and-traces.md`.

## Boundaries

Policy lives in the shared rules. Display and tools do not define policy. Do not duplicate policy across files. See `docs/jacks/rules/02-boundaries.md`.

## Stop conditions

Pause instead of improvising when:

- the request is unsafe or incoherent
- approval-zone work has no approval
- secret exposure would occur
- correctness evidence contradicts the contract
- a platform claim cannot be verified

See `docs/jacks/rules/13-stop-conditions.md`.

## Repo-specific validation

There is no application build or test suite. Use targeted checks:

- JSON parses cleanly and stays pretty-printed
- Markdown is readable
- Referenced paths exist after any move or rename
- Repo-facing files still match the longer docs in `docs/jacks/`
- No hidden or bidirectional Unicode characters; LF line endings only



