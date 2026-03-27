# Design rationale

JAC now uses a native-first two-layer layout.

## Layer A: supporting canon

`docs/jac/` is the canonical long-form set.
It keeps policy, rationale, rules, workflows, templates, event contracts, examples, and hook-contract notes.

## Layer B: native Copilot files

The native layer in this repo is:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`

Those are the first public activation path because GitHub documents them as Copilot customization surfaces.
They stay concise and point back to the canon.

## Why the split exists

The earlier layout kept too much of the public story in a custom source-pack folder.
That was honest, but it was weaker than it needed to be.
The current layout puts the documented native files first and keeps the longer reasoning in one quieter place.

## What stays canon-only

The repository still does not claim native runtime support for:

- `docs/jac/source-pack-registry.json`
- `docs/jac/workflows/` as executable commands
- `docs/jac/templates/`, `docs/jac/event-contracts/`, and `docs/jac/examples/` as direct runtime surfaces
- `docs/jac/hook-contracts/` as executable hook configuration

Those files are for policy, rationale, maintenance, and fallback.

## Claim discipline

Skills and hooks are documented native surfaces, but not every Copilot client loads every native surface the same way.
So the repo should describe them narrowly, especially outside agent-capable flows.

## Canon discipline

Each policy still has one canonical home.
The native layer should summarize or point at the canon, not become a second canon.
