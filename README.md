# Just Another Copilot

JAC is a small set of instructions, skills, hooks, and reference docs for GitHub Copilot.
It is meant to make Copilot work a little more cautious, explicit, and reviewable inside a repository.

## What this repo ships

The repo-scoped files live where GitHub documents them:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/agents/jac.agent.md`

Those files are the part a supported environment may read directly.
Repository instructions and `AGENTS.md` provide broad repo guidance.
Skills, hooks, and custom agent profiles are narrower and remain environment-specific.

## What `docs/jac/` is

`docs/jac/` is the longer reference set for JAC.
It holds rules, workflows, templates, event contracts, examples, hook notes, support docs, and maintenance inventory.
It supports the repo-scoped files and manual fallback use; it is not described here as a native runtime surface.

## Install shape

If you use this repository directly, keep `.github/`, `AGENTS.md`, and `docs/jac/` together.
If you transplant JAC into another repository, copy the same repo-scoped files first and bring `docs/jac/` along as the longer reference set.

`install.md` covers placement in more detail.

## Support boundaries

JAC only makes claims about GitHub Copilot surfaces that GitHub documents for the environment in question.
Skills, hooks, and custom agent profiles are still environment-specific.
Files under `docs/jac/`, including `docs/jac/inventory.json`, workflow notes, templates, examples, and hook notes, are reference material and manual fallback, not claimed runtime features.

`compatibility.md` covers those boundaries in more detail.

## Donation

Optional: https://buymeacoffee.com/jjnorris
