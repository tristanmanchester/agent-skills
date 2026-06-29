# Comparison with the original compound agent-native skills

## What the original skills did well

The deprecated Compound package was opinionated in a good way. It made a strong claim that agent support is not a bolt-on chatbot: the user and the agent should share action paths, context, and workspace state.

The most valuable original ideas preserved in v2 are:

- **Action parity:** meaningful user actions need agent paths unless intentionally human-only.
- **Context parity:** agents need the same domain objects, state, recent activity, and constraints a human operator sees.
- **Shared workspace:** agent work should land in durable, inspectable records/files/branches/drafts rather than hidden sandboxes.
- **Primitives over workflows:** expose composable capabilities; use workflow tools only for justified atomicity, safety, or external orchestration.
- **Dynamic context injection:** static prompts are not enough; runtime state and capabilities should be injected.
- **Noun test:** for every domain object, verify the agent can understand, discover, inspect, act where appropriate, and verify.
- **Human-only exceptions:** CAPTCHA, MFA, OAuth consent, legal acceptance, biometric prompts, and platform trust gates are not parity failures.
- **Mobile/offline and self-modification guardrails:** checkpoints, local files, review, rollback, and safe evolution matter.

## What was narrow or brittle in the original package

The original package focused mainly on app architecture and code review patterns. It was excellent for reviewing UI/tool parity inside a product, but weaker for:

- Public web/docs agent readiness.
- `llms.txt`, markdown negotiation, robots/sitemap/content policy, API catalog, and OAuth metadata.
- CLIs/TUIs as first-class agent surfaces.
- HTTP APIs, SDKs, schemas, error envelopes, pagination, idempotency, and versioning as agent contracts.
- Agent Skill packaging quality, trigger evals, scripts, templates, and progressive disclosure.
- File/workspace, mobile/offline, and long-running job patterns as reusable audit surfaces.
- Runnable local scanners, validators, scaffolding scripts, schemas, and example outputs.
- Separating “documentation says this exists” from “implementation evidence shows this exists.”

## How v2 improves it

Version 2 turns the original principles into a cross-surface audit/design skill. It keeps action/context parity as the central architecture principle, then adds surface-specific contracts for websites and docs, CLIs and TUIs, APIs and SDKs, MCP/A2A/tools, Agent Skills and repository instructions, app UIs and shared workspaces, files, mobile/offline, long-running jobs, checkpoints, and self-modification.

It also adds operational artifacts the original lacked:

- A local scanner with implementation-vs-doc evidence separation and generated-report exclusions.
- A web readiness checker for common agent discovery/capability endpoints, including `llms.txt`, API catalog Linkset, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A cards, and agent skill indexes.
- An `llms.txt` generator.
- An action-parity inventory script that turns UI/action/tool evidence into a candidate capability map.
- An agent-asset scaffolder.
- A skill/asset validator.
- JSON schemas and templates.
- Trigger and output-quality eval seeds.
- Example validation and self-audit outputs.

The result is not just “review a product for agent-native architecture”; it is “audit or design any useful agent-facing surface and give engineers patchable fixes.”

## What did not change

The skill still treats generic advice as low quality. Findings should be evidence-backed and implementable. Human approval is allowed and often required. Safety protocols are part of parity, not obstacles to it.

## v2 correctness fixes over v1 of this package

The v2 pass fixed concrete packaging and tooling defects: stale command references, validation path handling for `.` skill directories, missing output-directory creation, recursive self-audit evidence from generated reports, hidden `.well-known` discovery being skipped, ad-hoc API catalog JSON, missing `/.well-known/mcp.json`, and one-size-fits-all web scoring that penalized content-only sites for not publishing API/app endpoints.
