# Compatibility notes

## Portable core

The following parts are intentionally portable and do not depend on a verified native Copilot runtime feature:

- markdown instructions and rules
- workflow documents
- templates
- JSON event contracts
- portable manifest metadata
- skill and hook definitions as behavioral contracts
- docs and examples

These files can be used manually, through editor notes, or through a custom adapter.

## Platform-specific assumptions

The following are not claimed as verified native GitHub Copilot features by this repository:

- global user-level installation of this exact package shape
- native execution of `hooks/*/hook.json`
- native registration of `skills/*/skill.json`
- native slash-command binding for `workflows/*.md`
- native acceptance of `manifest.json` as an official schema

If your environment supports some equivalent surface, adapt the pack carefully and document what was actually verified.

## Activation modes

JAC defines three conceptual activation modes:

- `always-on`: core instructions always apply
- `model-decision`: a router or user decides whether a skill or workflow is relevant
- `glob-pattern`: a workspace or adapter activates local rules by file pattern

These are policy modes. They are not proof of native runtime support.

## Fallback behavior

If advanced surfaces are unsupported:

- `instructions.md` stays authoritative
- `rules/` stay readable policy files
- `workflows/` stay manual procedural rails
- `hooks/` become review checklists and pseudo-hook contracts
- `skills/` become named behavior bundles for manual routing
- event contracts remain trace formats for local artifacts or logs

## Environment classes

### Local-first
Use direct file access, local tasks, local tests, and local notes. Prefer this mode.

### Remote or hosted
Use the same authority pack, but keep stronger scrutiny on secrets, networked actions, and credential boundaries.

### Degraded or offline
Skip semantic retrieval, remote research, or live telemetry. Keep working-memory-only behavior and local evidence notes.

## Versioning guidance

Increment this pack when:
- a rule meaning changes
- a schema changes
- a workflow pause point or blocker changes
- a compatibility claim is newly verified or withdrawn

Do not change compatibility claims casually.
