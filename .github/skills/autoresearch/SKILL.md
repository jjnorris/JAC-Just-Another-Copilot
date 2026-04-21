---
name: autoresearch
description: Gather and structure external facts when repo truth is not enough.
---

# autoresearch

## Purpose
Gather and structure external facts when repo truth is not enough.

## When to use
- current facts required
- unverified platform behavior
- security or license question

## Inputs
- research question
- decision context

## Outputs
- cited findings
- trust grading
- fact vs inference split

## What it checks
- Prefer primary sources.
- Label untrusted sources.
- Do not trigger when repo truth already answers the question.

## Warnings
- Research can bloat context.
- Secondary summaries may distort technical facts.

## Blocks on
- Only weak or untrusted sources support a high-risk recommendation.

## Evidence expected or emitted
- research_source_used
- research_source_untrusted

## Examples
- Check official docs before claiming a native Copilot package surface.

## Limitations
- Falls back to: Local recommendation with uncertainty note and no external fetches.

## Boundary
- May recommend and cite. It may not convert speculation into verified platform support.

## Related docs
- `docs/jacks/rules/08-research-policy.md`
- `docs/jacks/workflows/research-with-citations.md`


