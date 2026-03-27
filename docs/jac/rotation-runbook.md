# Rotation runbook

Use this runbook when a token, credential, or secret-adjacent artifact might have been exposed.

## Trigger examples
- secret appears in output, trace, screenshot, or committed file
- insecure local config was created
- provider credential was shared in prompt context

## Immediate steps
1. Stop further distribution of the artifact.
2. Revoke or rotate the exposed credential.
3. Replace stored values with placeholders or secure references.
4. Record where the secret appeared and which artifacts must be cleaned.
5. Review logs, screenshots, and examples for copies.

## Recovery notes
- Prefer revocation over trying to prove non-exposure.
- Preserve minimal evidence needed for incident follow-up.
- Update local ignore patterns or secret handling docs if the event exposed a process gap.

## Reporting
Record:
- exposed secret type
- where it appeared
- revocation owner
- cleanup status
- follow-up prevention change
