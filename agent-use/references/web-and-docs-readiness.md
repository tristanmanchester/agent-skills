# Web and docs readiness

Use this when auditing or designing a website, documentation site, support portal, marketing site with product actions, or public developer docs for agent use.

## Documentation websites

Agent-useful docs are discoverable, compact, canonical, and linkable.

Signals to look for:

- `/llms.txt` with concise links to the most important docs.
- `/llms-full.txt` only if useful and not too large.
- Markdown page variants or content negotiation with `Accept: text/markdown`.
- `robots.txt`, sitemap, canonical URLs, and redirects for deprecated docs.
- Stable anchors, headings, examples, outputs, limits, errors, auth scopes.
- Clear separation between tutorials, how-to guides, references, and explanations.

Common fixes:

- Create `llms.txt` with a top-level summary and curated links.
- Add a “For agents and automation” page that links specs, examples, schemas, and policies.
- Add markdown fallbacks for docs pages.
- Split giant pages into smaller pages with stable anchors.
- Redirect stale docs and mark archived content clearly.
- Add examples that include command/API output and error handling.

## Discovery endpoints

Publish only what is real and maintained.

| Surface | Recommended signal |
| --- | --- |
| Canonical docs index | `/llms.txt` |
| Larger docs dump | `/llms-full.txt` when bounded and current |
| Crawl policy | `/robots.txt`, `/sitemap.xml` |
| API discovery | `/.well-known/api-catalog` as `application/linkset+json` |
| API contract | OpenAPI/GraphQL/JSON Schema links from docs and Link headers |
| OAuth protected API | `/.well-known/oauth-protected-resource` and authorization-server/OpenID metadata |
| MCP server | `/.well-known/mcp.json`; keep legacy alternates redirected or linked |
| A2A/delegated agent | `/.well-known/agent-card.json` or equivalent card |
| Agent Skills | `/.well-known/agent-skills/index.json` |

Example headers are in `assets/templates/WEB_DISCOVERY_HEADERS.txt`.

## Auth and onboarding

Agents often fail before using the product because auth is unclear. Good docs include token creation, least-privilege scopes, service accounts or bot users, OAuth/OIDC metadata where applicable, expiration/rotation policy, sandbox credentials, permission error examples, and a way to identify read-only credentials.

## Content quality

Agents overfit stale snippets quickly. Every task page should include prerequisites, the current version, a minimal safe path, example input, example output, common errors, permission requirements, side effects, and verification steps.

## Observability

Track invalid tool/API/CLI calls, repeated docs retrieval before failure, docs search misses, error codes encountered by agents, retry and recovery success, approval requests/denials, latency, token use, and human corrections after agent actions.
