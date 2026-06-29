# Agent-use audit: `/mnt/data/agent-use-v2/agent-use`

Overall: **90/100** (A)
Files scanned: 58

## Scores

| Dimension | Applicable | Score | Main gaps |
| --- | --- | ---: | --- |
| Discoverability | True | 8.4 | — |
| Content readability | True | 9.4 | No examples/samples directory found. |
| Capability contracts | True | 9.8 | — |
| Action parity | True | 9.8 | — |
| Context parity | True | 9.5 | — |
| Composability and primitive quality | True | 9.3 | No examples found to show how primitives compose into workflows. |
| Parseable, bounded outputs | True | 8.2 | — |
| Safety, permissions, and governance | True | 9.0 | — |
| Recovery and resilience | True | 9.0 | — |
| Evals and observability | True | 7.6 | — |

## Top recommendations

1. **low / Composability and primitive quality**: Add recipes that compose small API/CLI/tool primitives for common tasks.
2. **low / Content readability**: Add small runnable examples with realistic inputs and outputs.

## Evidence by dimension

### Discoverability
Evidence:
- `README.md` (file matches README*)
- `AGENTS.md` (file matches AGENTS.md)
- `SKILL.md` (file matches *.md)
- `README.md` (file matches *.md)
- `AGENTS.md` (file matches *.md)
- `CHANGELOG.md` (file matches *.md)
- `references/framework.md` (file matches *.md)
- `references/audit-playbook.md` (file matches *.md)

### Content readability
Evidence:
- `README.md` (file matches README*)
- `SKILL.md` (file matches *.md)
- `README.md` (file matches *.md)
- `AGENTS.md` (file matches *.md)
- `CHANGELOG.md` (file matches *.md)
- `references/framework.md` (file matches *.md)
- `references/audit-playbook.md` (file matches *.md)
- `references/build-playbook.md` (file matches *.md)
Recommendations:
- Add small runnable examples with realistic inputs and outputs.

### Capability contracts
Evidence:
- `assets/templates/tool-result.schema.json` (file matches **/*schema*.json)
- `assets/templates/task-lifecycle.schema.json` (file matches **/*schema*.json)
- `assets/schemas/cli-error-envelope.schema.json` (file matches **/*schema*.json)
- `assets/schemas/tool-definition.schema.json` (file matches **/*schema*.json)
- `SKILL.md:35` (JSON Schema) — 2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help
- `SKILL.md:52` (JSON Schema) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de
- `references/framework.md:18` (JSON Schema) — - Stable links to OpenAPI, GraphQL, JSON Schema, SDK docs, CLI docs, MCP server card, API catalog, changelog, examples, and support policy.
- `references/framework.md:52` (JSON Schema) — - OpenAPI, AsyncAPI, GraphQL schema, JSON Schema, protobuf, Smithy, TypeSpec, or typed SDK docs.

### Action parity
Evidence:
- `scripts/agent_use_audit.py:257` (<button\b) — r"onClick\s*=", r"onSubmit\s*=", r"addEventListener\(['\"]click", r"<button\b", r"<Button\b",
- `scripts/agent_use_audit.py:258` (onTapGesture) — r"onPressed\s*:", r"onTapGesture", r"TouchableOpacity", r"Pressable", r"button_to", r"form_with",
- `scripts/agent_use_audit.py:259` (submitButton) — r"submitButton", r"MenuItem", r"DropdownMenuItem",
- `scripts/action_parity_inventory.py:16` (<button\b) — "ui_action":[r"\bonClick\b",r"\bonSubmit\b",r"<button\b",r"Button\(",r"addEventListener\(['\"]click",r"onPressed\b",r"onTap\b"],
- `SKILL.md:35` (GraphQL) — 2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help
- `SKILL.md:52` (GraphQL) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de
- `LICENSE:7` (REST) — in the Software without restriction, including without limitation the rights
- `CHANGELOG.md:5` (REST) — - Fixed stale script references and restored working v2 command names plus v1 compatibility entry points.

