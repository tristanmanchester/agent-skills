# Surface guides

Use these guides to inspect or design specific surfaces. Many products combine several surfaces; judge the whole agent journey, not each surface in isolation.

## Repository and project layout

Agent-useful repositories let an agent orient itself quickly, modify safely, and validate changes.

Minimum useful set:

- `README.md`: project purpose, setup, run, test, build, deploy, architecture pointers.
- `AGENTS.md`: agent-specific instructions, safe commands, coding conventions, known traps, validation commands, ownership boundaries.
- `CONTRIBUTING.md`: development workflow and review expectations.
- `docs/`: architecture and domain concepts.
- `scripts/`: deterministic helpers with `--help`.
- `examples/`: small realistic runnable examples.
- `tests/` and/or `evals/`: validation fixtures.
- Machine contracts: OpenAPI, JSON Schema, CLI references, tool schemas.

Audit checks:

- Can an agent install dependencies without guessing?
- Can it run a targeted test and full test?
- Can it tell generated files from hand-edited files?
- Are formatting/linting commands documented?
- Are secrets, credentials, and destructive deploy commands clearly marked?
- Are common failure messages documented?

Design recommendations:

- Put agent instructions in `AGENTS.md`, not hidden in chat prompts.
- Make scripts idempotent and non-interactive.
- Include minimal fixtures for local validation.
- Use stable path names and avoid burying core docs in search-only systems.

## Documentation websites

Agent-useful docs are discoverable, compact, canonical, and linkable.

Signals to look for:

- `/llms.txt` with concise links to the most important docs.
- `/llms-full.txt` only if useful and not too large.
- Markdown page variants or content negotiation.
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

## Web apps and UI workflows

A UI can be excellent for humans and still hostile to agents if actions and state are trapped in the interface.

Action parity checklist:

- List every important button, form, bulk action, import/export, approval, configuration, and destructive action.
- Identify the corresponding API/CLI/tool/SDK path.
- Check that the action path exposes all required parameters and validation rules.
- Check that mutation responses return durable IDs and links.
- Check that the action can be previewed, retried, and audited.

Context parity checklist:

- Current workspace, project, selected objects, active filters, permissions, limits, and validation rules are available outside the DOM.
- Charts/tables have exportable underlying data.
- Files and records have stable IDs.
- Multi-step workflows expose checkpoint state.
- Error states are machine-readable.

Design patterns:

- Shared workspace: users and agents collaborate on the same objects.
- Dynamic context injection: when an embedded agent is used, inject current object IDs, selection, permissions, and relevant state.
- Agent action drawer: show what the agent will do, why, and what it needs from the user.
- Change preview: provide a diff or summary before applying writes.
- Audit trail: record actor, action, target, parameters, result, and rollback link.

## CLIs

Agent-friendly CLIs are stable APIs with a shell syntax.

Required patterns:

- `--help` on every command and subcommand.
- `--version` at top level.
- Non-interactive operation for automation.
- `--output json` or `--format json` for all data-producing commands.
- Data on stdout; diagnostics, progress, and logs on stderr.
- Bounded output: pagination, `--limit`, `--cursor`, `--fields`, filtering.
- Stable documented exit codes.
- Clear error envelope in JSON mode.
- `--dry-run` for side-effecting commands.
- Idempotency keys or deterministic create semantics where possible.
- Explicit `--yes`/`--force` only for automation-safe confirmation bypasses, never silent destructive defaults.

Avoid:

- Required interactive prompts with no flags.
- Spinners/progress bars in machine mode.
- Tables as the only output.
- Changing command names/flags without deprecation.
- Hidden network writes in commands that look read-only.
- Color escape codes in JSON.

Recommended command taxonomy:

```text
product resource list --output json --limit 50
product resource get <id> --output json
product resource create --name ... --dry-run --output json
product resource update <id> --field ... --output json
product resource delete <id> --dry-run --output json
product job status <job-id> --output json
```

## TUIs

TUIs are often interactive by design. To make them agent-useful, expose an equivalent machine path.

Good patterns:

- Every TUI workflow maps to CLI/API commands.
- TUI can export/import state as JSON.
- Prompts show equivalent CLI command.
- Logs and final output are available in files.
- No critical capability exists only behind arrow-key navigation.

A TUI does not need to be agent-operated directly. The agent should usually use the underlying CLI/API and leave the TUI for humans.

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

Mutation response checklist:

- Return created/updated object ID.
- Return status and links.
- Return warnings and partial-success information.
- Include request/correlation ID.
- Include next action when operation is asynchronous.

## SDKs

