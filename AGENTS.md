# JACK contributor notes

For contributors and coding agents working on this repository.

## How to work in this repo

- Write each file for its actual audience and purpose.
- Keep public docs plain, practical, and understated.
- Use `docs/jack/` when you need the longer rule set, rationale, or support notes.
- Keep GitHub Copilot support claims narrow and verified.
- Use precise scope terms: `repo-scoped`, `user-scoped`, `cross-project`, and `environment-specific`.
- Prefer small, reversible edits over broad rewrites.
- Do not add outside-product stories or unsupported runtime claims.

## What to validate

This repository does not have an application build or test suite.
Validate the files it actually ships:

- JSON parses cleanly and stays pretty-printed
- referenced paths still exist after moves or renames
- Markdown stays readable
- repo-facing files still agree with the longer docs in `docs/jack/`
- hidden or bidirectional Unicode characters are absent
- line endings stay LF

## When to pause instead of bluffing

Pause when:

- a GitHub Copilot support claim cannot be verified
- two docs disagree about scope or support boundaries
- a destructive or approval-zone action appears without approval
- a security, secret, or license concern becomes blocking
