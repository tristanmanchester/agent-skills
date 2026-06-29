---
name: agent-use
description: Audit or design websites, docs, apps, CLIs/TUIs, APIs, SDKs, MCP/A2A agents, Agent Skills, and repos so AI agents can discover, understand, safely operate, verify, and recover from real tasks. Use for agent-readiness audits, action/context parity reviews, AGENTS.md/llms.txt/OpenAPI/API catalog/MCP/A2A/tool design, CLI JSON/non-interactive ergonomics, shared workspaces, prompt-native features, evals, templates, and implementation roadmaps.
license: MIT
compatibility: Optional scripts require Python 3.10+. Web checks require network access. Repository scans require read access to the target tree.
metadata:
  version: "2.0.0"
  updated: "2026-06-29"
  origin: "Synthesizes deprecated compound agent-native architecture/audit skills with current public agent-readiness practices."
---

# agent-use

Use this skill to make work easier for AI agents to use: easier to discover, easier to understand in a small context window, easier to operate safely, easier to verify, and easier to recover.

Audit mode reviews existing work and produces an evidence-backed score, gap list, and remediation plan. Build mode guides new work so the agent contract is designed before implementation ossifies.

The doctrine: **agents need action parity, context parity, safe primitives, structured outputs, durable state, explicit completion signals, and recovery paths.** Prose helps, but agent-useful systems also provide inspectable contracts, examples, commands, schemas, evals, and stable entry points.

## Audit workflow

1. Classify the target: website/docs, app UI, repository, CLI/TUI, HTTP API, SDK, MCP server, A2A agent, Agent Skill, file/workspace system, mobile app, or mixed product.
2. Gather evidence from applicable surfaces. For repositories, run `scripts/audit_agent_use.py --root <path> --markdown`. For UI/app repos, also run `scripts/action_parity_inventory.py <path> --output action-parity-inventory.md --csv-output capability-map.csv`. For websites, run `scripts/web_agent_readiness.py <url> --markdown --profile auto`. For Agent Skills, run `scripts/validate_agent_assets.py --skill-dir <skill-dir> --run-help --py-compile --markdown`.
3. Build a capability map. List the important things a capable human can see, decide, and do; then map agent-readable context, agent action path, verification path, safety tier, and recovery path.
4. Run the noun test. For every important domain object, ask whether the agent can discover it, identify it, read it, mutate it when appropriate, verify results, and recover from failure.
5. Score only dimensions that apply using `references/scoring-rubric.md`. Mark non-applicable dimensions explicitly rather than penalizing them.
6. Write findings with file paths, URLs, commands, response snippets, schemas, or screenshots. Avoid generic advice that cannot be patched.
7. Prioritize fixes into quick wins, medium work, and structural work. Include evals that prove the improvements help agents complete tasks.

Recommended audit output is in `references/report-template.md`.

## Build workflow

1. Define 5-10 real agent tasks before choosing surfaces. Include read-only tasks, mutation tasks, recovery tasks, permission-sensitive tasks, and long-running tasks if relevant.
2. Publish discovery entry points appropriate to the target: `README`, `AGENTS.md`, `llms.txt`, markdown docs, OpenAPI/GraphQL/JSON Schema, `.well-known/api-catalog`, OAuth/OIDC metadata, `/.well-known/mcp.json`, A2A agent card, CLI `--help`, SDK examples, and an agent skills index.
3. Expose primitives, not brittle workflows. Tools should give agents capability; prompts/docs/recipes should describe behavior. Use workflow tools only when atomicity, safety, performance, or external orchestration justifies them.
4. Design context parity. Inject current resources, capabilities, constraints, user-visible state, recent activity, domain vocabulary, permissions, and completion criteria into the agent path.
5. Design action parity. Core user-visible actions should have agent-accessible paths unless they are intentionally human-only, such as CAPTCHA, biometric prompts, MFA enrollment, or legal consent.
6. Make outputs parseable and bounded. Prefer typed JSON or schema-backed objects for agents and concise markdown for humans. Separate diagnostics from data.
7. Make mutations safe. Add dry-run/preview, idempotency keys, scoped permissions, audit logs, confirmation for high-impact actions, sandbox/test mode, and undo/rollback where practical.
8. Make work resumable. Long-running jobs need progress, checkpoints, partial results, completion signals, and retry/resume tokens.
9. Ship evals. Compare baseline versus improved surfaces and cover discovery, happy paths, permissions, edge cases, recovery, and regression.

Use templates in `assets/templates/` when creating new agent-facing assets.

## What to inspect

