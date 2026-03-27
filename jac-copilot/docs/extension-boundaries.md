# Extension boundaries

An extension or editor integration may improve local ergonomics.
It may provide:
- commands
- CodeLens
- tree views
- panels
- task runners
- targeted diff, test, or trace views
- session continuation helpers

It must not become the authority engine.

## What stays in the authority pack
- policy
- review rules
- correctness rules
- memory rules
- trace contracts
- route and gate logic

## What stays in the surface
- display
- relay
- focused local interaction
- local-first task and test launching
- offline and degraded-mode UX

## v1 guidance
Do not try to rebuild an entire browser workbench.
Prioritize repo-native workflows, diffs, tests, targeted control-plane visibility, and continuation.
