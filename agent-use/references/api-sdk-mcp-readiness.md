# API, SDK, MCP, A2A, and tool readiness

Use this when auditing or designing HTTP APIs, SDKs, tool servers, MCP servers, A2A agents, webhooks, and automation contracts.

## HTTP APIs

Agent-friendly APIs are predictable and richly documented.

Required patterns:

- OpenAPI or equivalent schema.
- Auth scope documentation.
- Consistent object IDs and resource URLs.
- Pagination on list endpoints.
- Filtering/sorting/field selection for large resources.
- Standard error envelope.
- Idempotency for mutations.
- Rate limits and retry headers.
- Long-running job model.
- Changelog/versioning/deprecation policy.
- Examples for common workflows.

Mutation responses should return created/updated object ID, status, links, warnings, partial-success information, request/correlation ID, and next action when asynchronous.

## SDKs

SDKs should not hide capability gaps. Methods should align with API operation names and docs. Types should be exported and documented. Errors should preserve API error codes and details. Examples should cover auth, common operations, pagination, retries, idempotency, and cleanup. Generated SDK docs should link back to the canonical API schema.

## MCP and other tool servers

MCP/tool servers are agent-facing APIs. Treat tool definitions as contracts.

Tool design checklist:

- Names are namespaced, concise, and intent-oriented.
- Descriptions state when to use the tool, what it does, side effects, and constraints.
- Input schemas are precise; required fields are clear; enums/bounds/examples are used where possible.
- Output shapes are stable and documented.
- Large outputs are summarized and paginated.
- Resources expose context that does not require side effects.
- Prompts encode repeatable workflows and best practices.
- Dangerous actions are gated or previewable.
- Tool errors include stable codes and remediation.

Avoid tool names like `run`, `execute`, `manage`, or `do_task` without a namespace; free-form JSON blobs where typed objects are possible; huge raw responses by default; tools that silently mutate state during reads; and tools that require invisible IDs without lookup tools.

## A2A/delegated task agents

For delegated tasks, expose task lifecycle, input/output artifacts, status, cancellation, approval needs, and resume semantics. The agent card should say what tasks are accepted, what modalities/artifacts are supported, how auth works, and how to poll or subscribe to progress.

## Notifications and webhooks

Agent-friendly event systems expose versioned event schemas, delivery signatures, retry semantics, event IDs and timestamps, replay/backfill, test events, and local development support.
