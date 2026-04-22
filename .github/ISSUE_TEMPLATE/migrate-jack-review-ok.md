---
name: Migrate from JACK_REVIEW_OK
about: Guidance to remove JACK_REVIEW_OK env var usage and migrate to server-verified review artifacts
---

## Summary
Describe where JACK_REVIEW_OK was used (workflows, CI settings, environment variables).

## Migration checklist
- [ ] Locate all uses of JACK_REVIEW_OK (workflows, CI, deployment configs).
- [ ] Remove the JACK_REVIEW_OK environment variable or stop setting it.
- [ ] Update workflows to rely on server-verified review artifacts (see docs/jack/deprecate_jack_review_ok.md).
- [ ] Run repository checks and verify JACK hooks enforce review requirements.

## Notes
Link any PRs or CI changes that are required and add testing notes.
