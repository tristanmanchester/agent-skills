# Core reference

## Transport basics

- Base URL: `https://api.resend.com`
- Authentication: `Authorization: Bearer $RESEND_API_KEY`
- Raw HTTP integrations should send a `User-Agent` header.
- Use JSON request bodies unless the endpoint explicitly returns or expects binary content.

## Preferred execution surfaces

Choose the simplest surface that matches the task:

1. **Official SDK already in project** — extend that codebase in-place.
2. **One-off example or debugging** — use REST or cURL.
3. **Agent environment with Resend MCP** — acceptable for live operations, but still follow the
   request-shape and safety rules in this skill.
4. **Offline discovery or careful live calls** — use `scripts/resend_api.py`.

## Rate limiting

Resend documents a default per-team limit of **2 requests per second**. For loops, migrations, or
bulk operations, build in pacing or backoff instead of firing unbounded parallel requests.

## Cursor pagination

List endpoints use cursor pagination:

- `limit`: 1 to 100, default 20
- `after`: fetch the page after a given object ID
- `before`: fetch the page before a given object ID
- never send `after` and `before` together

Typical list responses look like:

```json
{
  "object": "list",
  "has_more": true,
  "data": [{ "id": "..." }]
}
```

If you are paginating forward, use the last object's `id` as the next `after` cursor.

## Stable endpoint groups

Use `assets/endpoint-catalog.json` or `python3 scripts/resend_api.py catalog` for the full list.
The stable OpenAPI snapshot covers:

- Emails
- Receiving Emails
- Domains
- API Keys
- Templates
- Contacts
- Segments
- Topics
- Contact Properties
- Broadcasts
- Webhooks
- Audiences (deprecated)

## Safety rules for mutations

- For `POST /emails` and `POST /emails/batch`, set an `Idempotency-Key` before retrying.
- Do not blindly retry `POST`, `PATCH`, or `DELETE` unless the operation is demonstrably idempotent
  or guarded with an idempotency key.
- Prefer `--dry-run` or schema inspection before destructive changes.

## Error triage cheat sheet

Start here before blaming the entire integration.

### 400

- `invalid_idempotency_key` — malformed or oversized idempotency key

### 401

- `missing_api_key` — forgot the bearer token
- `restricted_api_key` — using a sending-only key for a broader operation

### 403

- `invalid_api_key` — wrong or expired key
- missing or blocked `User-Agent` on raw HTTP
- unverified sender domain or test-mode restriction

### 404

- wrong resource ID
- wrong path or wrong environment assumptions

### 409

- `invalid_idempotent_request` — same idempotency key reused with a different payload
- `concurrent_idempotent_requests` — same key still in-flight

### 422

- invalid attachment payload
- invalid from-address format
- invalid access pattern or incompatible body fields

## Live-call checklist

Before making a real call, confirm all of the following:

- `RESEND_API_KEY` is loaded from the environment
- the sender domain is verified if the endpoint involves sending
- the request includes `Authorization` and `User-Agent`
- the path and method match the intended endpoint
- the body obeys endpoint-specific restrictions
- the follow-up verification step is known in advance

## Useful assets

- `assets/endpoint-catalog.json` — compact endpoint and schema index
- `assets/resend-openapi.yaml` — raw stable OpenAPI snapshot
- `assets/send-email.json` — simple transactional send payload
- `assets/create-domain.json` — verified-domain creation payload
