# JAC supporting canon

This directory is the longer canon behind the repo-native Copilot files in:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `.github/skills/*/SKILL.md`
- `.github/hooks/*.json`
- `AGENTS.md`

It is mostly rules, notes, templates, and JSON.
It is not the first thing to wire by hand if your Copilot environment already reads the native repo files.

## What is in here

- long-form instructions
- rules with one canonical home each
- workflow notes
- templates and event contracts
- examples
- hook contract notes under `hook-contracts/`
- inventory metadata in `source-pack-registry.json`

## What `source-pack-registry.json` means here

`source-pack-registry.json` is maintenance metadata for this folder and its native adapters.
It is not presented as an official GitHub Copilot package manifest.

## What does not live here anymore

Native skill folders live in `.github/skills/`.
Native hook configuration lives in `.github/hooks/`.
This folder keeps the longer rationale behind them.

## When to read this folder first

Read this folder first when you need the long-form policy text or when you are editing the canon itself.
Otherwise, start with the native repo files and come back here when you need detail.
