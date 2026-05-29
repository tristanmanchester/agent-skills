# Sending and templates

## Choose the right sending primitive

### `POST /emails`

Use this for **one logical email send**.

Good fit for:

- transactional emails
- one message to up to 50 direct recipients
- sends that require attachments
- sends that require `scheduled_at`
- sends scoped to a `topic_id`
- sends that use a published template

Important request fields:

- required: `from`, `to`, `subject`
- content: `html`, `text`, or `template`
- optional: `cc`, `bcc`, `reply_to`, `headers`, `attachments`, `tags`, `scheduled_at`, `topic_id`

### `POST /emails/batch`

Use this for **many distinct email objects in one API call**.

Good fit for:

- personalised transactional messages for many recipients
- queueing up to 100 separate email payloads per request

Important restrictions:

- `attachments` are not supported
- `scheduled_at` is not supported
- use an `Idempotency-Key` when retries are possible

### Broadcasts

Use Broadcasts when the target is a **segment/list**, not a one-off transactional send.

Broadcast flow:

1. create or update Contacts
2. define Topics and Contact Properties if needed
3. define a Segment
4. create a Broadcast
5. send immediately or schedule it

Broadcast request notes:

- required: `from`, `subject`, `segment_id`
- `send: true` can send immediately
- `scheduled_at` can be used when `send` is true
- `topic_id` scopes the unsubscribe and topic behaviour

## Scheduling rules

Resend documents these constraints for scheduled sends:

- timestamps must be ISO 8601
- scheduled sends can be at most 72 hours in the future
- cancelled scheduled emails cannot be rescheduled
- scheduled sends do **not** support:
  - batch emails
  - SMTP sends
  - emails with attachments

Use `/emails/{email_id}/cancel` to cancel a scheduled email.
A `PATCH /emails/{email_id}` endpoint exists for updating a scheduled email, but check the latest
schema/docs before assuming which fields are mutable.

## Attachments

For transactional `POST /emails`:

- attachment payloads may include file content, filename, hosted path, content type, and content ID
- total attachment size is constrained by Resend's documented 40 MB limit **after base64 encoding**
- if you expect binary responses when retrieving attachments, prefer `--output FILE` with the
  bundled script

## Tags

Tags are useful for downstream analytics and event handling.

Tag rules from the stable schema:

- `name` and `value` may contain ASCII letters, numbers, underscores, or dashes
- each field can be at most 256 characters

## Template lifecycle

Templates are draft resources until published.

Recommended flow:

1. `POST /templates` — create draft
2. `PATCH /templates/{id}` — refine it
3. `POST /templates/{id}/publish` — publish it
4. `POST /emails` with `template.id` or template alias logic in your own app

Template sending rules:

- if you use `template`, do **not** also send raw `html` or `text`
- the template must already be published
- `from`, `subject`, and `reply_to` in the email send payload override template defaults

## Template variables

Documented constraints to keep in mind:

- keys should be kept small and predictable
- values on send are string/number pairs in the send payload
- Resend documents reserved variable names on template/send docs; avoid these across templates and
  payloads:
  - `FIRST_NAME`
  - `LAST_NAME`
  - `EMAIL`
  - unsubscribe-related reserved names
  - `contact`
  - `this`

When in doubt, use application-specific keys such as `customer_name`, `cta_url`, `plan_name`.

## Minimal examples

### cURL single send

```bash
curl -X POST https://api.resend.com/emails   -H "Authorization: Bearer $RESEND_API_KEY"   -H "User-Agent: my-app/1.0"   -H "Content-Type: application/json"   -H "Idempotency-Key: password-reset-001"   -d @assets/send-email.json
```

### Node.js SDK single send

```ts
import { Resend } from "resend";

const resend = new Resend(process.env.RESEND_API_KEY);

await resend.emails.send({
  from: "Acme <onboarding@example.com>",
  to: "user@example.net",
  subject: "Welcome to Acme",
  html: "<p>Hi Ada, welcome aboard.</p>",
});
```

### Batch send via bundled helper

```bash
python3 scripts/resend_api.py request POST /emails/batch   --json-file assets/send-batch.json   --idempotency-key shipping-batch-001
```

## Common send-debug checklist

If a send is failing:

1. confirm the sender domain is verified
2. confirm the request includes `User-Agent`
3. confirm batch is not being used for attachments or scheduling
4. confirm template sends are using a published template
5. confirm idempotency keys are not being reused with different payloads
6. inspect `422` details for address, access, or attachment problems

## Useful assets

- `assets/send-email.json`
- `assets/send-email-template.json`
- `assets/send-batch.json`
- `assets/create-broadcast.json`
