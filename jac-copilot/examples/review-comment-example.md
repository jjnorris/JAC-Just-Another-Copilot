# Review comment example

```json
{
  "task_id": "task-42",
  "review_mode": "request_review",
  "status": "comment",
  "scope": "dependency change for workspace adapter",
  "risk_class": "heightened-scrutiny",
  "approval_needed_for": ["dependency shift"],
  "comments": [
    {
      "id": "rc-1",
      "severity": "warning",
      "message": "Document the rollback path and license impact before proceeding.",
      "required_before_proceed": true
    }
  ]
}
```
