---
name: resend-cli
description: >-
  Operate Resend through its official CLI for authorised sends, hosted templates,
  domains, contacts, broadcasts, inbound email, webhooks, or Automations. Use for
  explicit Resend terminal/CI operations; use resend-api for application SDK code,
  not this skill for generic email or inbox tasks.
compatibility: Requires the official resend CLI and authorised Resend access for live operations. Discover the installed command surface before execution; no bundled Python wrapper is required.
metadata:
  version: "4.0.0"
  reviewed: "2026-09-13"
  source: "https://github.com/resend/resend-cli"
---

# Resend CLI operations

Use the maintained CLI directly. Its `commands` output replaces the old duplicated
command catalogue, task router, and Python wrapper. Preserve task-specific intent
and verification, not stale copies of every flag.

## Discover and scope

```bash
resend --version
resend --json commands
resend emails send --help
resend --json -q doctor
```

`doctor` can inspect the account; it is not a purely offline version check. Use an
already authorised connector instead when that is the available execution surface.
Do not install, log in, change profiles, or broaden credentials just to run a
read-only inspection. Check effective account/profile and token scope without
printing keys. Prefer a secret-store environment value or stored profile over
`--api-key` in arguments. Record the CLI version and help used.

For bounded automation, pass every required argument, `--json -q`, and capture
stdout, stderr, and exit status separately. Current machine output is success
JSON on stdout and errors on stderr; warnings may also occur. Exit zero and a
valid expected result are both needed. Stream listeners are not bounded JSON
commands. Do not concatenate output channels and pretend the result is one JSON
document. Inspect installed help when a flag or output shape differs.

## Choose the operation

| Intent | Surface | Verification |
| --- | --- | --- |
| One transactional email | `emails send` | Persist ID; inspect delivery result later |
| Distinct transactional messages | `emails batch` | Freeze payload, map returned IDs, reconcile failures |
| Hosted content | `templates` and `emails send --template` | Published version, variables, sender defaults |
| Marketing campaign | `broadcasts`, `segments`, `topics` | Exact audience/consent, preview, send status |
| Sender/receiving setup | `domains` | Returned DNS records and verified capabilities |
| Received message | `emails receiving` | Fetch full content/attachments after verified event |
| Event-driven email sequence | `automations`, `events` | Disabled draft, approved activation, run results |
| Credential/event delivery setup | `api-keys`, `webhooks` | Least privilege, secret storage, test delivery |

Exact flags come from `resend commands` and subcommand help, not this routing table.
Do not declare an operation unsupported just because a cached catalogue lacks it.
Use the API/SDK only after confirming a relevant CLI gap.

## Hosted-template send

Current `emails send` supports **`--template` and `--var`**. It is not necessary to
fall back to REST just to send a hosted template.

```bash
resend --json -q emails send \
  --template "$TEMPLATE_ID" --to delivered@resend.dev \
  --var CUSTOMER_NAME=Taylor --idempotency-key "$SEND_KEY" --dry-run
```

Resolve an actual published template and its variable definitions first. Supply
sender/subject when not defined by the template; verify overrides. Current CLI
`--var` values are strings: use an appropriate typed SDK/API payload when numeric
variable types matter. Do not combine template with raw body flags; the inspected
CLI also rejects attachments with templates. CLI restrictions need not imply the
same restriction on every API surface.

The dry run validates local input, not template existence, publication, permissions,
recipient authorisation, or delivery. Review its payload; remove `--dry-run` only
for the authorised send, retaining the same content and operation identity.

## Mutation and retry discipline

Confirm actual recipients, account, content, attachments, schedule/timezone, and
scope before sending. Drafting or previewing is not permission to send. Sending a
broadcast or firing a custom event may fan out to many recipients.

Persist a unique idempotency key and exact request **before** email/batch submission.
Retry the same operation with that key only within the provider's documented
window (currently 24 hours). New content is a new operation. After the window,
reconcile rather than replay; do not extend email idempotency guarantees to other
endpoints. A timeout may mean accepted-but-unacknowledged, not unsent.

Native `--dry-run` exists for specific commands (currently email send and broadcast
create), not every mutation. Inspect help; never emulate a preview by making a
live call. For unsupported previews, render the intended payload and recipients
locally without invoking the mutation.

Read [operational checks](references/OPERATIONS.md) for batching, domains,
subscriptions, receiving, streams, and Automations. Report IDs, confirmed state,
unknown outcomes, and next evidence needed. Accepted is not delivered, and
recorded delivery is not proof of inbox placement or human reading.

## Sources and evaluation

Reviewed against the [official CLI](https://github.com/resend/resend-cli),
[send source](https://github.com/resend/resend-cli/blob/main/src/commands/emails/send.ts),
and [API docs](https://resend.com/docs/api-reference/introduction) on 2026-09-13.
Evaluation cases: [evals/scenarios.json](evals/scenarios.json). They require agent
trace review; no live account access or send is implied by their presence.
