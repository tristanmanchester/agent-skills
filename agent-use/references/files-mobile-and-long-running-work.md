# Files, mobile, and long-running work

## Files as universal interface

Files are often the simplest shared workspace. Good file-based agent surfaces have stable paths, clear ownership, explicit generated-file markers, sidecar metadata where needed, atomic writes, diffs/previews, and validation commands.

Good patterns:

- `AGENTS.md` documents where agents may edit.
- Generated files are clearly marked and reproducible.
- Long outputs are written as artifacts and linked.
- State files use JSON/YAML/CSV/Markdown with schemas where possible.
- Checkpoints are durable and recoverable.

## Self-modification

Self-modifying systems need guardrails: version control, branches, tests, rollback, human review for risky changes, changelogs, and clear distinction between policy/prompt changes and executable code changes.

## Mobile and offline constraints

Mobile agent surfaces must account for battery, network loss, OS background limits, permissions, storage sandboxes, and user-visible approval. Work should checkpoint before suspension, resume safely, avoid unbounded background activity, and expose status when the app foregrounds.

## Long-running jobs

Long tasks need a lifecycle contract: create/start, status, logs/events, artifacts, checkpoint, cancel, resume, completion signal, error envelope, and final verification.

Minimum task object:

```json
{
  "task_id": "task_123",
  "status": "running",
  "progress": 0.4,
  "checkpoint": "after-validation",
  "resume_token": "res_abc",
  "artifacts": [],
  "next_action": "poll status or wait for webhook"
}
```
