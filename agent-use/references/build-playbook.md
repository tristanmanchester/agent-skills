# Agent-use build playbook

Use this playbook when designing new work or refactoring an existing system so agents can use it well.

## 1. Start from agent jobs, not interfaces

Write 5-10 real jobs an agent should complete. Prefer outcome-oriented tasks:

- “Find the latest failed deployment, identify the likely cause, and draft a fix.”
- “Create a report from uploaded CSVs and save it as a PDF.”
- “Add a read-only API token for a teammate and document the scopes.”
- “Generate a migration plan from v1 API to v2 API.”
- “Run tests, fix formatting, and open a PR.”

For each job, record:

- Required context.
- Required actions.
- Safety or approval boundaries.
- Expected final state.
- Common edge cases.
- How success can be verified automatically.

## 2. Choose the right surfaces

Most systems need a portfolio, not one magic surface.

| Need | Good surface |
| --- | --- |
| Discovery and orientation | README, AGENTS.md, llms.txt, docs homepage |
| Reference contract | OpenAPI, GraphQL schema, JSON Schema, CLI help, MCP server card |
| Local automation | CLI, scripts, files, SDK |
| Remote automation | HTTP API, SDK, MCP/tools |
| Human-agent collaboration | Shared workspace, comments, approvals, audit log |
| Long-running work | Job API, status endpoint, logs, checkpoints |
| Repeated recipes | Skill, prompt template, examples, runbook |
| Safety | Auth scopes, dry-run, preview, approval, rollback |

Do not force all agent use through a chat interface. Chat is a coordination surface; durable objects, APIs, CLIs, and files are execution surfaces.

## 3. Create an agent contract

An agent contract is the compact promise your system makes to agents.

It should answer:

- What can the agent do?
- Where are the canonical docs and schemas?
- What identifiers and state models exist?
- Which actions are read-only, write, destructive, costly, or externally visible?
- How does auth work?
- What are the safe defaults?
- What outputs and errors are guaranteed?
- How can the agent verify, resume, retry, or undo?
- What should the agent never do?

Use `assets/templates/AGENTS.md.template`, `CLI_AGENT_CONTRACT.md.template`, `API_AGENT_CONTRACT.md.template`, and `MCP_TOOL_CARD.md.template`.

## 4. Design capability maps

Before building, create a capability map.

```csv
capability,human_ui_path,agent_context_path,agent_action_path,safety_level,recovery_path,status,owner
Create project,New project form,GET /orgs + project schema,POST /projects,write,DELETE /projects/{id} or rollback,planned,@team
List deployments,Deployments tab,GET /deployments,GET /deployments,read,pagination cursor,done,@team
Delete environment,Settings > Delete,GET /environments/{id},DELETE /environments/{id},destructive,soft delete + restore,missing,@team
```

Capability maps prevent accidental UI-only features and make agent support visible in planning.

## 5. Design primitives first

Good primitives are:

- Small enough to explain in one sentence.
- Strongly typed.
- Side effects explicit.
- Output sufficient for the next decision.
- Idempotent or safely retryable where possible.
- Namespaced consistently.
- Not coupled to UI screen names.

Examples:

- Good: `project.list`, `project.get`, `project.create`, `project.update`, `project.archive`, `project.restore`.
- Weak: `manage_project`, `click_dashboard_button`, `run_project_workflow`.

Workflows are still useful, but put them in docs, skills, prompts, or orchestration code that composes primitives.

## 6. Design context intentionally

For each action, ask what a careful human would inspect first.

Common context objects:

- Current workspace/org/project.
- User identity and permissions.
- Active selection/filter/query.
- Available plans, limits, quotas, and feature flags.
- Validation rules and schemas.
- Recent changes and audit trail.
- Related records and dependencies.
- File metadata and provenance.
- Cost, risk, and external visibility.

Expose context as state endpoints, resources, files, prompt context, or tool responses. Avoid requiring agents to scrape it from UI text.

