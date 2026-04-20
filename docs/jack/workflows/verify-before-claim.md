# Verify before claim

## goal
Prevent success claims that outrun the evidence.

## when to use
- Before reporting completion.

## prerequisites
- Correctness contract.
- Collected verification artifacts.

## steps
1. Map each `must` and `must_not` to evidence.
2. Verify the `wiring_claim` directly.
3. Record gaps as coverage misses.
4. Record orphan or unused implementation concerns.
5. Refuse or narrow any claim that lacks evidence.

## pause points
- When a wiring claim is only assumed.
- When evidence covers only a happy path.

## evidence to collect
- verification report
- coverage miss note
- wiring claim status

## stop conditions
- Critical claim lacks proof.
- Explicit wiring claim is false or untested.

## escalation or review path
- Return to implementation or review if evidence is incomplete.

## final report contract
Report verified behaviors, gaps, and exactly which claims remain unverified.
