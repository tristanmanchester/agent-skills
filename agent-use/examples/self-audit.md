# Agent-use audit: `/Users/tristan/Projects/skills/agent-use`

Overall: **91/100** (A)
Confidence: **medium**
Files scanned: 60

## Scores

| Dimension | Applicable | Score | Main gaps |
| --- | --- | ---: | --- |
| Discoverability | True | 9.4 | — |
| Content readability | True | 10.0 | — |
| Capability contracts | True | 8.1 | — |
| Action parity | False | — | — |
| Context parity | False | — | — |
| Composability and primitive quality | False | — | — |
| Parseable, bounded outputs | False | — | — |
| Safety, permissions, and governance | False | — | — |
| Recovery and resilience | False | — | — |
| Evals and observability | True | 8.8 | — |

## Top recommendations

1. **low / Discoverability**: llms.txt exists but no local web discovery files were found; add .well-known, robots, or sitemap when this package is published as web docs.

## Evidence by dimension

### Discoverability
Evidence:
- `README.md` (docs; file matches README*)
- `AGENTS.md` (contract; file matches AGENTS.md)
- `CHANGELOG.md` (docs; file matches *.md)
- `README.md` (docs; file matches *.md)
- `SKILL.md` (docs; file matches *.md)
- `AGENTS.md` (contract; file matches *.md)
- `references/audit-playbook.md` (docs; file matches *.md)
- `references/review-recipes.md` (docs; file matches *.md)

### Content readability
Evidence:
- `README.md` (docs; file matches README*)
- `CHANGELOG.md` (docs; file matches *.md)
- `README.md` (docs; file matches *.md)
- `SKILL.md` (docs; file matches *.md)
- `AGENTS.md` (contract; file matches *.md)
- `references/audit-playbook.md` (docs; file matches *.md)
- `references/review-recipes.md` (docs; file matches *.md)
- `references/web-and-docs-readiness.md` (docs; file matches *.md)

### Capability contracts
Evidence:
- `assets/schemas/tool-definition.schema.json` (contract; file matches **/*schema*.json)
- `assets/schemas/cli-error-envelope.schema.json` (contract; file matches **/*schema*.json)
- `assets/templates/task-lifecycle.schema.json` (template; file matches **/*schema*.json)
- `assets/templates/tool-result.schema.json` (template; file matches **/*schema*.json)
- `SKILL.md:58` (docs; JSON Schema) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de
- `references/audit-playbook.md:42` (docs; JSON Schema) — - OpenAPI/GraphQL/protobuf/JSON Schema.
- `references/web-and-docs-readiness.md:37` (docs; JSON Schema) — | API contract | OpenAPI/GraphQL/JSON Schema links from docs and Link headers |
- `references/build-playbook.md:31` (docs; JSON Schema) — | Reference contract | OpenAPI, GraphQL schema, JSON Schema, CLI help, MCP server card |

### Action parity
No obvious user action or automation surface detected.

### Context parity
No obvious workflow surface detected.

### Composability and primitive quality
No obvious API/CLI/SDK/tool primitives detected.

### Parseable, bounded outputs
No obvious machine execution surface detected.

### Safety, permissions, and governance
No obvious side-effecting surface detected.

### Recovery and resilience
No obvious execution surface detected.

### Evals and observability
Evidence:
- `evals/trigger_queries.json` (contract; file matches evals/**)
- `evals/evals.json` (contract; file matches evals/**)
- `llms.txt:23` (contract; eval) — - [Evaluation](references/evaluation.md): Task-level evals and regression checks.
- `llms.txt:32` (contract; eval) — - [Skill validator](scripts/validate_agent_assets.py): Validate Agent Skill structure, JSON, scripts, and evals.
- `CHANGELOG.md:14` (docs; eval) — - Added agent-asset scaffolding for AGENTS.md, llms.txt, web discovery headers, capability maps, API/CLI contracts, permission matrices, API catalog, MCP card, A2A card, skills index, and eval seeds.
- `CHANGELOG.md:16` (docs; eval) — - Expanded guidance across websites/docs, CLIs/TUIs, APIs, SDKs, MCP/A2A/tools, app UIs, files/workspaces, security, evals, and Agent Skill packaging.
- `README.md:9` (docs; eval) — Zip the `agent-use/` directory or install it wherever your Agent Skills runtime expects skills. The main entry point is `SKILL.md`. Detailed playbooks are in `references/`; reusable helpers are in `scripts/`; templates and schemas are in `a
- `README.md:27` (docs; eval) — A good audit includes an overall agent-use score, applicability notes, dimension-by-dimension evidence, an action/context parity map, safety and recovery findings, a concrete remediation plan, and evals/acceptance criteria.

## Surface signal counts

```json
{
  "agents": 1,
  "api_markers": 12,
  "api_specs": 4,
  "auth": 12,
  "bounded_output": 12,
  "capability_map": 10,
  "changelog": 1,
  "cli_markers": 12,
  "contributing": 0,
  "docs": 12,
  "errors": 12,
  "evals_tests": 14,
  "examples": 1,
  "json_output": 12,
  "json_schema": 8,
  "llms": 1,
  "observability": 12,
  "readme": 1,
  "recovery": 14,
  "safety": 14,
  "sdk_markers": 10,
  "skill_markers": 12,
  "stdout_stderr": 8,
  "tool_markers": 14,
  "tui_markers": 10,
  "ui_actions": 4,
  "web_discovery": 0
}
```

## Score basis

```json
{
  "contract": 45,
  "docs": 159,
  "generated": 0,
  "implementation": 1,
  "scanner": 13,
  "template": 5
}
```

Heuristic scan only. Confirm findings by walking through real agent tasks and the action/context parity map.
