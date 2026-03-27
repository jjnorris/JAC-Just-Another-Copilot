# Secret handling

## goal
Keep secrets, tokens, and credentials out of unsafe storage, logs, and prompts.

## when to use
- Any task touching auth, provider credentials, local config, or secret-adjacent data.

## prerequisites
- Secret boundary identified.
- Storage or runtime path understood.

## steps
1. Classify values as secret or non-secret config.
2. Prefer encrypted store or dedicated secret manager.
3. Keep secrets out of general settings files and prompts when possible.
4. Review logging, traces, screenshots, and examples for accidental disclosure.
5. Add rotation or revocation notes when tokens are involved.

## pause points
- Before persisting or echoing any credential.
- Before sharing examples that could normalize insecure storage.

## evidence to collect
- secret-boundary note
- storage decision
- redaction note if needed

## stop conditions
- Secret would be stored unsafely.
- Credential would be exposed in output.

## escalation or review path
- Require approval for config changes that affect secret handling.

## final report contract
State where secrets are allowed, where they are forbidden, and what redactions or rotations were required.
