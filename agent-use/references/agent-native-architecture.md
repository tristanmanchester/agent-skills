# Agent-native architecture

This reference preserves the strongest ideas from the original Compound skills and generalizes them beyond a single app stack.

## Core principles

1. **Action parity.** Every important human action should have an agent-accessible path unless it is intentionally human-only. The path can be API, CLI, SDK, MCP/tool, file operation, or controlled UI automation. Parity is about outcomes, not copying every click.
2. **Context parity.** Agents need the same domain objects, state, permissions, constraints, recent activity, and completion criteria a competent human operator sees.
3. **Shared workspace.** Agents and humans should collaborate in durable, inspectable state: files, records, branches, drafts, tickets, tasks, or artifacts. Avoid hidden sandboxes unless isolation is the explicit product model.
4. **Primitives over workflows.** Expose composable capabilities. Use workflow tools only when atomicity, safety, performance, or external orchestration makes primitive-by-primitive execution risky or wasteful.
5. **Dynamic context injection.** Static system prompts are not enough. Runtime context should tell the agent what resources exist, what it may do, what state is current, and what success means now.
6. **Prompt-native behavior.** Behavior that is inherently judgment-based should often be represented as prompts, policies, examples, and evals rather than hard-coded branching.
7. **Completion and recovery.** Agents need explicit done states, progress, partial results, checkpoints, retries, and failure semantics.

## The noun test

After mapping actions, map domain nouns. For each important object, ask:

| Question | Evidence to seek |
| --- | --- |
| Can the agent discover the object type? | Docs, schema, examples, tool/resource lists |
| Can the agent identify a specific object? | Stable IDs, URLs, search/list operations, file paths |
| Can the agent read enough context? | Get/list/export operations, resource views, data exports |
| Can the agent act when appropriate? | Create/update/delete/archive/import/export primitives |
| Can it verify the action? | Mutation response, status endpoint, UI reflection, audit log |
| Can it recover? | Undo, rollback, soft delete, idempotency, checkpoints |

## Capability map

Use this for app, API, CLI, and tool reviews.

| Human workflow | Human context | Agent-readable context | Agent action path | Safety level | Recovery path | Status |
| --- | --- | --- | --- | --- | --- | --- |
| Create project | org selector, form validation | org list, project schema, scopes | POST /projects or tool `project.create` | write | archive/delete project | planned |
| Delete production resource | settings page, danger copy | resource details, dependents, dry-run diff | API/CLI/tool with approval token | destructive | soft restore/backups | missing |

## Human-only exceptions

Do not flag these as parity failures by default: CAPTCHA, biometric prompts, MFA enrollment, OAuth consent screens, app-store permission prompts, legal acceptance, password entry, and other ceremonies designed to prove human presence or legal consent. Do flag the absence of an appropriate alternative, such as service accounts, scoped tokens, admin approval flows, or documented delegation.

## Anti-patterns

| Anti-pattern | Signal | Fix |
| --- | --- | --- |
| Orphan feature | UI action has no API/CLI/tool/SDK path | Add an agent path or document the human-only boundary |
| Context starvation | Agent sees a static prompt but not current state | Inject workspace, permissions, objects, limits, recent activity |
| Sandbox isolation | Agent outputs land where users cannot inspect/edit | Use shared records/files/drafts or clear artifact links |
| Silent mutation | Agent changes state but UI/logs do not reflect it | Emit events, update shared store, expose audit trail |
| Workflow blob | Tool encodes decisions and hidden side effects | Split primitives or justify workflow atomicity/safety |
| Giant response | Tool/API dumps unbounded data | Add pagination, summaries, fields, cursors |
| Decision enum as input | Tool asks agent to pass business decision category only | Accept evidence/data and let prompt/policy decide |

## Review steps

1. Find UI actions, route handlers, CLI commands, SDK methods, tool definitions, and system prompt/context construction.
2. Build the action map first, then run the noun test.
3. Separate must-have workflows from low-priority or cosmetic actions.
4. Inspect mutation responses. They should return IDs, links, status, warnings, and next actions.
5. Inspect runtime context. The agent path should not depend on guessing hidden IDs or reading a brittle DOM.
6. Add evals for at least one read task, one mutation task, one permission failure, and one recovery path.
