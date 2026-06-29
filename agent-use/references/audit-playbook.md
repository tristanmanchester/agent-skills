# Agent-use audit playbook

Use this playbook to audit existing work. The goal is not to prove that a system is “bad for agents.” The goal is to find the smallest concrete changes that make agents more successful while preserving safety and maintainability.

## 1. Scope the audit

Write down:

- Target name and version/date.
- Surfaces in scope: repo, docs website, app UI, CLI/TUI, API, SDK, MCP/tool server, agent skill, files, auth, observability.
- Intended agent tasks: what should an agent be able to do?
- Constraints: private repo, no network, no credentials, read-only review, safety limits.
- Non-goals: surfaces that intentionally do not apply.

Assume partial evidence. Be explicit about what was not inspectable.

## 2. Fast triage

Look for these high-signal files and endpoints.

Repository:

- `README.md`, `AGENTS.md`, `CONTRIBUTING.md`, `docs/`, `examples/`, `scripts/`, `bin/`, `cli/`, `.github/`, `openapi.*`, `schema.*`, `mcp.*`, `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`.
- Tests and evals: `tests/`, `e2e/`, `evals/`, `fixtures/`, `goldens/`.
- Safety and permissions: auth middleware, policy docs, RBAC, audit logs, destructive operations.

Website/docs:

- `/llms.txt`, `/llms-full.txt`, `/robots.txt`, `/sitemap.xml`.
- Markdown alternatives such as `/docs/index.md` or content negotiation with `Accept: text/markdown`.
- `/.well-known/api-catalog`, `/.well-known/mcp.json`, `/.well-known/agent-skills/index.json`, OAuth protected-resource metadata, and authorization-server metadata.
- API references, SDK references, CLI references, changelog, examples, limits, errors, auth scopes.

CLI/TUI:

- `--help`, `--version`, `--output json`, `--format json`, `--json`.
- Non-interactive equivalents for prompts.
- Exit codes, stderr/stdout separation, config/env docs, dry-run/yes flags, idempotency.

API/SDK:

- OpenAPI/GraphQL/protobuf/JSON Schema.
- Auth scopes, pagination, errors, idempotency, rate limits, sandbox.
- SDK method naming, typed parameters, examples, generated docs.

MCP/tools:

- Tool names/descriptions/input schemas/examples.
- Resource listings and prompt templates where useful.
- Consent, side-effect descriptions, safe defaults, output shapes.

## 3. Run automated checks

Use bundled scripts where applicable:

```bash
python scripts/audit_agent_use.py --root /path/to/repo --markdown --output agent-use-report.md --json-output agent-use-report.json
python scripts/web_agent_readiness.py https://example.com/docs --markdown --profile auto --output web-agent-readiness.md
python scripts/validate_agent_assets.py --skill-dir /path/to/skill --run-help --py-compile --markdown
```

Treat script output as a triage aid, not as final truth. The best audits combine automated signals with manual inspection of the actual user/agent journey.

## 4. Build the action/context parity map

For each important workflow, fill this table:

| Human workflow | Human context | Agent-readable context | Agent action path | Recovery path | Gap |
| --- | --- | --- | --- | --- | --- |
| Example: create project | Form fields, org, plan, permission, validation errors | `GET /orgs/{id}`, schema, limits, scopes | `POST /projects` or `tool:project.create` | idempotency key, delete/rollback | Missing schema for limits |

Good audits are won or lost here. If a UI has ten important buttons and only two are exposed through an API/CLI/tool, that is an action-parity gap. If the API exists but agents cannot know which ID, limit, plan, or permission applies, that is a context-parity gap.

## 5. Inspect common failure modes

### Discovery failure

The agent cannot find the right entry point, current docs, or canonical schema.

Evidence examples:

- No `README`, `AGENTS.md`, `llms.txt`, sitemap, OpenAPI link, or CLI reference.
- Docs search requires JavaScript and has no stable result URLs.
- Multiple conflicting docs versions with no redirects.

Fix examples:

- Add `AGENTS.md` and link all machine surfaces.
- Add `llms.txt` with concise links to docs, API, SDK, CLI, examples, changelog, auth, limits, and support.
- Add `/.well-known/api-catalog` or prominent API spec links.

### Context failure

The agent can find actions but cannot determine the right parameters.

Evidence examples:

- UI shows selected workspace but API docs do not explain workspace IDs.
- CLI can deploy but cannot list valid environments in JSON.
- Tool returns a success string but no created object ID.

Fix examples:

