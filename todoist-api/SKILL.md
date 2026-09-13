---
name: todoist-api
description: >-
  Work with Todoist tasks and projects through the official td CLI or Todoist API
  v1. Use for explicitly requested Todoist capture, triage, bulk edits, completed-work
  reports, or integration development. Do not activate for generic reminders or
  tasks in another system.
license: MIT. See LICENSE.txt
compatibility: Requires authorised Todoist access. Routine operations use the official @doist/todoist-cli package; API integrations use HTTPS and the project's supported SDK/runtime.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Todoist workflows

Use the official CLI for routine operations. Use the public API only for a
specific integration or a gap confirmed in installed CLI help. Do not maintain
another complete client or silently switch the user's account/connection.

## Establish the surface

1. Prefer an already authorised Todoist connector when it exposes the requested
   operation. Otherwise inspect `td --version`, `td --help`, and `td auth status`.
2. The official package is `@doist/todoist-cli`, executable `td`. Installation and
   authentication change the host/account state; do them only as authorised.
3. Use OS credential storage, not a token in a command argument, report, or repo.
   `TODOIST_API_TOKEN` overrides stored credentials: check its presence without
   printing its value when the apparent account or permissions are wrong.
4. For read-only work, prefer read-only OAuth. CLI auth metadata is not proof
   that an externally supplied token has a particular scope.
5. Read the exact subcommand's help before use. Prefer its structured output;
   do not parse a human-formatted table or assume a flag exists across commands.

Doist maintains its own CLI skill (`td skill install universal`, or the relevant
agent target). Use that for exhaustive command syntax when available; installing
it is optional, not a prerequisite or permission to modify agent configuration.
This skill adds the resolution, bulk-change, and reconciliation workflow below.

## Resolve, execute, verify

```bash
td project list --json
td task list --project "Work" --json
td task view TASK_ID --json
```

Resolve names within their context: account/workspace, project, section, and
personal versus shared label. Preserve opaque string IDs. On duplicate names,
show the candidates; do not choose the first match. Never pass a `tmp-` client
placeholder to a server endpoint.

For an authorised capture, a simple example is:

```bash
td add "Email Chris tomorrow at 09:00 #Work @follow-up p2"
```

Read the resulting task and verify project, labels, parsed date/time, timezone,
and recurrence. Natural-language parsing is not proof the intended date was
stored. API priority numbering and user-facing `p1` notation are different;
verify their mapping rather than copying numbers between surfaces.

For edits, read current state, apply the requested change using installed help,
and read back the affected fields. Complete rather than permanently delete when
that matches the request. Completing a recurring occurrence and ending the
series are different operations; inspect the returned next due date.

## Bulk edits and recovery

Before bulk close/move/comment/delete, read
[API and bulk operations](references/API_AND_BULK.md). Freeze an explicit set of
IDs and proposed changes, preview it, and apply that set rather than re-running
a changing filter. Existing user authorisation can cover the plan; CLI flags or
plan files cannot grant extra permission.

Keep an outcome ledger of confirmed successes, confirmed failures, and unknown
outcomes. A timeout after a write is **unknown**, not evidence that nothing
happened. Reconcile before retrying. Never restart an entire partially completed
batch or regenerate deduplication IDs on recovery.

## Reports and integration work

For completed-work reports, define the timezone and interval, and distinguish
completion time from due date. Follow all returned cursors needed for the
request, or label the result partial. Do not mistake a page size for total count.

For Sync API, attachments, templates, archived resources, or migration work, use
the reference only after confirming the live endpoint/SDK contract. The old
custom Python CLI and its flags are removed; there is no compatibility shim.

Return what was found/changed, stable IDs or provider-returned links, verification
performed, unresolved outcomes, and pagination boundaries. Do not claim a
successful connection, write, or report from a command example alone.

## Sources and checks

Reviewed 2026-09-13 against [Todoist API v1](https://developer.todoist.com/api/v1/)
and the [official CLI](https://github.com/Doist/todoist-cli). Installed help and
current endpoint documentation remain the authority for exact syntax.

Maintainers: run the scenarios in [evals/scenarios.json](evals/scenarios.json)
against agent traces. They are evaluation cases, not a claim of live tests.
