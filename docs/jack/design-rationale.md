# Design rationale

JACK keeps concise repo-scoped files in the locations GitHub documents and keeps the longer reference material in `docs/jack/`.

## Why the split exists

The split keeps the repo-scoped native layer practical and easier to transplant into another repository.
It also reduces repeated prose, gives policies one clear home, and makes support boundaries easier to state honestly.

## What belongs in each layer

The repo-scoped native layer is `.github/` plus `AGENTS.md`.
Those files need to stay concise because they are the files a supported environment may read directly.

`docs/jack/` keeps the longer rules, workflows, templates, examples, hook notes, support docs, and maintenance inventory that those repo-scoped files point back to.

## Claim boundaries

JACK only makes support claims that GitHub documents for the environment in question.
`docs/jack/inventory.json`, Markdown workflows, templates, examples, event contracts, and hook notes are reference material and manual fallback, not claimed native runtime features unless GitHub documents them that way.

## Maintenance rule

Each policy should have one clear home.
Repo-scoped files can summarize or point to the longer docs, but they should not quietly grow into a second copy of the same policy.


