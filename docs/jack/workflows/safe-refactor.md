# Safe refactor

## goal
Refactor without creating parallel abstractions or breaking real wiring.

## when to use
- Structural cleanup.
- Naming, layout, and ownership changes.

## prerequisites
- Existing pattern inventory.
- Correctness contract with explicit must-not regressions.

## steps
1. Identify the canonical existing pattern.
2. Check for near-duplicate abstractions.
3. Plan the refactor in reversible slices.
4. Preserve behavior first, then improve structure.
5. Verify that affected entry points still use the intended path.

## pause points
- Before renames with broad reach.
- Before deleting old paths.

## evidence to collect
- reuse assessment
- duplicate-abstraction warnings if any
- verification report

## stop conditions
- Refactor would require a broad approval-zone rewrite.
- Wiring claim cannot be validated.

## escalation or review path
- Request review for broad refactors or ownership changes.

## final report contract
Report what was consolidated, what stayed canonical, and how behavior was verified.
