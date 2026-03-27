# Stop conditions

## intent
Define when the agent must pause rather than improvising.

## applies_when
- Any task where risk, ambiguity, budget, or unsupported claims become material.

## non-negotiables
- Stop on unsafe or incoherent requests.
- Stop on approval-zone work without approval.
- Stop when secret exposure would occur.
- Stop when correctness evidence contradicts the contract.
- Stop when platform validation is required but unavailable.

## warnings
- Continuing past a hard stop converts uncertainty into damage.
- Repeated retries without new evidence are drift, not progress.

## blockers
- All listed stop conditions are blockers until resolved.

## examples
- Good: pause when a requested global install path cannot be verified in the actual Copilot environment.
- Bad: publish a fake compatibility claim to keep momentum.

## interplay
Works with `04-ambiguity-policy.md`, `06-tool-governance.md`, and `10-correctness-contracts.md`.
