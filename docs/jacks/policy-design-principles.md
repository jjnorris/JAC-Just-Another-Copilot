# Policy design principles

This document explains where JACK material belongs and how to keep the repository readable.

## Repo-scoped files

These files live where GitHub documents them:

- `.github/copilot-instructions.md`
- `.github/instructions/**/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/agents/*.agent.md`

They should stay short, direct, and written for the person or tool that will use them.

## Reference material in `docs/jacks/`

`docs/jacks/` keeps the longer rules, workflows, templates, event contracts, examples, hook notes, and support docs.
Use it for longer explanations and maintenance detail.

## Placement guidance

### `.github/copilot-instructions.md`

Broad repo-wide guidance.
Keep it short and practical.

### `.github/instructions/**/*.instructions.md`

Scoped instructions with `applyTo` frontmatter.
Keep each file focused on one concern.

### `AGENTS.md`

Contributor and agent operating notes for this repository.
Include working rules, validation rules, and pause conditions.

### `.github/skills/*/SKILL.md`

Named capabilities that an agent can invoke.
Each skill should explain purpose, when to use it, what it checks, limits, and boundary.

### `.github/hooks/*.json`

Event-driven checks.
Each hook should target one class of risk and keep its message actionable.

### `.github/agents/*.agent.md`

Custom agent profiles.
Keep them brief and clearly distinct from the default behavior.

## Principles

1. **One clear home per policy.** If a rule already lives under `docs/jacks/rules/`, avoid rewriting it elsewhere.
2. **Keep repo-scoped files concise.** Longer explanation belongs in `docs/jacks/`.
3. **State narrow support claims.** Match GitHub's documented behavior for the environment in question.
4. **Keep the public voice plain.** Public-facing files should be modest and practical.
5. **Put policy checks in the right surface.** Use hooks or skills when the rule really belongs there.
6. **Keep reference material honest.** `docs/jacks/` supports maintenance and manual fallback; it is not a claimed runtime surface.

## What does not belong here

- repo-specific workflow chores such as deploy or changelog generation
- invented GitHub Copilot behavior
- broad claims about non-GitHub products
- model-tuning folklore presented as policy



