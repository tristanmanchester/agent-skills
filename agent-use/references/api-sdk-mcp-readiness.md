# API, SDK, MCP, and A2A contracts

## APIs and SDKs

Specify operation inputs, stable IDs, pagination boundaries, scopes, errors,
side effects, concurrency preconditions, and result states. Choose only applicable
features: a synchronous read does not need a background task model. Document the
actual retention/scope of write deduplication and distinguish partial/unknown
outcomes. SDK retries must not silently repeat ambiguous mutations. Preserve API
error details and versions; verify code against installed types.

## MCP

Use the chosen protocol version and transport, actual tool/resource discovery,
typed input/output, bounded results, and explicit errors. Resources and tool
annotations describe behaviour; they do not prove a read is harmless or grant
permission. Require server-side authorization and verify real effects. Do not
promote this package's local server-card example into an MCP standard. Use the
current official schema/SDK for wire-format conformance.

## A2A 1.0 baseline

The bundled `assets/templates/a2a-agent-card.json` follows the reviewed 1.0 field
shape: required name/description/version, ordered `supportedInterfaces`, a
`capabilities` object, default input/output media types, and described `skills`.
Each interface declares its service URL, `protocolBinding`, and `protocolVersion`
(`1.0`, not the agent's release version). The card URL and service URL differ.

Security declarations use `securitySchemes` with the selected union member and
`securityRequirements`; the example uses `httpAuthSecurityScheme` with Bearer and
an empty scope list. This does not implement authentication. Replace the example
with the actual enforced policy; no credentials belong in the card. Optional
streaming/push/extended-card capabilities default false until implemented and tested.

A2A 1.0 also changes message/event encodings from older kind-discriminator forms.
Use the versioned SDK/protocol schema rather than reusing old JSON samples. Send
`A2A-Version: 1.0` for the chosen interface and preserve any declared tenant routing.
No silent version downgrade is needed for new designs in this skill.

Validate generated cards with the actual current SDK/schema before publication,
then test discovery, authentication, messages/tasks, denied operations, declared
optional capabilities, progress, and cancellation. Cancellation is an operation
whose outcome must be observed, not guaranteed remote termination. Retain task
and context identities when resuming. The local regression tests check selected
scaffold fields only, not complete protocol conformance.

## Events and webhooks

Verify authentication/signatures before trusting state changes, durably deduplicate
receipts, acknowledge durable acceptance, and test concurrent replay/out-of-order
updates. Bound payloads and validate callback destinations to avoid forwarding
credentials or making unintended internal requests. Distinguish delivered events,
accepted jobs, completed tasks, and verified external effects.

Source reviewed 2026-09-13: [A2A 1.0 specification](https://a2a-protocol.org/latest/specification/),
particularly sections 3.6 and 4.4–4.5. Check the exact current MCP/API contract for
the selected implementation; these design checks are not substitute schemas.
