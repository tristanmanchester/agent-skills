# App UI and workspace readiness

Use this when auditing or designing products where humans use an app UI but agents also need to act.

## Action parity

Inventory every important button, form, menu action, bulk action, import/export, approval, destructive flow, and configuration change. Then map each to a stable agent path. Browser automation is a fallback, not a durable contract.

Agent paths can be API endpoints, CLI commands, SDK methods, MCP/tools, files, or controlled background tasks. The path must expose all required parameters and validation rules, return IDs/links, and offer verification.

## Context parity

Agents need access to current workspace, selected project, active filters, table data, chart underlying data, object IDs, permissions, limits, validation rules, recent activity, and current user intent. Avoid hiding decisive state only in the DOM, canvas, screenshot, hover tooltip, modal, or client-only store.

## Shared workspace

Agent outputs should land where users can inspect and edit them: records, drafts, comments, files, tickets, branches, pull requests, notebooks, or artifacts. The UI should reflect agent mutations through shared state, event streams, polling, or file watching.

## Prompt-native product patterns

Some features are better expressed as agent goals and policies than as rigid UI forms. Capture latent demand from user prompts, expose capability hints, and let useful repeated prompts graduate into templates, skills, or product affordances.

## Review red flags

- Agent can chat but cannot perform core CRUD.
- Agent can mutate but user cannot see what changed.
- Agent has stale or incomplete runtime context.
- UI has exportable data but no API/CLI/tool equivalent.
- Approval prompts lack diff, target IDs, side effects, or rollback plan.
- Multi-step work has no checkpoint, resume, or cancellation.
