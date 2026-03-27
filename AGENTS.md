# JAC agent notes

Start with the native adapter layer:

1. `.github/copilot-instructions.md`
2. relevant `.github/instructions/*.instructions.md`
3. this `AGENTS.md`

Then use `jac-copilot/` as the longer source pack when you need the full policy text.

## Working rules

- `jac-copilot/` is the canonical source of truth
- `.github/` instruction files and `AGENTS.md` are concise adapters, not separate policy canons
- keep the public tone modest and a little unimpressed with itself
- do not reference outside product names or imply any outside runtime is required
- do not claim native execution for source-pack hooks, skills, workflows, or manifest metadata
- preserve the extension or client boundary and keep policy in the source pack
- prefer small reversible slices
- do not overclaim verification

## Validation rules for this repo

There is no normal app build or test pipeline here.
Use targeted checks instead:

- parse JSON
- verify manifest registry paths when the source-pack file list changes
- keep Markdown readable
- keep adapter files and source-pack summaries aligned
- remove hidden or bidirectional Unicode characters
- keep LF line endings

## Escalation rules

Pause instead of bluffing when:

- a Copilot support claim is not verified
- a change would make the adapter layer disagree with the source pack
- a destructive or approval-zone action appears without approval
- a security, secret, or license concern stops being advisory and becomes blocking
