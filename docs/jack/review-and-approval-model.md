# Review and approval model

JACK uses two execution zones.

## Autonomous zone
Low-risk, bounded, reversible work may proceed after a review artifact marks `always_proceed`.
Typical examples:
- narrow doc edits
- small config-neutral refactors
- local file organization that does not change runtime behavior

## Approval zone
The following require explicit review or approval before execution:
- deleting files
- broad refactors
- dependency shifts
- secrets or config changes
- schema migrations
- extension installation
- permission escalation
- deploy-like actions

## Review artifact requirements
A review artifact must include:
- scope
- correctness contract
- plan steps
- evidence plan
- risk class
- rollback notes when relevant
- approval-needed actions
- proceed vs review-comment path

## Comment path
Task-scoped review comments are first-class.
They are not casual chat.
A comment should identify:
- concern
- severity
- exact blocker or warning
- expected remediation
- whether it must be resolved before proceeding

## Final authority
Human approval is final for approval-zone work.
The agent may prepare the artifact and route the decision, but it may not self-approve blocked actions.
