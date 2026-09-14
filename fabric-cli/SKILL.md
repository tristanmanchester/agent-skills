---
name: fabric-cli
description: >-
  Operate the official Fabric.so CLI to search a selected workspace, save notes,
  links and files, manage tasks, or maintain explicitly authorised project memory.
  Use for Fabric.so terminal workflows. Not Microsoft Fabric, Python Fabric SSH,
  Fabric.js, or Daniel Miessler's Fabric framework.
compatibility: Requires the official fabric executable, shell access, and an authorised Fabric.so account for live operations. Installed subcommand help defines the available flags.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
  source: "https://fabric.so/guide/ai-tools/CLI-usage"
---

# Fabric.so CLI workflows

Use the native CLI directly or an already authorised Fabric connector when that
is the available surface. Do not wrap it in a second command catalogue or treat a
planner's `read` label as an access-control guarantee.

## Verify tool and workspace

```bash
fabric --version
fabric --help
fabric --json workspace current
fabric --json workspace list
fabric search --help
```

Verify this is Fabric.so, not another executable with the same name. Help/version
checks are local; workspace checks access account state. Check exit status and the
returned workspace before any write. A workspace name may be ambiguous; preserve
provider IDs where exposed. Switching workspace changes persistent CLI context:
serialise operations or use a documented per-command scope, and recheck the target.

The official installer is `https://fabric.so/cli/install.sh`. Download and inspect
it before an authorised installation; do not pipe remote code into a shell by
default. Prefer browser login for setup. `fabric auth <api-key>` puts a secret in
process arguments/history; use a supported protected authentication route and
never log or copy credentials into notes. Do not invent environment support that
the installed CLI has not documented.

## Search and retrieve evidence

```bash
fabric --json search "project notes"
fabric --json search "design" --tag work
fabric --json path
fabric --json path "Inbox/Reports"
```

Use search for candidate content and path browsing for known folders. Keep query,
tag, workspace, and pagination limitations visible. A snippet is not the full
source. For a detailed summary, retrieve original content through a supported
CLI/API/connector action. Do not silently substitute the Fabric AI assistant's
interpretation for the source document or assume a search is exhaustive.

**`fabric ask` is delegated agent execution.** Its documented purpose includes
asking the assistant to do things. A natural-language 'read-only' prompt or the
old `ask-read` planner label does not disable tools, writes, or paid inference.
Use it only with deliberate scope; use actual resource reads for evidence.

## Save the exact content and type

For authorised writes, use `note`, `link`, or `file` when the type is known.
`save` auto-detects type: text resembling a path can upload a file instead of
creating a note. Verify that inference before using it.

```bash
fabric --json note --parent "Work/Projects" < "/private/output/reviewed-note.md"
fabric --json link "https://example.com" --title "Reference" --parent "Work/Reading"
fabric --json file "/absolute/path/reviewed-report.pdf" --parent "Work/Reports"
```

The note command's positional text is the **body**, not a title. Set a separate
title only through a flag advertised by the installed command. Inspect the exact
bytes and attachment scope before upload, preserve destination constraints, and
retain the returned ID. Verify the created resource by ID where supported;
search indexing delay can make absence inconclusive.

## Tasks and mutations

Read `fabric --json task list` and resolve the exact task before completion/edit/
delete. Use current `task help` for fields, priority, due date, and identifiers.
Keep due dates distinct from reminder delivery and timezone-bearing times. Preview
an explicit ID set for bulk operations; do not rerun a changing query as the plan.
Deletion, workspace changes, and remote assistant execution need actual user
scope, not permission inferred from a flag or bundled recipe.

Check stdout, stderr, exit status, and the expected response shape separately.
**Never rerun a mutation without `--json` merely because parsing failed.** It may
already have succeeded. Capture the original result, reconcile by ID/current
state, and report unknown outcomes. Retry bounded reads when appropriate; no
undocumented idempotency is assumed for creates, saves, or delegated asks.

## Project memory

Use [memory and handoff](references/MEMORY.md) only when the user or established
project instructions authorise persistent Fabric memory. Retrieve a small relevant
set, preserve provenance, and draft a compact note before saving it. Do not upload
raw conversations or trust a heuristic redactor to remove all secrets.

## Finish with evidence

Report the verified workspace, found/changed IDs, relevant source content, and
unresolved outcomes. Generated completion scripts are executable shell code;
inspect them before sourcing or editing shell startup files. No CLI command in
this skill has been authenticated merely because its syntax appears here.

Current official source, reviewed 2026-09-13:
[Fabric CLI guide](https://fabric.so/guide/ai-tools/CLI-usage).
For application SDK work use `fabric-api`, not these terminal recipes.
