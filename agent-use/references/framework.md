# Agent-use framework

Agent-usefulness is the degree to which an AI agent can discover, understand, operate, verify, and recover while using a system to complete real user goals.

This is broader than “has an API” or “has an MCP server.” A system is agent-useful when all important capability surfaces are coherent: docs, web pages, UI, CLI, API, SDK, tool server, files, examples, auth, logging, and evals. The agent does not need every human affordance, but it needs a reliable path to the same meaningful outcomes.

## The ten dimensions

### 1. Discoverability

Agents need obvious entry points. Good systems answer: “What is this? What can I do? Where are the machine-readable contracts? What should I not do?”

Strong signals:

- A high-quality `README` and/or `AGENTS.md` at repo root.
- `llms.txt` for documentation-heavy websites.
- Sitemap and robots policy that do not accidentally hide useful docs.
- Stable links to OpenAPI, GraphQL, JSON Schema, SDK docs, CLI docs, MCP server card, API catalog, changelog, examples, and support policy.
- Capability summaries that use intent language, not only product marketing.

Weak signals:

- Critical docs only in screenshots, videos, dynamic search UIs, gated pages, or large undifferentiated pages.
- Docs that require knowing product-specific names before discovery.
- Stale duplicate docs with no redirect or deprecation marker.

### 2. Content readability

Agents need compact, current, linkable content. Human-readable does not always mean agent-readable.

Strong signals:

- Markdown or clean HTML docs with headings, anchors, code examples, and stable URLs.
- Pages small enough to fit into context or chunk cleanly.
- Explicit prerequisites, permissions, side effects, limits, and failure modes.
- Examples that include realistic inputs and outputs.
- “Do this, then this” recipes for common goals, separated from primitive API/tool references.

Weak signals:

- Giant reference pages with no summaries or anchors.
- Missing output examples.
- Content split across hidden tabs, modals, accordions, JavaScript-only rendering, or images.
- Stale docs that outrank current docs in search.

### 3. Capability contracts

Agents work better when capabilities are specified in a machine-readable contract.

Strong signals:

- OpenAPI, AsyncAPI, GraphQL schema, JSON Schema, protobuf, Smithy, TypeSpec, or typed SDK docs.
- CLI help that is stable and exhaustive.
- MCP/tool definitions with names, descriptions, input schemas, examples, and response schemas.
- Versioned contracts and changelog.
- Contract tests that detect drift between docs and implementation.

Weak signals:

- Blog-post-only integration docs.
- Handwritten examples that no longer run.
- Flags, parameters, or response fields that exist but are not documented.
- Hidden workflows known only to the UI.

### 4. Action parity

Every important human action should have a corresponding agent-usable path. The path can be a CLI command, API endpoint, SDK method, MCP tool, file operation, or skill script.

Strong signals:

- A capability map from UI workflows to agent actions.
- Create/read/update/delete/list/search/export/import parity where applicable.
- Bulk and batch operations for repetitive work.
- Preview/dry-run for destructive or costly operations.
- Stable identifiers and durable links for objects.

Weak signals:

- Agents can read state but cannot act on it.
- Agents can act only through browser automation of brittle UI flows.
- UI has privileged workflows that no API/CLI/tool exposes.
- Agent path exists but lacks the context necessary to choose correctly.

### 5. Context parity

Agents need access to the same decision-relevant context a competent user would see.

Strong signals:

- Explicit state endpoints or files for visible UI state, selected records, configuration, permissions, validation rules, active filters, recent activity, and constraints.
- Dynamic context injection when an agent is operating inside an app.
- Inspectable resource models: records, relationships, provenance, timestamps, ownership, status, and links.
- Context that is current and scoped to the task.

Weak signals:

- Key state hidden in the browser DOM, a canvas, hover text, charts, or screenshots.
- Agents receive only natural-language summaries with no identifiers.
- No way to list changed files/records, current selection, active workspace, or user permissions.

### 6. Composability and primitive quality

Agents are good at planning when tools are clean primitives. Avoid forcing them into rigid magic workflows unless the workflow is truly atomic.

Strong signals:

- Tools do one clear job and compose naturally.
- Inputs are typed and explicit.
- Responses include enough data to decide the next step.
- Higher-level recipes live in docs/prompts, not inside opaque tools.
- Related operations are namespaced consistently.

Weak signals:

- A single overloaded `do_everything` operation.
- Tool names tied to UI labels rather than user intent.
- Hidden side effects, implicit global state, or output that depends on previous calls in undocumented ways.

### 7. Parseable, bounded outputs

Agents must parse outputs reliably and avoid wasting context.

