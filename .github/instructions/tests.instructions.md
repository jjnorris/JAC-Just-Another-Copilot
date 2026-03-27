---
applyTo: "README.md,.github/copilot-instructions.md,.github/instructions/**/*.instructions.md,AGENTS.md,jac-copilot/manifest.json,jac-copilot/**/*.json,jac-copilot/**/*.md"
---

This repository does not have an application test suite.
Do not invent one.
Use targeted validation instead.

For meaningful changes, validate the things this repo actually ships:

- JSON parses cleanly
- JSON stays pretty-printed
- Markdown stays readable
- manifest registry paths still exist when source-pack files change
- native adapter files exist and still reflect the source pack
- verified GitHub Copilot surfaces are described honestly
- portable-only files are clearly marked as portable-only
- hidden or bidirectional Unicode characters are absent and line endings stay LF
- the donation note uses either a real link or the explicit placeholder token
