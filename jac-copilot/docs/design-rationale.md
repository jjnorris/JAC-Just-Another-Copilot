# Design rationale

JAC now uses a two-layer layout.

## Layer A: source of truth

`jac-copilot/` is the canonical source pack.
It keeps the long-form policy, rules, workflows, templates, schemas, docs, examples, and portable behavioral contract files.

## Layer B: native Copilot adapter

The repo-native adapter layer is:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`

Those files are the first public activation path because GitHub documents them as customization surfaces.
They are intentionally concise summaries derived from the source pack.

## Why the split exists

The first version of this PR centered the portable package shape too much.
That kept the internal architecture strong, but it made the public install story less concrete than it should be.
The two-layer model fixes that by putting documented Copilot entry points first while preserving the deeper source pack behind them.

## What stays portable only

The repository still does not claim a native GitHub Copilot runtime for:

- `jac-copilot/manifest.json`
- `jac-copilot/hooks/`
- `jac-copilot/skills/`
- `jac-copilot/workflows/`

Those remain source-pack modules, adapter inputs, and behavioral contracts.

## Canon discipline

Each policy still has one canonical home.
The adapter layer should summarize or point at the canon, not become a second canon.
That keeps the public setup usable without letting the adapter files drift into a separate rule system.