## 7. Make every execution surface agent-friendly

### Web/docs

- Publish `llms.txt` with concise links.
- Offer markdown pages or markdown content negotiation for docs.
- Keep pages small enough to chunk cleanly.
- Give every section a stable anchor.
- Include realistic code examples and output examples.
- Publish current API/tool/CLI contracts and redirect stale docs.

### CLI/TUI

- Every command has `--help` and examples.
- Machine mode is non-interactive.
- Provide `--output json` or equivalent.
- Data goes to stdout; logs/progress/errors go to stderr.
- No spinners/colors/progress bars in machine mode.
- Destructive commands support `--dry-run` and require explicit confirmation flags in automation.
- Commands are idempotent where possible.
- Exit codes are documented.

### API/SDK

- Publish schemas and examples.
- Use consistent pagination, filtering, sorting, and field selection.
- Standardize errors.
- Include idempotency for mutations.
- Use stable object IDs and links.
- Document auth scopes and rate limits.
- Keep SDK methods aligned with API capability names.

### MCP/tools

- Tool names are concise, namespaced, and action-oriented.
- Descriptions explain when to use, side effects, and constraints.
- Inputs are typed and validated.
- Responses are high-signal, not giant raw dumps.
- Resources expose context; tools execute actions; prompts encode workflows.
- Dangerous tools require consent/approval patterns.

### Files

- Use stable file IDs.
- Expose metadata and hashes.
- Support range/chunk access for large files.
- Keep transformations deterministic and logged.
- Preserve originals unless explicitly replacing them.

## 8. Make safety part of the API, not a policy footnote

Agentic systems need explicit safety affordances:

- Separate read-only and write scopes.
- Principle of least privilege.
- Dry-run/preview for high-impact changes.
- Human approval where appropriate.
- Idempotency keys.
- Soft delete/version history/rollback.
- Actor attribution and audit logs.
- Rate limits and cost limits.
- Sandbox/test mode.
- Clear policy for bot/agent access.

Safety friction should be proportional: low-risk reads should be easy; irreversible external actions should be deliberate.

## 9. Define response and error contracts

For every command/tool/API endpoint, define:

- Success shape.
- Error shape.
- Partial success shape.
- Pagination shape.
- Long-running job shape.
- Correlation/request ID.
- Retryability.
- Remediation.

Example error envelope:

```json
{
  "error": {
    "code": "permission_denied",
    "message": "The token lacks deployments:write.",
    "retryable": false,
    "remediation": "Request deployments:write or use a read-only action.",
    "correlation_id": "req_123"
  }
}
```

## 10. Add evals before launch

For each real agent job, create:

- Prompt/task.
- Allowed tools/surfaces.
- Starting state/fixtures.
- Expected final state.
- Assertions.
- Safety expectations.
- Failure examples.

Run evals with and without the agent-use surface. Measure success rate, tool-call count, invalid calls, token use, latency, retries, recoveries, and approval escalations.

## 11. Launch checklist

Before launch, verify:

- Agents can find the right docs from the public entry point.
- Agents can discover available capabilities without guessing names.
- Important UI workflows have agent action paths.
- Important actions expose enough context to choose parameters.
- Machine-readable outputs are parseable and bounded.
- Errors are stable and actionable.
- Destructive actions have preview/approval/rollback as appropriate.
- Auth scopes and rate limits are documented.
- Examples run in CI.
- Evals cover the top tasks.
- Telemetry can identify agent failures.

## 12. Maintenance loop

Agent-usefulness decays unless maintained.

Recommended cadence:

- On every release: validate schemas, CLI help, examples, and docs links.
- Weekly/monthly: review failed agent tasks and invalid tool calls.
- Quarterly: refresh `llms.txt`, `AGENTS.md`, API catalog, MCP card, evals, and templates.
- Before deprecations: add redirects, warnings, migration recipes, and compatibility tests.
