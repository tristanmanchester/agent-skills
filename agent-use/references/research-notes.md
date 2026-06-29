# Research notes and synthesis

Accessed 2026-06-29. This file summarizes the sources used to build the skill and how they inform the recommendations. It is a synthesis, not a copy of the source material.

## Bundled deprecated resources supplied by the user

Source: `compound-agent-native-old-skills-2026-06-29.zip`.

Important ideas carried forward:

- **Action parity**: every important user-facing action should have an agent-usable equivalent.
- **Context parity**: agents need the same decision-relevant state that human users see.
- **Shared workspace**: humans and agents should collaborate on the same durable objects rather than chat-only artifacts.
- **Primitive tools over opaque workflows**: expose composable actions and put recipes in prompts/docs/skills.
- **Dynamic context injection**: app-embedded agents should receive current object IDs, selection, permissions, and state.
- **Files as a universal interface**: durable, inspectable, transformable files are one of the most broadly useful agent surfaces.
- **Eval-driven iteration**: agent-native surfaces should be tested with realistic task workflows.

This new skill generalizes those ideas across web/docs, CLIs, TUIs, APIs, SDKs, MCP/tool servers, repos, skills, files, safety, and observability.

## Agent Skills documentation

Sources:

- `https://agentskills.io/specification`
- `https://agentskills.io/skill-creation/best-practices`
- `https://agentskills.io/skill-creation/optimizing-descriptions`
- `https://agentskills.io/skill-creation/evaluating-skills`
- `https://agentskills.io/skill-creation/using-scripts`

Synthesis:

- A skill package should be compact at the top level and use progressive disclosure: `SKILL.md` for routing/default workflow, references for long guidance, scripts for deterministic work, assets for templates/schemas.
- Skill descriptions are trigger contracts. They should describe intent and use contexts in the user’s likely wording.
- Scripts should be non-interactive, inspectable, safe by default, and helpful to agents through `--help`, clear errors, structured output, and deterministic behavior.
- Skill quality should be evaluated with trigger/non-trigger queries and output-quality tests, ideally compared with a baseline.

How this skill applies it:

- `SKILL.md` stays as a concise router.
- Detailed methods live in `references/`.
- Deterministic audits/validators/generators live in `scripts/`.
- Templates/schemas/eval seeds live in `assets/` and `evals/`.

## Cloudflare Agent Readiness and web discoverability

Source:

- `https://blog.cloudflare.com/agent-readiness/`

Synthesis:

- Web agent readiness includes discoverability, content quality, bot access controls, and machine-readable capability surfaces.
- Useful web endpoints include `llms.txt`, markdown docs, sitemaps, robots policies, API catalogs, MCP server cards such as `/.well-known/mcp.json`, agent skill indexes, and OAuth metadata.
- Markdown alternatives and curated resource indexes reduce agent search and token overhead.
- Stale docs and poor redirects create expensive “grep loops” for agents.

How this skill applies it:

- The web/docs guide checks for `llms.txt`, markdown variants, stable URLs, well-known capability endpoints, robots/sitemap, and stale docs handling.
- `scripts/web_agent_readiness.py` probes common endpoints and reports a pragmatic readiness score.
- `scripts/generate_llms_txt.py` drafts a simple `llms.txt` from docs trees.

## llms.txt proposal

Source:

- `https://llmstxt.org/`

Synthesis:

- `llms.txt` is a concise Markdown index for LLMs at inference time.
- The format centers on a required H1, a short summary, curated sections, and links with descriptions.
- It is complementary to sitemaps; sitemaps enumerate pages, while `llms.txt` curates the context and docs an agent should use.

How this skill applies it:

- Templates include `LLMS_TXT.template`.
- The web readiness script validates high-level shape and size.
- The build playbook recommends using it as a curated map to canonical docs, specs, examples, limits, errors, and changelog.

## Agent-friendly documentation specs

Sources:

- `https://agent-friendly-docs.firecrawl.dev/specification`
- `https://agent-friendly-docs.firecrawl.dev/`

Synthesis:

