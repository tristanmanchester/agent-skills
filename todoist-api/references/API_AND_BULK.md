# API gaps, bulk operations, and recovery

## Choose a supported route

Use the official CLI/connector for supported tasks, projects, sections, labels,
and comments. For programmatic integration use the official SDK appropriate to
the project, checking its installed method signatures and retry behaviour. For
an unsupported endpoint, consult [API v1](https://developer.todoist.com/api/v1/)
and make a deliberately bounded HTTPS request to `https://api.todoist.com/api/v1`.
Do not send credentials to arbitrary URLs, follow credential-bearing redirects,
or add automatic retries around an SDK that may already retry internally.

Read operations may use bounded backoff respecting the server's rate-limit
response. Writes need the endpoint's documented deduplication contract; being
HTTP POST, sending a made-up request-ID header, or using a unique task name does
not establish idempotency. On an ambiguous result without that contract, stop,
read current state, and report unresolved ambiguity rather than guessing.

## Bulk plan

Record the query and selection time, IDs, relevant current values, proposed
changes, and expected count. Resolve every destination before writing. Store
these personal task details privately, not in a public source repository.

Example plan shape (illustrative, not a CLI input format):

```json
{
  "operation": "move",
  "selection": ["task-id-a", "task-id-b"],
  "destination": {"project_id": "project-id", "section_id": "section-id"},
  "expected_count": 2
}
```

Re-read each target before applying. Skip an already-satisfied change. Stop on
an unexpected identity, changed precondition, missing target, or permission
failure. A read-then-write check is not an atomic lock: use server preconditions
where supported and disclose a concurrency window where they are not.

For create-if-missing, resolve within the correct parent, create only after no
match is found, and read back. This is not uniqueness enforcement across
concurrent clients. Never replay repeated comments after a timeout merely
because the client did not receive the new comment ID.

## Sync API

The current `/sync` surface uses some different names from REST (`items`,
`notes`). Use the documented command type, not a mechanical REST-name conversion.

For each logical write command, persist a unique `uuid` **before sending**, along
with the exact command and arguments. The Sync API documents deduplication by
command UUID. Recovery reuses the same UUID for that same command; a changed
operation gets a new UUID. Creation commands may use `temp_id`, resolved through
`temp_id_mapping`; these are not the unsynced UI's `tmp-` placeholders.

Inspect `sync_status` for every submitted UUID, including missing entries and
per-command errors. HTTP 200 does not make a batch wholly successful. Persist
confirmed outcomes; reconcile unknowns with the original command identities.
Do not assert batch atomicity.

For incremental reads, retain the returned sync token only after applying the
corresponding changes durably. Record the selected resource types. Follow the
provider's invalid-token/full-resync handling without silently dropping local
uncommitted intent.

## Less-common operations

- **Completed work/activity:** pick completion-time or due-date semantics, an
  explicit timezone, a bounded interval, and all necessary cursors. Record plan
  restrictions and permission failures rather than converting them to emptiness.
- **Archived resources:** include them deliberately when resolving old names;
  do not unarchive as a side effect of searching.
- **Uploads/templates/backups:** verify endpoint, file type, limits, scopes, and
  whether it creates remote state. A template export is not a full account backup.
  Treat returned download URLs as private and never attach a Todoist bearer token
  to a different host just because the URL came from an API response.
- **ID migration:** use a currently documented mapping endpoint when needed;
  preserve IDs as strings and never infer a mapping from numeric appearance.

## Source

[Official API](https://developer.todoist.com/api/v1/), especially Write resources,
Command UUID, Response / Error, and the exact endpoint used. Reviewed 2026-09-13.
