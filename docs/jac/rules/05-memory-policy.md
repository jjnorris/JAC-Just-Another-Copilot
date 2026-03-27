# Memory policy

## intent
Keep memory bounded, useful, and faithful to decisions instead of chat history.

## applies_when
- Storing or retrieving task context, knowledge items, and summaries.

## non-negotiables
- Working memory stays short and deterministic.
- Long-term memory is optional, bounded, and relevance-gated.
- Memory items must include title, summary, artifacts, and scope.
- Preserve decisions, constraints, rejected paths, and unresolved risks.

## warnings
- Chronological dumps crowd out current work.
- Retrieval without relevance checks floods context.

## blockers
- Silent mutation of requirements through summary rewrite.

## examples
- Good: store a compact note that a repo has no test harness.
- Bad: store a whole chat transcript as memory.

## interplay
Pairs with `12-reporting-and-traces.md`, `.github/skills/memory-manager/SKILL.md`, and `.github/hooks/context-budgeter.json`.
