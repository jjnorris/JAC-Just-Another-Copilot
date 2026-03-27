# JAC source pack

This directory is the longer source pack behind the repo-native Copilot files in:

- `.github/copilot-instructions.md`
- `.github/instructions/*.instructions.md`
- `AGENTS.md`

It is mostly rules, notes, templates, and JSON.
It is not the first thing to wire by hand if your Copilot environment already reads the repo-native adapter files.

## What is in here

- long-form instructions
- rules with one canonical home each
- workflow notes
- portable hook and skill contracts
- templates, schemas, docs, and examples
- internal metadata in `manifest.json`

## What `manifest.json` means here

`manifest.json` is portable source-pack metadata for this folder.
It is not presented as an official GitHub Copilot package manifest.

## What hooks and skills mean here

The `hooks/` and `skills/` directories describe behavioral contracts and future adapter targets.
They are not shipped as proven native Copilot runtime units in this repository.

## When to read this folder first

Read this folder first when you need the long-form policy text or when you are editing the source pack itself.
Otherwise, start with the repo-native adapter files and come back here when you need detail.
