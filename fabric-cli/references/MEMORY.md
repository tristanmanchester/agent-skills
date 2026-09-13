# Project memory and handoff

Use Fabric memory when explicitly selected by the user or established project
instructions. Ordinary conversation does not authorise saving private content to
a remote workspace. Retrieve only the project/topic context needed now.

## Retrieve

Start with the project and a meaningful tag or phrase. Broaden only for a specific
missing fact. Read original relevant notes before summarising; distinguish accepted
decisions, proposals, historical notes, and observations. Newer does not always
mean authoritative. Preserve source IDs/links, dates, and any conflicts.

Do not use `fabric ask` as an automatically read-only fallback. It delegates to an
assistant that can act. Use a genuine content-read surface, or report the missing
retrieval capability without inventing the unseen contents.

## Draft and save

Write a compact note containing only future-useful material:

```markdown
# Project handoff

As of: YYYY-MM-DD, timezone
Project/workspace: verified name and ID when available

## Current state
What is actually implemented or observed; relevant artefact/commit IDs.

## Decisions
Accepted decision, rationale, and source. Label proposals separately.

## Open questions and next actions
Unresolved issue, owner when known, and the next verifiable step.

## Sources
Original resource IDs/links and evidence dates.
```

Adapt sections to the task; omit empty placeholders. An agent-written note is a
summary, not a new authority overriding source decisions. Do not store secrets,
private signed URLs, unnecessary personal details, or large diagnostic dumps.
Review content before the authorised save; automatic pattern redaction is not a
confidentiality guarantee.

Use the project's existing tags. Do not invent a new universal taxonomy or change
old notes merely for consistency. Save reviewed text through `note` using stdin;
smart `save` can infer a different resource type. Persist its returned ID and
verify destination/content. On failure after submission, reconcile before retrying.

When a decision changes, record what supersedes what with dates and links. Do not
silently rewrite historical evidence. Deletion or retention changes require their
own authorised scope.

## Maintainer evaluation cases

Review actual agent traces for: ambiguous Fabric product; wrong active workspace;
note body mistaken for title; private local path passed to smart save; malformed
JSON after a successful create; delegated ask misclassified as a resource read;
conflicting historical decisions; and a conversation with no memory-write consent.
Expected outcome is correct scope and verified results, not a fixed command count.
These are test scenarios, not reported evaluations.

Source: [official CLI guide](https://fabric.so/guide/ai-tools/CLI-usage), reviewed
2026-09-13. Memory organisation is this skill's workflow, not a Fabric API guarantee.
