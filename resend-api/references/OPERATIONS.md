# Sending and operational contracts

## Send, template, batch, schedule

For hosted templates, resolve an actual published ID/alias and validate variables
against its definitions. Use `template: { id, variables }`; do not mix template
with `html`, `text`, or `react`. Sender/subject/reply-to overrides take precedence;
provide required values when there is no template default. Typed SDK variables
may be strings or numbers; do not let a CLI string conversion silently change
semantics. Raw REST JSON cannot contain a React component.

Batch sends currently contain at most 100 messages and do not support attachments.
Check the live batch schema for any other needed fields rather than assuming all
single-send options work. Freeze ordering and the exact request, persist its
idempotency key before send, and map returned IDs to messages. Inspect error/per-item
results when the chosen mode exposes them. A later bounce is not permission to
resend an entire batch or bypass a suppression.

A single `to` array is one message, not independent private personalised sends.
Review recipient visibility. Resolve a schedule into an absolute timestamp with
timezone and check the current horizon. Sending, scheduling, changing, cancelling,
and later delivery race with different states; verify the resulting provider state.

Validate attachment size/type and encoding against the current endpoint; JSON
binary content is Base64, not a local filesystem path. A hosted attachment URL
must remain fetchable when the provider needs it. Never upload private files
merely because a template or untrusted message mentions their path. Rendered
HTML/text, links, unsubscribe mechanism, and visible sender all need review.

## Transport and recovery

Use least-privilege credentials and keep API keys out of client bundles, URLs,
logs, fixtures, and command history. Raw API requests must include `Authorization: Bearer …`, the appropriate content
type, and a descriptive `User-Agent` such as `my-app/1.0`. A missing User-Agent can
cause an edge-layer 403 / error 1010 before the request reaches Resend; SDKs include
it automatically. See [the header requirement](https://resend.com/docs/knowledge-base/403-error-1010).
Raw API requests target HTTPS api.resend.com;
do not forward its bearer token to redirects or attachment download hosts. Use
bounded timeouts and response limits. Inspect SDK `error` results as well as
thrown transport errors.

For reads, bounded retries can respect server rate-limit headers. For writes,
apply only the endpoint's documented idempotency guarantee. Email/batch keys
currently last 24 hours and support at most 256 characters. Persist the exact
payload/key before submission, and retry that identity rather than generating a
new key. Do not assume the same contract covers contacts, broadcasts, events,
Automation creation, or DNS changes. Keep an outcome ledger and reconcile unknowns.

Follow documented pagination cursors until the requested scope is complete, or
label the result partial. Missing access, throttling, and malformed responses are
not empty data. Avoid hardcoding one account's rate limit as universal.

## Domains, consent, and administration

Read current domain/DNS state before changing it. Use the exact returned record
names/values, verify sending/receiving capabilities independently, and avoid
breaking existing MX delivery; an inbound subdomain may be preferable. A verify
request starting does not mean the domain is verified.

Contacts, Segments, and Topics replace deprecated Audiences for new integration
work. Membership is not consent. Preserve topic/global opt-outs and suppressions.
Preview the exact campaign before authorised delivery and make the required
unsubscribe path functional. Do not infer successful unsubscribe handling from
an unsubscribe link merely appearing in HTML.

Use separate secret storage for API credentials and webhook signing secrets.
Rotation, deletion, profile/account changes, recipient imports, and contact
removal require deliberate scope and read-back verification.

## Sources reviewed 2026-09-13

- [Send](https://resend.com/docs/api-reference/emails/send-email)
- [Batch](https://resend.com/docs/api-reference/emails/send-batch-emails)
- [Idempotency](https://resend.com/docs/dashboard/emails/idempotency-keys)
- [Current endpoint index](https://resend.com/docs/llms.txt)
