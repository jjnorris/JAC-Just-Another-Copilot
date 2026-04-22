# Bugfix with proof

## goal
Fix a bug and prove the real path is corrected.

## when to use
- Defect triage and repair.

## prerequisites
- Reproduction or clearly stated failure mode.
- Correctness contract with a concrete wiring claim.

## steps
1. Capture the observed failure or missing behavior.
2. State the smallest fix hypothesis.
3. Implement the minimum change.
4. Verify the failing path now behaves correctly.
5. Check that adjacent must-not conditions still hold.

## pause points
- If reproduction is unclear.
- If the fix expands into a refactor.

## evidence to collect
- before state description
- after state evidence
- coverage miss note if proof is partial

## stop conditions
- No reproducible or inspectable failure path.
- Fix would require unverifiable claims.

## escalation or review path
- Seek review when the fix crosses subsystem boundaries.

## final report contract
Describe the bug, the narrow fix, the proof gathered, and any remaining risk.
