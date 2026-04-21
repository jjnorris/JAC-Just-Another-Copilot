---
name: failure-triage
description: Classify failures, separate verified facts from guesses, identify a narrow first reproduction path, and prevent thrashing.
---

# failure-triage

## Purpose
When a task hits an error, test failure, or unexpected behavior, apply a structured classification before retrying blindly.

## When to use
- A build, test, or tool execution fails
- An error message appears and the cause is not immediately obvious
- The same fix has been attempted more than once without success
- The failure might be environment-specific or intermittent

## Inputs
- Error output or failure message
- Most recent action taken before the failure
- Relevant file or line reference if available

## Outputs
- Failure class: tool-error | environment-issue | logic-error | data-error | permission-error | unknown
- Verified facts: what can be confirmed from the output
- Unverified guesses: what is inferred but not confirmed
- First reproduction path: the narrowest possible test or command to confirm the failure
- Next step: one action only, not a list of speculative fixes

## What it checks
- Is the error message explicit about cause?
- Is the failure deterministic or potentially intermittent?
- Is there a simpler reproduction path than the full failing task?
- Has this same fix been tried before without success?

## Warnings
- Do not retry the same action a third time without new evidence.
- Distinguish "I tried and it failed" from "I understand why it failed."
- Environment issues (missing tool, wrong version) are not logic errors.

## Blocks on
- Attempting more than two retries without a new verified fact or changed approach.

## Evidence expected or emitted
- failure_class
- verified_facts list
- unverified_guesses list
- reproduction_path
- next_step

## Limitations
- Falls back to: emit the structured triage record and stop for review.
- Does not guess fixes. Does not run speculative commands.

## Boundary
- Classification and one recommended next step. Does not fix the problem autonomously.

## Related docs
- `docs/jacks/rules/01-repo-truth.md`
- `docs/jacks/rules/13-stop-conditions.md`
- `docs/jacks/workflows/bugfix-with-proof.md`


