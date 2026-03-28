# Just Another Copilot

JAC is a small discipline pack for GitHub Copilot.

It is mostly a few native repo files, a longer canon folder, and some JSON meant to keep Copilot a little more supervised.
It is not a runtime, not a service, and not a promise that every Copilot surface behaves the same way everywhere.

## Native files first

This repo puts the documented Copilot-facing files where GitHub expects them:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/agents/jac.agent.md`

Repository instructions and `AGENTS.md` are the broad repo layer.
Skills and hooks are narrower agent surfaces and should be described that way, not as universal behavior across every Copilot UI.

## What `docs/jac/` is

That folder is the longer supporting canon.
It keeps the long-form instructions, rules, workflows, templates, event contracts, examples, and hook-contract notes that sit behind the native layer.

## Install shape

If you use this repo as-is, keep these together:

1. `.github/copilot-instructions.md`
2. `.github/instructions/`
3. `.github/skills/`
4. `.github/hooks/`
5. `AGENTS.md`
6. `docs/jac/`

If you copy JAC into another repository, copy the same set.
Do not copy only `docs/jac/` and assume Copilot will discover it.

More detail is in `install.md` and `compatibility.md`.

## Release readiness note

- Verified native files in this repo: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`, `.github/skills/*/SKILL.md`, `.github/hooks/*.json`, `.github/agents/jac.agent.md`
- Supporting canon only: `docs/jac/source-pack-registry.json`, `docs/jac/hook-contracts/`, `docs/jac/workflows/`, templates, event contracts, examples, and longer docs
- Manual fallback: read the native files and `docs/jac/` directly if your environment does not load them automatically
- Still environment-specific: which Copilot clients load which surfaces, especially hooks and skills outside agent-capable flows

## What this is trying to do

Mostly just supervision.
A little less bluffing, a little more checking, and a clearer line between native files and supporting notes.

## Donation

If this saved you some time, you can buy me a coffee here: https://buymeacoffee.com/jjnorris
