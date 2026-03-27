# JAC

JAC stands for Just Another Copilot.

This is a small pile of rules, notes, templates, and JSON for steering GitHub Copilot in a more careful direction.
It is not a verified native Copilot package format.
It is mostly a portable authority pack that you can adapt to whatever instruction surface your editor actually supports.

## What it is

- a user-level rules pack
- a set of workspace-override patterns
- some workflow documents
- some pseudo-hook and pseudo-skill definitions
- a few schemas and templates for traces, review, memory, and verification

## What it is not

- not an official GitHub format claim
- not proof that Copilot runs hooks from this folder
- not proof that global install works the same everywhere
- not a runtime or extension by itself

## Install idea

1. Put this folder somewhere stable.
2. Point whatever reusable Copilot instruction surface you have to `instructions.md`.
3. Layer workspace rules on top when your editor supports that.
4. If your editor does not support any of that cleanly, open the workflow docs manually and use them as operating notes.

More detail is in `install.md` and `compatibility.md`.

## Layout

- `instructions.md` is the main file
- `rules/` holds narrow policies with one canonical home each
- `workflows/` holds step-by-step operating rails
- `skills/` and `hooks/` describe portable behaviors, not guaranteed native runtime features
- `event-contracts/` defines trace payloads
- `templates/` holds reusable review, assumption, rollback, and verification shapes
- `docs/` explains the design choices and boundaries
- `examples/` shows how to adapt the pack locally

## Why it exists

Mostly so Copilot does not bluff, overreach, or quietly skip the boring parts.

## Donation

If this saved you some time, you can buy me a coffee here: https://example.com/coffee