Web/docs: `llms.txt`, markdown availability, stable URLs, stale-doc avoidance, robots/sitemap, API catalog, OAuth/OIDC metadata, MCP/A2A discovery, examples, small pages, canonical docs, content access policy, and docs that fit context windows.

CLIs/TUIs: `--help`, `--version`, non-interactive mode, `--output json`, schema introspection, stdout/stderr separation, stable exit codes, explicit error envelopes, dry-run, idempotency, bounded output, no spinners in machine mode, no prompts without `--yes`/`--no-input` alternatives.

APIs/SDKs: OpenAPI/GraphQL/JSON Schema/Protobuf contracts, examples, pagination, consistent errors, idempotency, auth scopes, sandbox mode, webhooks/events, rate-limit metadata, SDK parity with API operations, generated docs, versioning, deprecation policy.

MCP/A2A/tools: clear names/descriptions, typed schemas, examples, resource and prompt support, server/agent cards, consent model, safe defaults, high-signal responses, no hidden side effects, task lifecycle for asynchronous work.

Apps/UIs: action parity, context parity, noun-test coverage, shared workspace, dynamic context injection, prompt-native features, UI reflection of agent mutations, durable links to entities/files, approval matrix, audit trail, latent-demand capture.

Files/workspaces/mobile: files as a universal interface, explicit working directories, safe self-modification, checkpoints, offline/battery/network constraints, background execution policy, conflict resolution, and inspectable artifacts.

Agent Skills: precise trigger description, compact `SKILL.md`, progressive disclosure through references/assets/scripts, runnable helpers, eval seeds, versioning, and backwards-compatible commands.

## References

Load only the needed reference:

- `references/framework.md` — overall agent-use model and dimensions.
- `references/scoring-rubric.md` — scoring rubric, maturity levels, evidence standards, severity definitions.
- `references/audit-playbook.md` — detailed audit process for existing systems.
- `references/build-playbook.md` — design process for new agent-useful work.
- `references/review-recipes.md` — full-repo, PR, and parallel-review recipes.
- `references/agent-native-architecture.md` — action/context parity, noun test, prompt-native behavior, shared workspace, completion signals.
- `references/web-and-docs-readiness.md` — web/docs discovery, llms.txt, API catalog, OAuth/OIDC, MCP/A2A discovery.
- `references/cli-tui-readiness.md` — CLI/TUI contract patterns.
- `references/api-sdk-mcp-readiness.md` — API, SDK, MCP, A2A, and tool design.
- `references/app-ui-and-workspace-readiness.md` — action/context parity, shared workspace, prompt-native product patterns.
- `references/files-mobile-and-long-running-work.md` — files, mobile/offline, checkpoints, background execution, self-modification.
- `references/agent-instructions-and-skills.md` — AGENTS.md, Agent Skills, llms.txt, and instruction assets.
- `references/security-recovery.md` — permissions, approval, safety, rollback, privacy, abuse resistance.
- `references/evaluation.md` — evals, observability, decay prevention, release checks.
- `references/report-template.md` — audit report template.
- `references/original-compound-comparison.md` — what changed versus the original deprecated compound skills.
- `references/source-map.md` — source synthesis and standards map.

## Scripts

- `scripts/audit_agent_use.py --root <repo-or-dir> --markdown` scans local projects for agent-use signals. `scripts/agent_use_audit.py` remains as a v1-compatible entry point.
- `scripts/action_parity_inventory.py <repo-or-dir> --output action-parity-inventory.md --csv-output capability-map.csv` inventories UI actions and candidate agent paths.
- `scripts/web_agent_readiness.py <url> --markdown --profile auto` checks web discovery and agent-readiness endpoints with profile-aware scoring.
- `scripts/generate_llms_txt.py <docs-root> --site-url <url> --output llms.txt` drafts an `llms.txt`.
- `scripts/generate_agent_assets.py --root <project> --project-name <name> --surface all` scaffolds common agent-facing files.
- `scripts/validate_agent_assets.py --skill-dir <skill-dir> --run-help --py-compile --markdown` validates this or another Agent Skill. `scripts/validate_skill.py` remains as a v1-compatible entry point.

## Quality bar

A recommendation is good only if an engineer can implement it, a PM can prioritize it, and an evaluator can test whether it worked.

Do not equate agent-useful with fully autonomous. A high-quality agent path may require explicit human approval for high-impact changes.

Do not count prose alone as implementation evidence. Good docs can guide agents, but actual capability needs contracts, scripts, tools, schemas, tests, and working routes.

Do not flag intentionally human-only flows as action-parity failures. Document the boundary and provide a safe agent alternative when one exists.
