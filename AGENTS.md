# JAC agent notes

Start with the native repo layer:

1. `.github/copilot-instructions.md`
2. relevant `.github/instructions/*.instructions.md`
3. matching `.github/skills/*/SKILL.md` or `.github/hooks/*.json` when the task is that narrow
4. this `AGENTS.md`

Then use `docs/jac/` when you need the longer policy and rationale.

## Working rules

- `docs/jac/` is the canonical long-form source
- `.github/` files and `AGENTS.md` are concise operational adapters
- keep the public tone modest and a little unimpressed with itself
- do not reference outside product names or imply any outside runtime is required
- keep hook and skill claims narrow and aligned with GitHub's documented surfaces
- do not turn the supporting canon into a fake runtime story
- prefer small reversible slices
- do not overclaim verification

## Validation rules for this repo

There is no normal app build or test pipeline here.
Use targeted checks instead:

- parse JSON
- verify referenced paths after any move or rename
- keep Markdown readable
- keep adapter files and supporting canon aligned
- remove hidden or bidirectional Unicode characters
- keep LF line endings

## Escalation rules

Pause instead of bluffing when:

- a Copilot support claim is not verified
- a change would make the adapter layer disagree with the supporting canon
- a destructive or approval-zone action appears without approval
- a security, secret, or license concern stops being advisory and becomes blocking
