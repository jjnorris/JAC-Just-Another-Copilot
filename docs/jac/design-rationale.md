# Design rationale

JAC keeps short repo-scoped Copilot files in the locations GitHub documents, and keeps the longer reference material in `docs/jac/`.

## Repo-scoped files

The repo-scoped files in this repository are:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `.github/agents/*.agent.md` when present

These files need to stay concise because they are the files a supported environment may read directly.

## Reference material under `docs/jac/`

`docs/jac/` keeps the longer rules, workflows, templates, event contracts, examples, hook notes, support docs, and maintenance inventory.
That gives JAC one stable place for the longer explanations that do not belong in every repo-scoped file.

## Why the split exists

The split keeps the repo-scoped files practical and easy to transplant into another repository.
It also reduces repeated prose and makes support boundaries easier to state honestly.

## Claim boundaries

JAC only makes support claims that GitHub documents for the environment in question.
`docs/jac/inventory.json`, Markdown workflows, templates, examples, event contracts, and hook notes are reference material and manual fallback, not claimed native runtime features unless GitHub documents them that way.

## Maintenance rule

Each policy should have one clear home.
Repo-scoped files can summarize or point to the longer docs, but they should not quietly grow into a second copy of the same policy.
