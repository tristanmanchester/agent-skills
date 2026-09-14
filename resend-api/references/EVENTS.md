# Webhooks, receiving, and Automations

## Receive events safely

Use the official SDK verifier or Svix, not an improvised HMAC formula. Supply the
**unchanged raw request body** and `svix-id`, `svix-timestamp`, `svix-signature`
headers with the signing secret. Enforce verification and timestamp checks before
parsing trusted event fields or changing state; absent/invalid signatures fail
closed. Keep raw bytes available before framework JSON middleware consumes them.

Deduplicate verified event IDs durably. Acknowledge only after durable acceptance
and process work with replay-safe operation IDs. A failed queue/database write
must not produce a success ACK. Handle retries, manual replay, concurrent
duplicates, and out-of-order updates without duplicate replies or stale state
regression. Secret rotation needs a tested overlap/rollout plan per the current
provider contract, not disabled verification.

For `email.received`, use `GET /emails/receiving/{email_id}` and its attachments
endpoints to fetch full content; event metadata is not the complete message.
Treat HTML, filenames, links, and attachment bytes as untrusted. Bound downloads,
reject unsafe paths, and do not attach Resend credentials to another host. Preserve
message threading headers deliberately and prevent autoreply loops.

## Define an Automation

The current REST contract is `POST /automations`, with `steps` and `connections`.
For example, after creating/resolving the custom event and published template:

```json
{
  "name": "Test welcome",
  "status": "disabled",
  "steps": [
    {"key": "start", "type": "trigger", "config": {"event_name": "user.created"}},
    {"key": "welcome", "type": "send_email", "config": {"template": {"id": "PUBLISHED_TEMPLATE_ID"}}}
  ],
  "connections": [{"from": "start", "to": "welcome"}]
}
```

Replace placeholders with verified IDs. Validate graph references, unique keys,
trigger/schema, template variables, sender defaults, and contact/consent policy.
Read back the disabled result before enabling. Current Node SDK configuration
uses `eventName` rather than REST `event_name`; its event sender uses `contactId`
rather than REST `contact_id`. Use the SDK's types, not a mechanical JSON paste.

`POST /events` defines an event schema; **`POST /events/send` emits an event** and
can start matching Automations. Supply `event`, either the documented contact-ID
or email-address target, and `payload` matching the schema. Inspect possible
fan-out before using a real contact. Event acceptance is not run completion.

Enabled Automation graphs cannot simply be edited in place. Duplicate and edit
a replacement, plan the activation/switchover, and choose deliberately whether
to let in-flight runs finish or cancel them. Consult the current update/stop
contracts for exact fields; do not equate disabled/new-run stopping with
cancelling every existing run. Inspect run and step results after rollout.

## Tests to require in the target integration

Test invalid/missing signatures, changed raw bytes, expired timestamps, repeated
and concurrent event IDs, durable-queue failure, out-of-order delivery, send
retry with the same identity, wrong template variables, disabled flow behaviour,
and event fan-out. Use synthetic contacts with explicit test authorisation for
live checks. A mock response validates local logic, not Resend acceptance.

## Sources reviewed 2026-09-13

- [Verification](https://resend.com/docs/webhooks/verify-webhooks-requests)
- [Receiving](https://resend.com/docs/api-reference/emails/retrieve-received-email)
- [Automations overview](https://resend.com/docs/dashboard/automations/introduction)
- [Create Automation](https://resend.com/docs/api-reference/automations/create-automation)
- [Update Automation](https://resend.com/docs/api-reference/automations/update-automation)
- [Stop Automation](https://resend.com/docs/api-reference/automations/stop-automation)
- [Send Event](https://resend.com/docs/api-reference/events/send-event)