- Add list/get endpoints, resource schemas, and examples.
- Include identifiers and links in every mutation response.
- Expose active workspace/state through API/tool/context payload.

### Action failure

The agent knows what to do but cannot do it through a stable non-UI interface.

Evidence examples:

- Only browser UI can approve, export, configure, or delete.
- CLI prompts for required values but no flags exist.
- SDK covers reads but not writes.

Fix examples:

- Add typed primitive operations.
- Add non-interactive flags and JSON output.
- Ensure SDK/API/CLI parity for high-value workflows.

### Parse failure

The agent executes the action but cannot reliably parse the result.

Evidence examples:

- CLI prints colorful tables and progress bars mixed with output.
- Errors are natural language only.
- API returns different shapes for the same error class.

Fix examples:

- Add `--output json` and schema docs.
- Separate stdout data from stderr diagnostics.
- Standardize error envelope with `code`, `message`, `retryable`, `details`, `remediation`, `correlation_id`.

### Safety failure

The easiest agent path is too powerful or irreversible.

Evidence examples:

- Token grants all scopes.
- Destructive command has no dry-run or soft delete.
- No audit log or actor attribution.

Fix examples:

- Add scoped credentials, read-only mode, preview/dry-run, idempotency keys, human approval gates, rollback/undo, and audit logs.

### Recovery failure

Normal interruptions cause duplicate, stuck, or unverifiable work.

Evidence examples:

- Create operations are not idempotent.
- Long-running job has no status endpoint.
- Pagination is absent from list operations.

Fix examples:

- Add idempotency keys, job status endpoints, resume tokens, checkpoints, and retryable error classification.

### Eval failure

No one knows whether changes help agents.

Evidence examples:

- No task-level examples.
- No with/without-surface benchmark.
- Docs examples are never executed.

Fix examples:

- Add eval tasks from real support tickets or user workflows.
- Add assertions over final state.
- Track invalid tool calls, repeated docs searches, error recovery, token use, latency, and human approval rate.

## 6. Scoring process

Use `references/scoring-rubric.md`.

For each applicable dimension:

1. Give a 0-10 score.
2. Cite evidence.
3. Name the main gap.
4. Propose one or more fixes.
5. Mark severity:
   - Critical: blocks most agent use or creates serious safety risk.
   - High: blocks important workflows or causes frequent wrong actions.
   - Medium: causes avoidable friction or repeated failures.
   - Low: polish, consistency, or documentation improvement.

Overall score is the average of applicable dimensions multiplied by 10. Do not include non-applicable dimensions in the denominator.

## 7. Remediation planning

Group recommendations by implementation time and dependency.

### 0-2 days

Fast, high-leverage changes:

- Add `AGENTS.md`.
- Add `llms.txt`.
- Link existing API/SDK/CLI/MCP docs from README and docs homepage.
- Add `--output json` to one or two high-value CLI commands.
- Add missing examples for top workflows.
- Add a machine-readable error schema to docs.
- Add eval prompts and expected outputs.

### 2-7 days

Targeted engineering changes:

- Add OpenAPI or update stale schema.
- Add non-interactive CLI flags.
- Add dry-run/preview to destructive commands.
- Add idempotency keys to critical mutations.
- Add list/get endpoints needed for context parity.
- Add structured tool responses and response schemas.
- Add docs redirects and canonical URLs.

### 7-30 days

Architectural work:

- Create full action/context parity across UI, CLI, API, SDK, and tools.
- Build shared workspace/event model for human-agent collaboration.
- Add scoped auth and audit logs.
- Add sandbox mode.
- Add automated eval suite and telemetry dashboard.
- Refactor opaque workflows into composable primitives.

## 8. Audit output checklist

A complete audit includes:

- Target and date.
- Surfaces reviewed and not reviewed.
- Overall score and grade.
- Dimension scores with evidence.
- Action/context parity map.
- Top 5-10 remediation items.
- Safety and recovery findings.
- Eval plan.
- Any assumptions, limits, or uncertainty.

## 9. Red flags that deserve explicit callout

- Agents must use browser automation for core product actions.
- CLI prompts are required and cannot be bypassed.
- No machine-readable outputs for automation surfaces.
- Write operations are non-idempotent and irreversible.
- Tool descriptions hide side effects.
- Docs examples are stale or impossible to run.
- Auth scopes are undocumented or all-powerful.
- Agents can act but cannot inspect current state.
- Large docs pages lack anchors or markdown equivalents.
- Error messages lack stable codes and remediation.