Strong signals:

- JSON/schema output for machine mode.
- Human summaries in markdown when appropriate.
- Pagination, filtering, field selection, and maximum result limits.
- Diagnostics separate from data.
- Error envelopes with codes, messages, retryability, remediation, and correlation IDs.

Weak signals:

- Tables intended only for terminals.
- Spinners, progress bars, colors, or logs mixed into JSON.
- Unbounded list operations.
- Free-form errors without codes or next steps.

### 8. Safety, permissions, and governance

Agent-useful systems make safe paths easy and dangerous paths explicit.

Strong signals:

- Scoped auth, least privilege, clear permission errors, and auditable actions.
- Separate read-only and write-capable credentials.
- Dry-run/preview before destructive, costly, external, or irreversible actions.
- Human confirmation gates for high-impact actions.
- Rollback, undo, soft delete, version history, and immutable audit logs where appropriate.
- Policy docs that describe allowed automation and bot access.

Weak signals:

- All-or-nothing tokens.
- Write endpoints with no preview or idempotency.
- Ambiguous permission errors.
- No record of agent actions.

### 9. Recovery and resilience

Agents make mistakes, networks fail, and tasks get interrupted. Good systems expose recovery handles.

Strong signals:

- Idempotency keys for create/update operations.
- Retryable error classification.
- Pagination cursors and resume tokens.
- Checkpoints and partial-progress records for long jobs.
- Conflict detection, optimistic concurrency, transactions, and rollback plans.
- Test/sandbox environments.

Weak signals:

- “Try again later” errors with no code.
- Duplicate side effects on retry.
- Long-running jobs with no status endpoint.
- Partial success that cannot be inspected.

### 10. Evals and observability

Agent-usefulness should be tested with real tasks, not just asserted.

Strong signals:

- Eval tasks from actual user workflows.
- Baselines with and without agent-use features.
- Assertions over final state, not only text quality.
- Logs for tool calls, error rates, retries, token usage, latency, and user approvals.
- Regression tests for docs examples, CLI JSON output, OpenAPI validity, tool schemas, and permission failures.

Weak signals:

- No examples runnable by an agent.
- Success measured only by subjective manual review.
- No telemetry on agent failures, repeated docs searches, invalid tool calls, or abandoned workflows.

## The parity triad

A mature system aligns three forms of parity.

**Action parity** means agents can perform important actions through stable surfaces.

**Context parity** means agents can see enough state and constraints to decide when and how to act.

**Recovery parity** means agents can check, undo, resume, or repair the consequences of action.

A product with action parity but weak context parity lets agents cause damage confidently. A product with context parity but no action parity forces agents into browser automation or asks humans to do every step. A product with both but no recovery parity fails under normal agentic iteration.

## Shared workspace principle

Prefer shared durable objects over chat-only artifacts. Agents and users should operate on the same records, files, branches, tickets, projects, tasks, and logs.

Good shared workspaces expose:

- Stable object IDs and URLs.
- Object metadata and relationships.
- Version history.
- Comments and approvals.
- Permissions and ownership.
- Agent attribution.
- Change summaries and diffs.

## The universal file interface

When a system deals with files, make them first-class:

- Upload, download, list, search, preview, transform, and delete where applicable.
- Preserve filenames, MIME types, size, hashes, created/modified times, provenance, and permissions.
- Provide streaming or chunked access for large files.
- Let agents reference files by stable IDs, not brittle UI labels.
- Include safe conversion paths for PDFs, images, spreadsheets, slides, archives, and code.

## Agent-use maturity levels

Level 0: Human-only. Important state/actions live only in UI or human docs.

Level 1: Readable. Agents can read docs and some state, but action paths are incomplete.

Level 2: Scriptable. Agents can use CLIs/APIs/tools for common workflows with some structured output.

Level 3: Reliable. Discovery, schemas, parity, safety, recovery, and examples cover most important workflows.

Level 4: Measured. Agent-usefulness is tested, monitored, and improved with task-level evals.

Level 5: Agent-native. Product architecture assumes human-agent collaboration: shared workspace, dynamic context, composable primitives, safe delegation, and continuous eval feedback.

## Design heuristics

- Make the obvious path the safe path.
- Prefer stable identifiers over names and positions.
- Prefer small typed primitives plus documented recipes over hidden mega-tools.
- Show examples with real outputs.
- Return actionable errors.
- Bound everything that can grow.
- Separate data from diagnostics.
- Keep public docs canonical and redirect stale material.
- Treat tool descriptions, CLI help, schemas, and examples as product surfaces.
- Test the agent journey, not just the API endpoint.
