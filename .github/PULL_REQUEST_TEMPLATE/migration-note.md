## Migration note
This change removes support for the JACK_REVIEW_OK environment variable. Instead, the hooks require server-verified review artifacts.

What to include in this PR:
- Files changed that remove or replace JACK_REVIEW_OK usage (workflows, CI, docs).
- Configuration updates made and how to test them.
- Verification steps for reviewers (e.g., run a pipeline with JACK_REVIEW_OK unset and confirm hooks block until a review artifact is present).

Reference: docs/jack/deprecate_jack_review_ok.md
