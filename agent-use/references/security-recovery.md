# Security, safety, and recovery patterns

Agent-useful systems should be safe by construction. Agents can move quickly, retry aggressively, and compose tools in surprising ways. The interface must make correct, reversible, auditable behavior the path of least resistance.

## Risk levels

Classify every action.

| Level | Examples | Default requirement |
| --- | --- | --- |
| Read | list, get, search, inspect logs | scoped read permission, bounded output |
| Local reversible write | create draft, modify local file, update test fixture | preview/diff, version history |
| Remote reversible write | create project, update setting, archive item | scoped write permission, idempotency, audit log |
| Destructive or costly | delete, charge, deploy prod, rotate secrets, send external message | dry-run, explicit approval, rollback/soft delete where possible |
| Irreversible/high-impact | legal/financial/medical action, public broadcast, permanent deletion | human approval and often out-of-band controls |

## Least privilege

Good agent auth design:

- Read-only credentials are easy to create.
- Write scopes are granular.
- Destructive scopes are separate.
- Tokens can be limited by workspace/project/environment.
- Tokens expire and can be rotated.
- Permission errors identify the minimum missing scope.
- Docs show least-privilege examples for common tasks.

Bad patterns:

- One API key grants everything.
- Scopes are undocumented.
- Permission denied errors do not say what is missing.
- Agents must use a human’s full session cookie.

## Human approval

Approval should be explicit, reviewable, and proportional.

Good approval payloads include:

- Action name.
- Target object IDs and names.
- Parameters.
- Side effects.
- Risk level.
- Dry-run result or diff.
- Rollback plan.
- Expiry time.
- Requesting actor/agent.

Avoid vague approval prompts such as “Allow this action?” without a diff or target.

## Dry-run and preview

Dry-run should be a first-class execution mode, not a separate approximate validator.

A good dry-run returns:

- Whether the action would be allowed.
- Validation errors.
- Objects that would change.
- Estimated cost/time.
- External side effects.
- Warnings.
- Required approval level.
- Idempotency key or operation token that can be used to apply the approved change.

## Idempotency

Idempotency prevents duplicate side effects during retries.

Recommended patterns:

- Mutating create/update operations accept `Idempotency-Key` or equivalent.
- Server stores key, request hash, result, and expiry.
- Repeated identical request returns same result.
- Reused key with different request returns conflict.
- Response includes whether result was newly created or replayed.

CLI equivalent:

```bash
product project create --name staging --idempotency-key task-2026-06-29-staging --output json
```

Tool equivalent:

```json
{
  "idempotency_key": "task-2026-06-29-staging",
  "name": "staging"
}
```

## Error envelopes

Errors should be stable and actionable.

Recommended fields:

```json
{
  "error": {
    "code": "rate_limited",
    "message": "Too many requests for this token.",
    "retryable": true,
    "retry_after_seconds": 30,
    "remediation": "Retry after the indicated delay or reduce request rate.",
    "details": {
      "limit": 100,
      "window_seconds": 60
    },
    "correlation_id": "req_123"
  }
}
```

Common codes:

- `validation_failed`
- `permission_denied`
- `not_found`
- `conflict`
- `rate_limited`
- `temporarily_unavailable`
- `precondition_required`
- `approval_required`
- `idempotency_conflict`
- `partial_success`

## Retryability

Document retry behavior for every error class.

- Retryable: rate limit, timeout, transient upstream failure.
- Maybe retryable after state change: conflict, locked resource, precondition failed.
- Not retryable without user/action change: validation, permission, not found.

Give agents enough information to choose correctly.

## Long-running jobs

Use jobs for operations that may exceed request/command time.

Job model:

```json
{
  "job_id": "job_123",
  "status": "running",
  "progress": {
    "completed": 42,
    "total": 100,
    "message": "Processing files"
  },
  "created_at": "2026-06-29T10:00:00Z",
  "updated_at": "2026-06-29T10:01:00Z",
  "logs_url": "https://example.com/jobs/job_123/logs",
  "result_url": null,
  "retryable": true,
  "correlation_id": "req_123"
}
```

Add:

- Status endpoint.
- Cancellation endpoint when safe.
- Output links.
- Error details.
- Retention policy.
- Resume/checkpoint support for large work.

## Rollback and undo

Rollback options, from strongest to weakest:

1. Transaction rollback before commit.
2. Version history restore.
3. Soft delete and restore.
4. Compensating action.
5. Manual repair runbook.

Document which applies. If no rollback exists, require stronger preview and approval.

## Audit logs

Agent actions should be auditable.

Log:

- Actor/user/agent identity.
- Credential or integration ID.
- Timestamp.
- Action.
- Target object IDs.
- Parameters or redacted parameter summary.
- Dry-run/apply distinction.
- Approval record.
- Result.
- Correlation ID.
- Rollback link/status.

Do not log secrets or sensitive payloads unnecessarily.

## Sandboxes

A sandbox or test mode dramatically improves agent reliability.

Good sandbox properties:

- Similar schemas and errors to production.
- Fake external side effects.
- Easy reset fixtures.
- Clear visual/API distinction from production.
- Low-friction credentials.
- Examples use sandbox by default.

## Prompt-injection and untrusted content

Agents may ingest docs, user files, webpages, issue comments, emails, or logs that contain malicious instructions.

Interface mitigations:

- Separate data from instructions.
- Mark untrusted content in tool responses.
- Do not include secrets in broad context blobs.
- Require scoped tools and user approval for sensitive actions.
- Let agents cite/source retrieved content.
- Provide safe parsers and sanitizers for common file types.
- Avoid tools that execute code from untrusted content by default.

## Bot access policy

For public websites and APIs, document automation expectations:

- Which user agents/bots are allowed.
- Rate limits.
- Preferred docs/index endpoints.
- Whether markdown variants are available.
- How to authenticate.
- Contact/support for high-volume access.

## Safety review questions

Ask these before launch:

- What is the worst thing an agent can do with the default credential?
- Can a read-only task accidentally write?
- Can retries duplicate side effects?
- Can the agent preview a destructive action?
- Can a human see exactly what will change?
- Can the action be undone?
- Are permission failures actionable?
- Are logs sufficient for incident response?
- Are secrets excluded from contexts and logs?
- Are untrusted documents treated as data, not instructions?
