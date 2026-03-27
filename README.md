# Just Another Copilot

JAC is a small discipline pack for GitHub Copilot.

It is mostly a few instruction files, a longer source folder, and some JSON that tries to keep Copilot from making a mess.
It is not a runtime, not a service, and not a claim that every file in here is a native Copilot feature.

## What Copilot can use directly first

This repo ships the GitHub-documented instruction surfaces first:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`

Those are the files to keep in place if you want the least confusing setup in GitHub Copilot and supported editor flows.

## What the `jac-copilot/` folder is

That folder is the source pack.
It holds the longer rules, workflows, templates, schemas, and other portable contract files that the native adapter files summarize.

Useful pieces in there include:

- long-form instructions
- rule files
- workflow notes
- correctness and review templates
- trace schemas
- hook and skill definitions as portable contracts

## Install shape

If you use this repo as-is, the native adapter files are already wired:

1. keep `.github/copilot-instructions.md`
2. keep `.github/instructions/`
3. keep `AGENTS.md`
4. keep `jac-copilot/` beside them as the source pack

If you copy JAC into another repository, copy those same pieces together.
Do not copy only `jac-copilot/` and assume Copilot will discover it by magic.

More detail is in `jac-copilot/install.md` and `jac-copilot/compatibility.md`.

## Release readiness note

- Verified GitHub Copilot surfaces: `.github/copilot-instructions.md`, `.github/instructions/*.instructions.md`, `AGENTS.md`
- Portable only: `jac-copilot/manifest.json`, `jac-copilot/hooks/`, `jac-copilot/skills/`, `jac-copilot/workflows/`, templates, schemas, docs, examples
- Manual fallback: read the adapter files and source pack directly if your environment does not load them automatically
- Still adapter-dependent: turning hooks, skills, workflows, or metadata into executable runtime behavior

## What this is trying to do

Mostly just supervision.
A little less bluffing, a little more checking, and a clearer line between what is verified and what is only a portable note.

## Donation

If this saved you some time, you can buy me a coffee here: [YOUR_BUY_ME_A_COFFEE_URL]