- Agent-friendly docs emphasize content discoverability, markdown availability, page-size limits, structure, URL stability, observability, and auth documentation.
- Practical checks include keeping `llms.txt` concise, serving markdown, keeping pages manageable, and monitoring resources.

How this skill applies it:

- Documentation scoring covers discoverability, content readability, page size, examples, stable URLs, and auth/access guidance.
- Eval guidance includes docs discovery tasks and stale-doc avoidance tasks.

## MCP and tool design

Sources:

- `https://modelcontextprotocol.io/specification/`
- `https://www.anthropic.com/engineering/writing-tools-for-agents`
- `https://docs.anthropic.com/en/docs/agents-and-tools/tool-use/overview`
- `https://www.anthropic.com/engineering/building-effective-agents`
- `https://cdn.openai.com/business-guides-and-resources/a-practical-guide-to-building-agents.pdf`

Synthesis:

- Tool definitions are contracts between deterministic systems and probabilistic agents.
- Good tools have clear names, descriptions, typed inputs, examples, high-signal outputs, and explicit side effects.
- Resources expose context, tools execute actions, and prompts encode repeatable workflows.
- Agents need interfaces designed as carefully as human-computer interfaces: clear affordances, constraints, examples, and edge-case behavior.
- Tooling should be evaluated with realistic tasks, not only unit tests.

How this skill applies it:

- The MCP/tool guide emphasizes namespacing, schemas, examples, safe defaults, context resources, bounded responses, and error envelopes.
- Evaluation guidance includes tool-selection, parameter-validation, and recovery evals.

## CLI/TUI guidance

Sources:

- `https://cli-spec.org/`
- `https://blog.arcjet.com/agent-friendly-clis/`
- `https://www.speakeasy.com/blog/cli-for-agents`

Synthesis:

- CLIs are API contracts for agents as much as for humans.
- Agent-friendly CLIs provide structured output, schema/help introspection, stdout/stderr separation, non-interactive execution, idempotent operations, and bounded output.
- Required prompts, spinners, colors, tables-only output, and ambiguous errors break automation.
- TUIs can remain human-first if every critical TUI action has equivalent CLI/API/tool paths.

How this skill applies it:

- CLI/TUI guidance requires `--help`, `--output json`, non-interactive flags, dry-run, documented exit codes, bounded output, and parseable errors.
- The audit script searches repositories for common CLI and TUI markers and output/safety signals.

## API, auth, and capability discovery standards

Sources:

- `https://spec.openapis.org/oas/latest.html`
- `https://www.rfc-editor.org/rfc/rfc9727.html`
- `https://www.rfc-editor.org/rfc/rfc9728.html`
- `https://json-schema.org/`

Synthesis:

- Machine-readable API descriptions let humans and computers understand service capabilities without reading source code.
- API catalogs provide a standardized `.well-known` location for API discovery.
- OAuth protected-resource metadata provides a standardized way for clients to discover authorization servers and supported scopes.
- JSON Schema and related schemas help make inputs/outputs/errors inspectable and testable.

How this skill applies it:

- API guidance recommends OpenAPI/GraphQL/JSON Schema or equivalent, well-known discovery, scoped auth docs, consistent errors, and contract tests.
- Templates include API agent contract, API catalog, and error-envelope schema.

## Final synthesis

An “agent-use” surface succeeds when it reduces ambiguity. The recurring pattern across all sources is the same:

1. Help the agent discover the right surface.
2. Give it compact, current context.
3. Expose typed primitive actions.
4. Make outputs parseable and bounded.
5. Make side effects safe, permissioned, recoverable, and auditable.
6. Test the real tasks agents are expected to perform.

The skill’s rubric and scripts are intentionally surface-agnostic so they can be used for codebases, websites, CLIs, SDKs, MCP servers, app UIs, and future interfaces.

## v2 update notes

Version 2 adds profile-aware web scoring, RFC-style API catalog Linkset templates, `/.well-known/mcp.json` discovery, hidden `.well-known` repo scanning, generated-report exclusions, action-parity inventory tooling, asset scaffolding, and deeper references for the original Compound material.
