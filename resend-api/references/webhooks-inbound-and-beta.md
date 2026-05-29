# Webhooks, inbound email, and beta APIs

## Webhooks

Stable webhook endpoints:

- `POST /webhooks`
- `GET /webhooks`
- `GET /webhooks/{webhook_id}`
- `PATCH /webhooks/{webhook_id}`
- `DELETE /webhooks/{webhook_id}`

Create-webhook essentials:

- `endpoint` — required
- `events` — required array with at least one event type

The create/retrieve/list flow returns a `signing_secret`. Keep it secure and use it to verify every
incoming webhook before trusting the payload.

## Verify signatures before parsing

Recommended verification approach:

1. read the **raw** request body bytes exactly as received
2. extract the Svix headers:
   - `svix-id`
   - `svix-timestamp`
   - `svix-signature`
3. verify the signature with the webhook signing secret
4. only then parse the JSON payload

If the raw body is altered before verification, signature checks can fail.

## Event types to expect

The docs show webhook coverage for email, domain, and contact events. Common email events include:

- `email.sent`
- `email.delivered`
- `email.delivery_delayed`
- `email.failed`
- `email.bounced`
- `email.complained`
- `email.opened`
- `email.clicked`
- `email.scheduled`
- `email.suppressed`
- `email.received`

Also expect domain/contact lifecycle events in webhook-capable accounts.

## Retry and replay behaviour

Resend documents automatic retries plus dashboard/manual replay support.

Operational guidance:

- make webhook handlers idempotent
- log the webhook event ID and affected resource ID
- return a fast 2xx once the event is durably queued
- use replay when backfilling or recovering from handler outages

## Inbound / receiving email

Receiving can use either:

- a `*.resend.app` domain
- a custom domain/subdomain you control

Recommended flow:

1. enable receiving on a domain
2. point the MX records as instructed by Resend
3. create a webhook subscribed to `email.received`
4. when a webhook fires, fetch the full message and attachments through the receiving endpoints

Important nuance: the inbound webhook payload contains **metadata**, not the full email body,
headers, or attachment bytes. To get the actual content, call:

- `GET /emails/receiving`
- `GET /emails/receiving/{email_id}`
- `GET /emails/receiving/{email_id}/attachments`
- `GET /emails/receiving/{email_id}/attachments/{attachment_id}`

If the receiving domain is a root domain that already depends on existing MX records, prefer a
dedicated subdomain for inbound routing.

## Sent-email attachments

For sent email inspection or audits, the stable API also exposes:

- `GET /emails/{email_id}/attachments`
- `GET /emails/{email_id}/attachments/{attachment_id}`

Use `--output FILE` with the bundled helper when retrieving binary attachment content.

## Beta: Workflows and Events

The Resend docs describe Workflows and Events as **private alpha / beta** functionality. Treat them
as unstable until the user's account and SDK version are confirmed.

### Workflows

Documented workflow notes include:

- create workflows via `POST /workflows`
- workflow shape includes `name`, `status`, `steps`, and `edges`
- documented step types include:
  - `trigger`
  - `send_email`
  - `delay`
  - `wait_for_event`
  - `condition`
- workflow runs can be inspected with:
  - `GET /workflows/{workflow_id}/runs`
  - `GET /workflows/{workflow_id}/runs/{run_id}`

### Events

Documented event notes include:

- create events via `POST /events`
- events can define a flat schema
- schema field types include `string`, `number`, `boolean`, and `date`
- dot notation is recommended for event names such as `cart.abandoned`

### Preview SDK note

The docs mention a preview Node SDK version for workflows/events:

- `resend@6.10.0-preview-workflows.1`

Do not silently generate production rollout plans around workflows/events without explicitly stating
their pre-GA status.

## Minimal webhook example flow

1. create the webhook
2. persist the signing secret
3. verify signatures against the raw body
4. make handler processing idempotent
5. for inbound events, fetch the full message after verification

## Useful assets

- `assets/create-webhook.json`
- `assets/endpoint-catalog.json` (includes beta notes)