### Context parity
Evidence:
- `SKILL.md:35` (GraphQL) — 2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help
- `SKILL.md:52` (GraphQL) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de
- `LICENSE:7` (REST) — in the Software without restriction, including without limitation the rights
- `CHANGELOG.md:5` (REST) — - Fixed stale script references and restored working v2 command names plus v1 compatibility entry points.
- `references/framework.md:18` (GraphQL) — - Stable links to OpenAPI, GraphQL, JSON Schema, SDK docs, CLI docs, MCP server card, API catalog, changelog, examples, and support policy.
- `references/framework.md:52` (GraphQL) — - OpenAPI, AsyncAPI, GraphQL schema, JSON Schema, protobuf, Smithy, TypeSpec, or typed SDK docs.
- `references/audit-playbook.md:42` (GraphQL) — - OpenAPI/GraphQL/protobuf/JSON Schema.
- `references/build-playbook.md:31` (GraphQL) — | Reference contract | OpenAPI, GraphQL schema, JSON Schema, CLI help, MCP server card |

### Composability and primitive quality
Evidence:
- `assets/templates/tool-result.schema.json` (file matches **/*schema*.json)
- `assets/templates/task-lifecycle.schema.json` (file matches **/*schema*.json)
- `assets/schemas/cli-error-envelope.schema.json` (file matches **/*schema*.json)
- `assets/schemas/tool-definition.schema.json` (file matches **/*schema*.json)
- `SKILL.md:3` (MCP) — description: Audit or design websites, docs, apps, CLIs/TUIs, APIs, SDKs, MCP/A2A agents, Agent Skills, and repos so AI agents can discover, understand, safely operate, verify, and recover from real tasks. Use for agent-readiness audits, ac
- `SKILL.md:22` (MCP) — 1. Classify the target: website/docs, app UI, repository, CLI/TUI, HTTP API, SDK, MCP server, A2A agent, Agent Skill, file/workspace system, mobile app, or mixed product.
- `SKILL.md:35` (MCP) — 2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help
- `SKILL.md:48` (MCP) — Web/docs: `llms.txt`, markdown availability, stable URLs, stale-doc avoidance, robots/sitemap, API catalog, OAuth/OIDC metadata, MCP/A2A discovery, examples, small pages, canonical docs, content access policy, and docs that fit context wind
Recommendations:
- Add recipes that compose small API/CLI/tool primitives for common tasks.

