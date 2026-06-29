# Agent-use scoring rubric

Score only applicable dimensions. A docs-only site should not be penalized for lacking a TUI; a CLI-only package should not be penalized for lacking a web app. Explain applicability.

## Overall formula

For each applicable dimension, assign 0-10. Overall score is:

```text
overall = round(mean(applicable_dimension_scores) * 10)
```

Grades:

- 90-100: A, agent-native.
- 80-89: B, strongly agent-useful.
- 70-79: C, usable with gaps.
- 50-69: D, fragile or partial.
- 0-49: F, mostly hostile or unsafe for agents.

Severity labels:

- Critical: blocks most useful agent tasks or creates serious safety risk.
- High: blocks important tasks or causes likely wrong actions.
- Medium: increases friction, cost, or failure rate.
- Low: polish, consistency, or maintainability issue.

## Dimension 1: Discoverability

0: No clear entry point. Agents must guess from search, UI, or code.

2: Human docs exist but no agent-oriented index, no stable machine contract links, and current/stale docs are hard to distinguish.

5: Basic README/docs exist with some links to capabilities, but discovery is incomplete or inconsistent across surfaces.

8: Clear canonical docs, `AGENTS.md`/automation guidance where relevant, links to specs, examples, auth, errors, changelog, and support.

10: Excellent discovery across repo and web: `llms.txt`/agent index/API catalog where relevant, stable canonical URLs, redirects for stale docs, current capability map, and explicit automation policy.

Evidence to cite: root docs, docs homepage, `llms.txt`, sitemap, API spec links, CLI help, server card, search behavior.

## Dimension 2: Content readability

0: Critical content unavailable or locked in screenshots/videos/JS-only UI.

2: Sparse prose with missing prerequisites, examples, outputs, or limits.

5: Adequate human docs, but pages are large, examples incomplete, or outputs/errors underdocumented.

8: Clean markdown/HTML, stable anchors, realistic examples with outputs, clear prerequisites, limits, errors, auth, and versioning.

10: Compact multi-format docs optimized for both humans and agents, canonical references, page-size discipline, runnable examples, and stale-content controls.

Evidence to cite: docs pages, markdown variants, examples, page sizes, anchors, output samples.

## Dimension 3: Capability contracts

0: No machine-readable or stable contract.

2: Partial/handwritten contract that omits many parameters or responses.

5: Schema/help/tool definitions exist but are incomplete, stale, or not linked from discovery surfaces.

8: Machine-readable contracts cover major capabilities with examples, validation, and versioning.

10: Contracts are canonical, tested against implementation, versioned, linked, and cover API/CLI/SDK/tool parity with examples and response/error schemas.

Evidence to cite: OpenAPI, GraphQL, JSON Schema, CLI help, SDK types, MCP/tool schemas, contract tests.

## Dimension 4: Action parity

0: Agents cannot perform important actions except by brittle UI automation.

2: Read-only or toy action paths; most important workflows are UI-only.

5: Common actions are exposed, but CRUD/bulk/import/export/admin/approval/destructive workflows have major gaps.

8: Important workflows have API/CLI/SDK/tool paths with stable IDs and useful mutation responses.

10: Full intentional action parity across important human workflows, with capability map, batch operations, preview/dry-run, and parity tests.

Evidence to cite: UI actions, routes/endpoints, CLI commands, SDK methods, tool names, capability map.

## Dimension 5: Context parity

0: Agents cannot inspect decision-relevant state.

2: Agents receive partial state but must infer crucial IDs, permissions, limits, or selections.

5: Core resources are readable, but active UI/workspace context, validation rules, permissions, dependencies, or recent changes are missing.

8: Agents can inspect current state, resources, relationships, permissions, constraints, files, and validation rules for important tasks.

10: Dynamic task-scoped context is available, complete, current, and safely bounded; agents can inspect the same decision-relevant context as competent users.

Evidence to cite: list/get endpoints, state APIs, resources, context payloads, exports, permissions APIs, schemas.