SDKs should not hide capability gaps.

Checks:

- SDK methods align with API operation names and docs.
- Types are exported and documented.
- Async/pagination helpers are ergonomic but not opaque.
- Errors preserve API error codes and details.
- Examples cover auth, common operations, pagination, retries, and idempotency.
- Generated SDK docs link back to canonical API schema.
- SDK includes dry-run/preview where the API supports it.

Agent-specific tip: include one-file examples that can be copied and modified. Agents often succeed faster when examples show full setup, auth, call, output, and cleanup.

## MCP and other tool servers

MCP/tool servers are agent-facing APIs. Treat tool definitions as contracts.

Tool design checklist:

- Names are namespaced, concise, and intent-oriented.
- Descriptions state when to use the tool, what it does, side effects, and constraints.
- Input schemas are precise, required fields are clear, enums are used where possible, and examples are supplied.
- Output shapes are stable and documented.
- Large outputs are summarized and paginated.
- Resources expose context that does not require side effects.
- Prompts encode repeatable workflows and best practices.
- Dangerous actions are gated or previewable.
- Tool errors include stable codes and remediation.

Avoid:

- Tool names like `run`, `execute`, `manage`, or `do_task` without a namespace.
- Free-form JSON blobs where typed objects are possible.
- Returning enormous raw API responses by default.
- Tools that silently mutate state during reads.
- Tools that require the agent to know invisible IDs without lookup tools.

## Agent skills

A good skill is compact at the top and rich on demand.

Checks:

- `SKILL.md` frontmatter has valid `name` and clear `description`.
- Description explains when to use the skill using the user’s likely phrasing.
- `SKILL.md` gives the default workflow and routes to references.
- Long material is in `references/`.
- Deterministic helpers are in `scripts/` and are non-interactive.
- Templates/assets are in `assets/`.
- Evals include trigger and non-trigger queries plus output tests.
- Scripts support `--help`, clear errors, structured output, and safe defaults.

Common fixes:

- Replace vague descriptions with intent-based trigger descriptions.
- Split giant `SKILL.md` into progressive-disclosure references.
- Add scripts for repetitive deterministic tasks.
- Add templates for common outputs.
- Add evals that compare with and without the skill.

## Files and artifacts

Files are often the bridge between humans, tools, and agents.

Checks:

- Can agents list and inspect files with metadata?
- Can they read large files in chunks?
- Can they preserve originals and write outputs separately?
- Are generated files marked as generated?
- Are binary formats convertible to inspectable text or images?
- Are filenames stable enough, or are IDs needed?
- Are permissions and provenance visible?

Good patterns:

- Always return file ID, name, MIME type, size, hash, created/modified time, and source.
- Provide previews for PDFs, images, spreadsheets, and slides.
- Keep sidecar manifests for generated artifacts.
- Support diffing or review before overwrite.
- Use archives only when necessary, with a manifest.

## Databases and data warehouses

Agent-useful data systems need safety and schema visibility.

Checks:

- Read-only credentials available.
- Schema introspection and table descriptions.
- Row limits by default.
- Query timeout and cost limits.
- Dry-run/explain plan.
- No accidental writes from default tools.
- Query results are downloadable in structured format.
- PII and sensitive fields are labeled.

## Long-running jobs

Agents need to monitor and resume long tasks.

Required patterns:

- Job creation returns `job_id` immediately.
- Job status endpoint includes state, progress, logs, warnings, output links, error details, and retryability.
- Jobs are idempotent or deduplicated by idempotency key.
- Jobs can be cancelled when safe.
- Completed jobs retain outputs long enough for review.

## Notifications and webhooks

Agent-friendly event systems expose contracts and replay.

Checks:

- Event schemas are versioned.
- Delivery signatures and verification are documented.
- Retry semantics are clear.
- Events have IDs and timestamps.
- Replay/backfill is available.
- Test events and local development are supported.

## Auth and onboarding

Agents often fail before using the product because auth is unclear.

Good docs include:

- Token creation steps.
- Scopes and least-privilege examples.
- Service accounts or bot users.
- OAuth metadata where applicable.
- Expiration/rotation policy.
- Sandbox credentials.
- Permission error examples.
- How to tell whether a credential is read-only.

## Observability

You cannot improve agent-usefulness without seeing where agents fail.

Track:

- Invalid tool/API/CLI calls.
- Most searched docs pages.
- Repeated docs retrieval before failure.
- Error codes encountered by agents.
- Retry and recovery success.
- Tool-call count per task.
- Approval requests and denials.
- Latency and token use.
- Human corrections after agent actions.
