# Source synthesis and standards map

This skill synthesizes three groups of material.

## 1. Deprecated Compound agent-native skills supplied by the user

Preserved concepts:

- Action parity and context parity.
- Shared workspace architecture.
- Tools as primitives and justified workflow tools.
- Dynamic context injection.
- Noun-test/CRUD completeness thinking.
- UI integration and visible agent mutations.
- Capability discovery.
- Prompt-native behavior.
- Files as universal interface.
- Mobile/background/checkpoint constraints.
- Self-modification guardrails.
- Product feedback loops and latent demand.
- Parallel audit structure and scored findings.

## 2. Current public web/agent-readiness practices

Mapped into this skill:

- Website/docs readiness dimensions: discovery, content readability, capability exposure, access/safety, and maintenance.
- `llms.txt` as a concise markdown entry point for LLM-friendly documentation.
- API catalog discovery through `/.well-known/api-catalog` using Linkset JSON.
- OAuth/OIDC protected-resource and authorization-server metadata for agent-accessible protected APIs.
- MCP discovery through `/.well-known/mcp.json` and tool/server cards.
- Agent skills indexes and A2A-style agent cards where applicable.

## 3. Agent-facing interface design patterns

Mapped into this skill:

- CLI/TUI machine mode: non-interactive operation, JSON output, stdout/stderr separation, schema introspection, stable exit codes, and bounded output.
- API/SDK contracts: OpenAPI/GraphQL/JSON Schema/Protobuf, auth scopes, pagination, idempotency, rate limits, errors, sandbox, webhooks/events, and versioning.
- Tool design: precise names/descriptions, typed schemas, bounded outputs, resource/context separation, prompts/recipes, preview/approval for dangerous actions, stable error envelopes.
- Evaluation: task-level success, baseline comparison, final-state assertions, recovery paths, safety checks, and regression tests.
