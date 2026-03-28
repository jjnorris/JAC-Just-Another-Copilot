# Policy design principles

This document explains what belongs in each layer of JAC and why.

## The two-layer model

JAC uses two layers:

1. **Native layer** — files placed where GitHub Copilot expects them
2. **Supporting canon** — longer policy, rationale, templates, and examples

The native layer activates. The supporting canon explains.

## What belongs where

### `.github/copilot-instructions.md`

Broad, always-on guidance for all Copilot interactions in this repo.
Keep it short. Every line should earn its place.
Do not put long rationale here. Point to `docs/jac/` instead.

### `.github/instructions/**/*.instructions.md`

Path-specific or topic-specific instructions.
Use `applyTo` frontmatter to scope them.
Keep each file focused on one concern.

### `AGENTS.md`

Operating notes for agent-capable flows.
Include working rules, validation rules, and escalation rules.
Stay concise. This is the agent's quick reference, not the full policy.

### `.github/skills/*/SKILL.md`

Named capabilities that an agent can invoke.
Each skill should do one thing and do it clearly.
Include: purpose, when to use, inputs, outputs, what it checks, limitations, and boundary.
Do not add a skill unless it fills a gap that instructions alone cannot fill.

### `.github/hooks/*.json`

Event-driven policy gates.
Each hook should target one class of risk and deny or warn clearly.
Keep the deny reason specific enough to be actionable.
Do not use hooks for workflow tasks (build, deploy, test, lint).

### `.github/agents/*.agent.md`

Custom agent profiles.
Required fields: `name`, `description` in YAML frontmatter.
Body should be concise operating instructions derived from the supporting canon.
Only add an agent profile if the agent role is meaningfully distinct from the default.

### `docs/jac/`

The canonical long-form source.
This is where rationale, long rules, workflows, templates, event contracts, examples, and hook-contract notes live.
Adapter files in `.github/` and `AGENTS.md` are derived from this layer, not the other way around.

## Principles

1. **One canonical home per policy.** If a rule exists in `docs/jac/rules/`, do not duplicate it in `.github/copilot-instructions.md`. Reference it instead.

2. **Derived, not duplicated.** The native adapter files should be concise derivations of the supporting canon. When the canon changes, update the adapters.

3. **Narrow claims.** Every surface claim should match what GitHub documents. Do not assert that a hook fires in every Copilot chat UI. Do not assert that skills load in every environment.

4. **Modest public voice.** Public-facing files should be plainly written and undersell rather than oversell. JAC is a small discipline pack, not a platform.

5. **Policy gates belong in hooks or skills.** Do not embed policy logic in prompts or instruction files when a hook or skill is the right tool.

6. **Supporting canon is for humans.** `docs/jac/` is not a runtime surface. It is for maintenance, manual fallback, and policy rationale. Do not claim GitHub natively consumes it.

## What does not belong in any JAC layer

- Workflow-specific tasks (run tests, deploy, generate changelog) — these are repo-specific
- Invented GitHub Copilot behavior not documented by GitHub
- Cross-product claims about non-GitHub tools
- Token counts, context limits, or model-specific tuning advice
