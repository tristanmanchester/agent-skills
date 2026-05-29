---
name: resend-api
description: "Use this skill when the user wants to integrate with, call, debug, or operate the Resend API or official SDKs/MCP tooling. Covers sending and scheduling emails, batch sends, templates, domains and DNS verification, API keys, contacts, segments, topics, broadcasts, inbound email, webhooks, receiving attachments, and Resend workflows/events. Also use it when the user mentions Resend, resend.emails.send, verified domains, email.received, broadcast campaigns, template publishing, or needs help choosing between single email, batch, broadcast, inbound, or workflow patterns."
compatibility: "Designed for skills-compatible coding agents. Live API calls require network access and a RESEND_API_KEY. The bundled helper script uses Python 3.10+ standard library only."
metadata:
  author: OpenAI
  version: "1.0.0"
  source: "https://resend.com/docs/api-reference/introduction"
  last-reviewed: "2026-03-13"
---


# Resend API

Use this skill for tasks that specifically involve Resend's API, SDKs, webhook model, receiving
API, or official agent-facing tooling. Do **not** use it for generic email-platform advice unless
the user is clearly working with Resend.

## Read only what you need

Start with the smallest relevant file instead of loading everything.

- `references/core-reference.md` — auth, headers, rate limits, pagination, idempotency, error triage
- `references/sending-and-templates.md` — transactional sends, batch sends, scheduling, templates
- `references/domains-and-api-keys.md` — verified domains, DNS records, regions, tracking, key scope
- `references/contacts-broadcasts-and-subscriptions.md` — contacts, segments, topics, properties, broadcasts
- `references/webhooks-inbound-and-beta.md` — webhook verification, receiving, replay/retry, workflows, events
- `assets/endpoint-catalog.json` — compact stable-endpoint catalogue plus beta notes
- `assets/resend-openapi.yaml` — raw stable OpenAPI snapshot for deeper schema inspection
- `assets/*.json` — reusable payload templates for common operations

## Quick routing

Choose the product primitive before generating code or making live calls.

1. **Single transactional email** → `POST /emails`
2. **Many distinct sends in one call** → `POST /emails/batch`
3. **Campaign to a segment or list** → Broadcasts + Segments + Topics
4. **Reusable content** → Templates
5. **Verified sender domain or receiving domain** → Domains
6. **Scoped credentials** → API Keys
7. **Subscriber model and profile data** → Contacts, Topics, Contact Properties, Segments
8. **Inbound email processing** → Receiving Emails API + `email.received` webhook
9. **Event delivery to your app** → Webhooks
10. **Custom event-driven automations** → Workflows + Events, but treat them as beta/private alpha

## Workflow

### 1) Identify the job type

Classify the request first:

- **Code generation** — add or edit Resend integration code in an existing project
- **Live API execution** — make a real call against a Resend account
- **Debugging** — explain an error, fix a payload, or diagnose a failed flow
- **Architecture** — choose between Resend features and design the right flow

### 2) Choose the best execution surface

Prefer the most native surface for the user's environment:

- If the project already uses an official Resend SDK, generate or modify code in that language.
- If the user wants a reproducible example or is stack-agnostic, prefer raw REST or cURL.
- If the environment already has the official Resend MCP server installed, it is fine to use it
  for live operations, but still follow the payload and workflow guidance in this skill.

### 3) Before any live request

Always do these checks for real API calls:

1. Load `references/core-reference.md`.
2. Confirm `RESEND_API_KEY` is present.
3. Use `python3 scripts/resend_api.py schema METHOD PATH` if you need an offline schema summary.
4. Use `python3 scripts/resend_api.py request ...` or an equivalent HTTP client for the live call.
5. Include `Authorization: Bearer ...` and a `User-Agent`.
6. For `POST /emails` and `POST /emails/batch`, add an `Idempotency-Key` before any retry.
7. Avoid automatic retries on unsafe mutations unless idempotency is in place.

### 4) Generate code or payloads

When writing code or examples:

- Keep them minimal, runnable, and explicit about required environment variables.
- Use absolute ISO 8601 timestamps for scheduling.
- Call out feature limits that affect the request shape.
- Mention the exact endpoint(s), payload keys, and next verification step.
- Use the sample payload files in `assets/` as a starting point when helpful.

### 5) Debug in the right order

When something fails, inspect these first:

1. Wrong or missing API key
2. Missing `User-Agent` on raw HTTP
3. Unverified or test-only sender domain
4. Retried send without idempotency
5. Invalid attachment or from-address format
6. Batch limitations (no attachments, no scheduling)
7. Template not published before send
8. Expecting full inbound message content directly inside the webhook payload

### 6) Special handling rules

- **Scheduling**: use an exact timestamp and mention the 72-hour limit.
- **Templates**: publish before sending; if a template is used, do not also send raw `html` or `text`.
- **Subscriptions**: prefer Topics + Segments over deprecated Audiences.
- **Receiving**: treat the webhook as the trigger; fetch the full message and attachments via the
  receiving endpoints.
- **Webhooks**: verify the signature against the raw request body before parsing JSON.
- **Workflows/Events**: explicitly label them as beta/private alpha and confirm availability before
  proposing them as production-critical building blocks.

## Bundled tools

### `scripts/resend_api.py`

The bundled helper script is designed for agents:

- `catalog` — list stable endpoints from the bundled catalogue
- `schema` — show a compact schema/parameter summary for an endpoint
- `request` — make a live request with auth, user-agent, JSON parsing, optional pagination, and
  cautious retry behaviour

Examples:

```bash
python3 scripts/resend_api.py catalog --group Emails
python3 scripts/resend_api.py schema POST /emails
python3 scripts/resend_api.py request GET /domains
python3 scripts/resend_api.py request POST /emails --json-file assets/send-email.json --idempotency-key welcome-001
python3 scripts/resend_api.py request GET /emails --paginate --page-limit 3
```

## Common pitfalls

- Using `/emails/batch` when attachments or scheduling are required
- Forgetting that `/emails` is the right primitive for one logical email, even when `to` is an array
- Generating template-send code before the template has been published
- Using deprecated Audiences for new subscriber flows
- Expecting inbound webhooks to include the full raw message or attachment bytes
- Treating beta workflow/event APIs as stable
- Ignoring the default per-team rate limit and flooding the API with parallel requests

## Output expectations

When this skill is active, return:

1. The **exact endpoint(s)** involved
2. The **minimal payload or code** needed
3. The **operational caveats** that matter for this task
4. The **next verification step**, such as listing resources, confirming DNS records, or replaying
   a webhook

## Example prompts this skill should handle

- “Add Resend to this Next.js app and send a scheduled password-reset email”
- “Why is my raw Resend API call returning 403?”
- “Create a verified sending domain in eu-west-1 and turn receiving on”
- “Set up topic-based newsletter subscriptions with contacts and broadcasts”
- “Build an inbound email webhook for support@”
- “Should I use batch sends, broadcasts, or templates for this flow?”
- “Can Resend workflows wait for a custom event and then send follow-ups?”