### Parseable, bounded outputs
Evidence:
- `SKILL.md:23` (--output) — 2. Gather evidence from applicable surfaces. For repositories, run `scripts/audit_agent_use.py --root <path> --markdown`. For UI/app repos, also run `scripts/action_parity_inventory.py <path> --output action-parity-inventory.md --csv-output
- `SKILL.md:50` (--output) — CLIs/TUIs: `--help`, `--version`, non-interactive mode, `--output json`, schema introspection, stdout/stderr separation, stable exit codes, explicit error envelopes, dry-run, idempotency, bounded output, no spinners in machine mode, no prom
- `SKILL.md:87` (--output) — - `scripts/action_parity_inventory.py <repo-or-dir> --output action-parity-inventory.md --csv-output capability-map.csv` inventories UI actions and candidate agent paths.
- `SKILL.md:89` (--output) — - `scripts/generate_llms_txt.py <docs-root> --site-url <url> --output llms.txt` drafts an `llms.txt`.
- `README.md:14` (--output) — python scripts/audit_agent_use.py --root /path/to/repo --markdown --output agent-use-report.md --json-output agent-use-report.json
- `README.md:15` (--output) — python scripts/action_parity_inventory.py /path/to/repo --output action-parity-inventory.md --csv-output capability-map.csv
- `README.md:16` (--output) — python scripts/web_agent_readiness.py https://example.com/docs --markdown --profile auto --output web-agent-readiness.md
- `README.md:17` (--output) — python scripts/generate_llms_txt.py ./docs --site-url https://example.com/docs --output llms.txt

### Safety, permissions, and governance
Evidence:
- `SKILL.md:34` (permission) — 1. Define 5-10 real agent tasks before choosing surfaces. Include read-only tasks, mutation tasks, recovery tasks, permission-sensitive tasks, and long-running tasks if relevant.
- `SKILL.md:35` (OAuth) — 2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help
- `SKILL.md:37` (permission) — 4. Design context parity. Inject current resources, capabilities, constraints, user-visible state, recent activity, domain vocabulary, permissions, and completion criteria into the agent path.
- `SKILL.md:40` (scope) — 7. Make mutations safe. Add dry-run/preview, idempotency keys, scoped permissions, audit logs, confirmation for high-impact actions, sandbox/test mode, and undo/rollback where practical.
- `SKILL.md:41` (token) — 8. Make work resumable. Long-running jobs need progress, checkpoints, partial results, completion signals, and retry/resume tokens.
- `SKILL.md:42` (permission) — 9. Ship evals. Compare baseline versus improved surfaces and cover discovery, happy paths, permissions, edge cases, recovery, and regression.
- `SKILL.md:48` (OAuth) — Web/docs: `llms.txt`, markdown availability, stable URLs, stale-doc avoidance, robots/sitemap, API catalog, OAuth/OIDC metadata, MCP/A2A discovery, examples, small pages, canonical docs, content access policy, and docs that fit context wind
- `SKILL.md:52` (scope) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de

### Recovery and resilience
Evidence:
- `SKILL.md:40` (idempotenc) — 7. Make mutations safe. Add dry-run/preview, idempotency keys, scoped permissions, audit logs, confirmation for high-impact actions, sandbox/test mode, and undo/rollback where practical.
- `SKILL.md:41` (retry) — 8. Make work resumable. Long-running jobs need progress, checkpoints, partial results, completion signals, and retry/resume tokens.
- `SKILL.md:50` (idempotenc) — CLIs/TUIs: `--help`, `--version`, non-interactive mode, `--output json`, schema introspection, stdout/stderr separation, stable exit codes, explicit error envelopes, dry-run, idempotency, bounded output, no spinners in machine mode, no prom
- `SKILL.md:52` (idempotenc) — APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, de
- `SKILL.md:58` (checkpoint) — Files/workspaces/mobile: files as a universal interface, explicit working directories, safe self-modification, checkpoints, offline/battery/network constraints, background execution policy, conflict resolution, and inspectable artifacts.
- `SKILL.md:76` (checkpoint) — - `references/files-mobile-and-long-running-work.md` — files, mobile/offline, checkpoints, background execution, self-modification.
- `SKILL.md:78` (rollback) — - `references/security-recovery.md` — permissions, approval, safety, rollback, privacy, abuse resistance.
- `llms.txt:21` (checkpoint) — - [Files/mobile/long-running work](references/files-mobile-and-long-running-work.md): Checkpoints, offline constraints, task status.

### Evals and observability
Evidence:
- `evals/evals.json` (file matches evals/**)
- `evals/trigger_queries.json` (file matches evals/**)
- `SKILL.md:3` (eval) — description: Audit or design websites, docs, apps, CLIs/TUIs, APIs, SDKs, MCP/A2A agents, Agent Skills, and repos so AI agents can discover, understand, safely operate, verify, and recover from real tasks. Use for agent-readiness audits, ac
- `SKILL.md:18` (eval) — The doctrine: **agents need action parity, context parity, safe primitives, structured outputs, durable state, explicit completion signals, and recovery paths.** Prose helps, but agent-useful systems also provide inspectable contracts, exam
- `SKILL.md:28` (eval) — 7. Prioritize fixes into quick wins, medium work, and structural work. Include evals that prove the improvements help agents complete tasks.
- `SKILL.md:42` (eval) — 9. Ship evals. Compare baseline versus improved surfaces and cover discovery, happy paths, permissions, edge cases, recovery, and regression.
- `SKILL.md:60` (eval) — Agent Skills: precise trigger description, compact `SKILL.md`, progressive disclosure through references/assets/scripts, runnable helpers, eval seeds, versioning, and backwards-compatible commands.
- `SKILL.md:79` (eval) — - `references/evaluation.md` — evals, observability, decay prevention, release checks.

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
  "examples": 0,
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

Heuristic scan only. Confirm findings by walking through real agent tasks and the action/context parity map.
