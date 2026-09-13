# Web and discovery contracts

Publish only maintained surfaces a real consumer uses. Discovery conventions have
different status; do not count every absent filename as a defect.

| Surface | Status and appropriate use |
| --- | --- |
| `llms.txt`, bounded Markdown documentation | Optional documentation convention; neither permission to crawl nor a protocol requirement |
| robots/sitemap/canonical links | Crawl/discovery signals; not authentication or proof of content completeness |
| `/.well-known/api-catalog` | RFC 9727 API catalog using the specified Linkset representation; link to actual APIs |
| OAuth/OIDC metadata | Use the exact current discovery/authorization contract for the protected resource and issuer |
| A2A `/.well-known/agent-card.json` | A2A discovery card; its supported interface URL is the service, not the card itself |
| `/.well-known/mcp.json` | A local example in this package, not a universal MCP discovery requirement |
| `/.well-known/agent-skills/index.json` | A local index proposal, not required by the Agent Skills file format |

For MCP, verify the selected specification/client/transport's actual discovery,
initialisation, and authorization behaviour. Do not substitute a fabricated server
card for protocol negotiation. Auth metadata is not authorization to obtain or use
credentials. Validate issuer/resource relationships and redirect destinations
before sending tokens; do not trust arbitrary links inside discovery documents.

Useful documentation exposes stable object IDs, bounded examples, field semantics,
side effects, scopes, error/retry handling, dates/versioning, and result verification.
Provide compact task-focused pages and a canonical source instead of copying an
entire SDK catalogue into each skill. Keep dates and maintenance ownership visible.

Evaluate with real tasks: can the agent find the correct page, authenticate within
its existing permission, choose the right operation, and verify the outcome?
Measure failures, retries, corrections, and time/context cost. A heuristic discovery
score is a lead for inspection, not that evaluation's result.

Sources reviewed 2026-09-13:
[Agent Skills specification](https://agentskills.io/specification),
[A2A discovery](https://a2a-protocol.org/latest/specification/),
[RFC 9727](https://www.rfc-editor.org/rfc/rfc9727.html).
For MCP, read the applicable current official transport/authorization specification
at implementation time; no single static well-known filename is assumed here.
