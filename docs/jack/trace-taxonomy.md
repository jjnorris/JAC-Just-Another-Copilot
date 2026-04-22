# Trace taxonomy

JACK traces meaningful actions instead of relying on vague narration.

## Event families

### Agent trace
Used for assumptions, clarification, research use, route selection, and usage records.
See `docs/jack/event-contracts/agent-trace.schema.json`.

### Review events
Used for review requests and applied review comments.
See `docs/jack/event-contracts/review-events.schema.json`.

### Tool events
Used for denials, budget breaches, changed tool definitions, unresolved dependencies, and secret or PII detections.
See `docs/jack/event-contracts/tool-events.schema.json`.

### Memory events
Used for retrieval and recording of bounded knowledge items.
See `docs/jack/event-contracts/memory-events.schema.json`.

### Correctness events
Used for coverage misses, orphan wiring claims, and duplicate abstraction warnings.
See `docs/jack/event-contracts/correctness-events.schema.json`.

## Minimum event list
- assumption_added
- clarification_requested
- clarification_resolved
- review_requested
- review_comment_applied
- duplicate_abstraction_candidate
- pii_detected
- unresolved_dependency
- tool_permission_denied
- budget_exceeded
- research_source_used
- research_source_untrusted
- coverage_miss
- wiring_claim_orphan
- changed_tool_definition_detected
- model_route_chosen
- usage_recorded
- memory_retrieved
- memory_recorded

If native telemetry is unavailable, emit these as local JSON artifacts or structured report sections.
