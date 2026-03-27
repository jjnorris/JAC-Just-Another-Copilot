# Rollback and recovery

## goal
Keep risky work reversible and operationally understandable.

## when to use
- Heightened scrutiny work.
- Any change with migration, dependency, config, or deletion risk.

## prerequisites
- Known blast radius.
- Rollback owner or decision path.

## steps
1. State the disable path.
2. State the rollback trigger.
3. Note which artifacts must be preserved.
4. Define how to detect a bad outcome.
5. Record recovery steps in plain language.

## pause points
- Before irreversible actions.
- Before broad refactors or migrations.

## evidence to collect
- rollback note
- trigger conditions
- preserved artifact list

## stop conditions
- No credible rollback or disable path.
- Blast radius is unknown.

## escalation or review path
- Require review when rollback depends on human coordination.

## final report contract
Report rollback trigger, recovery owner, preserved evidence, and disable instructions.
