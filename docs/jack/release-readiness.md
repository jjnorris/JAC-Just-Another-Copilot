# Release readiness

Use this checklist before calling a JACK change ready to ship.

## Repo-scoped files

- `.github/copilot-instructions.md` exists and still fits its repo-wide purpose
- `.github/instructions/*.instructions.md` exist and still use `applyTo` frontmatter correctly
- `AGENTS.md` exists and still reads like contributor guidance for this repository
- `.github/skills/*/SKILL.md` exist and still read like skill docs
- `.github/hooks/*.json` exist and still point at the right files
- `.github/agents/jac.agent.md`, if present, still reads like a real custom agent profile

## Reference material

- `docs/jack/inventory.json` matches current file paths after any move or rename
- `docs/jack/` still provides the longer rules, workflows, templates, examples, hook notes, and support docs
- public docs describe those files as reference material and manual fallback where appropriate
 - `docs/jack/hook-contract-schema-families.md` and `docs/jack/hook-enforcement-truth-matrix.md` capture the reconciled hook schema families and the runner ↔ contract enforcement mapping; see reconciliation batch closeouts in `docs/jack/` for the edit history.

## Truthful support claims

- repo-scoped files are described as repo-scoped
- user-scoped equivalents are labeled environment-specific
- hooks remain repo-scoped unless GitHub documents something broader
- no doc claims native runtime support for `docs/jack/inventory.json`
- no doc claims Markdown workflow files execute as commands unless GitHub documents that behavior

## File quality

- JSON parses cleanly and stays pretty-printed
- Markdown is readable
- referenced paths still exist
- hidden or bidirectional Unicode characters are absent
- line endings stay LF