## Dimension 6: Composability and primitive quality

0: No usable primitives.

2: One-off opaque workflows with hidden side effects.

5: Some primitives exist but naming, schemas, outputs, or side-effect boundaries are inconsistent.

8: Operations are clear, typed, namespaced, composable, and aligned with domain objects.

10: Excellent primitive design with recipes/prompts layered on top, high-signal responses, safe side-effect boundaries, and compositional eval coverage.

Evidence to cite: tool definitions, endpoint design, CLI taxonomy, SDK methods, examples, workflows.

## Dimension 7: Parseable, bounded outputs

0: Outputs are unparseable or unavailable.

2: Tables/logs/free text only; errors have no codes.

5: Some JSON/schema output exists but not universal; pagination/error handling inconsistent.

8: Structured output for major surfaces, stdout/stderr separation for CLIs, pagination/limits, standard errors, and examples.

10: Fully documented stable output and error contracts, bounded by default, with schemas, field selection, pagination, and tested parsing.

Evidence to cite: command output, API responses, schemas, error examples, pagination docs.

## Dimension 8: Safety, permissions, and governance

0: Unsafe for agent actions; broad tokens, irreversible writes, no auditability.

2: Some auth exists but scopes, side effects, or destructive actions are unclear.

5: Basic permissions and confirmations exist, but dry-run, approval, audit logs, or rollback are incomplete.

8: Scoped auth, clear permission docs, dry-run/preview, human approval for high-risk actions, audit logs, and safe defaults.

10: Comprehensive least-privilege model, policy-aware automation, reversible workflows, sandboxing, actor attribution, review/approval, and governance telemetry.

Evidence to cite: auth docs, scopes, permission errors, destructive command behavior, audit log, dry-run, approvals.

## Dimension 9: Recovery and resilience

0: Agent failures cause duplicate, stuck, or unrecoverable state.

2: Retry/resume/rollback mostly absent.

5: Some retry/pagination/job status patterns exist, but not consistently.

8: Idempotency, retryable errors, pagination, job status, partial success, conflict detection, and rollback cover key workflows.

10: Recovery is a first-class design: resumable operations, checkpoints, compensation, conflict-safe updates, clear retry semantics, and recovery evals.

Evidence to cite: idempotency docs, job APIs, retry headers, pagination, rollback/undo, transactions, error retryability.

## Dimension 10: Evals and observability

0: No evidence agent use has been tested.

2: Manual demos only.

5: Some examples/tests exist, but not task-level agent evals or telemetry.

8: Realistic task evals, baseline comparison, assertions over state, example validation, and basic agent-failure telemetry.

10: Continuous eval loop tied to product telemetry, regression fixtures, safety evals, docs/schema/example tests, and measured improvement over time.

Evidence to cite: evals, fixtures, CI, telemetry dashboards, logs, test outputs, example validation.

## Weighting adjustments

Default weights are equal. Adjust only when justified by the target.

Examples:

- Docs website: weight discoverability, content readability, and capability contracts higher.
- CLI package: weight CLI parseability, non-interactivity, errors, and idempotency higher.
- MCP server: weight tool descriptions, schemas, safety, and evals higher.
- App with agent feature: weight action parity, context parity, shared workspace, safety, and recovery higher.
- SDK: weight capability contracts, examples, typed errors, and parity with API higher.

When using adjusted weights, state them in the report.

## Common score interpretation

### 90+

Agents can discover, understand, act, verify, and recover for the main workflows. Remaining work is mostly optimization, breadth, or domain-specific polish.

### 70-89

Agents can do useful work but hit gaps in discovery, structured output, safety, or recovery. High-leverage fixes likely produce immediate improvement.

### 50-69

Agents can use parts of the system with careful prompting or manual steering. Failures are likely in multi-step tasks.

### Below 50

The system is not yet a reliable agent surface. Invest first in canonical docs, structured contracts, basic action/context parity, and safe non-interactive execution.
