# Action/context parity inventory

Root: `/mnt/data/agent-use-v2/agent-use`

> Starter inventory only. Confirm important workflows manually and map human context to agent context/action/recovery.

## Candidate capability map

| Human capability | Evidence | Agent path candidate | Context needed | Safety/recovery | Status |
| --- | --- | --- | --- | --- | --- |
| UI action | `scripts/agent_use_audit.py:257` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/agent_use_audit.py:258` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/action_parity_inventory.py:16` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| Agent/action surface | `scripts/web_agent_readiness.py:91` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:178` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:191` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:9` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:240` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:241` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:690` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:691` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:5` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:202` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:203` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/generate_llms_txt.py:9` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/generate_llms_txt.py:181` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/generate_llms_txt.py:182` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:5` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:108` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:109` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:128` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:129` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/action_parity_inventory.py:8` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/action_parity_inventory.py:18` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/action_parity_inventory.py:66` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/generate_agent_assets.py:4` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/generate_agent_assets.py:34` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `SKILL.md:54` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `AGENTS.md:15` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `references/audit-playbook.md:46` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:262` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:263` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/action_parity_inventory.py:19` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `assets/schemas/tool-definition.schema.json:6` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `assets/schemas/tool-definition.schema.json:20` | tool_definition | docs/schema/auth | errors/retry/idempotency | candidate |

## Evidence by category

### ui_action
- `scripts/agent_use_audit.py:257` — r"onClick\s*=", r"onSubmit\s*=", r"addEventListener\(['\"]click", r"<button\b", r"<Button\b",
- `scripts/agent_use_audit.py:258` — r"onPressed\s*:", r"onTapGesture", r"TouchableOpacity", r"Pressable", r"button_to", r"form_with",
- `scripts/action_parity_inventory.py:16` — "ui_action":[r"\bonClick\b",r"\bonSubmit\b",r"<button\b",r"Button\(",r"addEventListener\(['\"]click",r"onPressed\b",r"onTap\b"],

### api_route
- `scripts/web_agent_readiness.py:91` — def fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int) -> tuple[EndpointResult, str]:
- `scripts/web_agent_readiness.py:178` — r,b=fetch(label, endpoint, accept, timeout, max_bytes); results.append(r)
- `scripts/web_agent_readiness.py:191` — app=report.get("applicability",{}); lines.append(f"Profile: **{app.get('profile')}** ({app.get('profile_reason')})"); lines += ["","## Scores"]

### cli_command
- `scripts/agent_use_audit.py:9` — import argparse
- `scripts/agent_use_audit.py:240` — r"argparse", r"click\.command", r"typer\.Typer", r"commander", r"yargs", r"oclif",
- `scripts/agent_use_audit.py:241` — r"cobra\.Command", r"clap::Parser", r"picocli", r"console_scripts", r"\[project\.scripts\]",
- `scripts/agent_use_audit.py:690` — def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
- `scripts/agent_use_audit.py:691` — parser = argparse.ArgumentParser(description="Audit a repository/directory for agent-usefulness signals.")
- `scripts/web_agent_readiness.py:5` — import argparse
- `scripts/web_agent_readiness.py:202` — def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace:
- `scripts/web_agent_readiness.py:203` — p=argparse.ArgumentParser(description="Check web/docs agent-readiness discovery endpoints.")
- `scripts/generate_llms_txt.py:9` — import argparse
- `scripts/generate_llms_txt.py:181` — def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
- `scripts/generate_llms_txt.py:182` — parser = argparse.ArgumentParser(description="Generate a draft llms.txt from a docs directory.")
- `scripts/validate_skill.py:5` — import argparse, json, py_compile, re, subprocess, sys
- `scripts/validate_skill.py:108` — content=script.read_text(encoding="utf-8", errors="replace"); helpful="argparse" in content or "from validate_skill import main" in content or "from agent_use_audit import main" in
- `scripts/validate_skill.py:109` — checks.append(Check(f"script-{script.name}","pass" if helpful else "warn","script uses argparse/help patterns or delegates to a validated CLI" if helpful else "script may not expos
- `scripts/validate_skill.py:128` — def parse_args(argv: Optional[Sequence[str]]=None) -> argparse.Namespace:
- `scripts/validate_skill.py:129` — p=argparse.ArgumentParser(description="Validate an Agent Skill package structure and common agent-use assets.")
- `scripts/action_parity_inventory.py:8` — import argparse, csv, fnmatch, os, re, sys
- `scripts/action_parity_inventory.py:18` — "cli_command":[r"argparse",r"click\.command",r"commander\(",r"cobra\.Command",r"yargs",r"clap::",r"process\.argv"],
- `scripts/action_parity_inventory.py:66` — p=argparse.ArgumentParser(description="Inventory candidate UI actions and agent action paths.")
- `scripts/generate_agent_assets.py:4` — import argparse, datetime as dt, re, sys
- `scripts/generate_agent_assets.py:34` — p=argparse.ArgumentParser(description="Scaffold agent-use assets from templates.")

### tool_definition
- `SKILL.md:54` — MCP/A2A/tools: clear names/descriptions, typed schemas, examples, resource and prompt support, server/agent cards, consent model, safe defaults, high-signal responses, no hidden si
- `AGENTS.md:15` — - API/SDK/MCP/A2A/tools: `references/api-sdk-mcp-readiness.md`
- `references/audit-playbook.md:46` — MCP/tools:
- `scripts/agent_use_audit.py:262` — r"input_schema", r"server\.tool\(", r"\.tool\(", r"@tool", r"function_tool",
- `scripts/agent_use_audit.py:263` — r"StructuredTool", r"Tool\(", r"tools\s*[:=]", r"tool_choice", r"function_call",
- `scripts/action_parity_inventory.py:19` — "tool_definition":[r"\btool\s*\(",r"StructuredTool",r"function_call",r"tools\s*[:=]",r"McpServer",r"server\.tool",r"input_schema",r"inputSchema"],
- `assets/schemas/tool-definition.schema.json:6` — "required": ["name", "description", "input_schema"],
- `assets/schemas/tool-definition.schema.json:20` — "input_schema": {"type": "object"},

### context_injection
- `SKILL.md:37` — 4. Design context parity. Inject current resources, capabilities, constraints, user-visible state, recent activity, domain vocabulary, permissions, and completion criteria into the
- `SKILL.md:40` — 7. Make mutations safe. Add dry-run/preview, idempotency keys, scoped permissions, audit logs, confirmation for high-impact actions, sandbox/test mode, and undo/rollback where prac
- `SKILL.md:42` — 9. Ship evals. Compare baseline versus improved surfaces and cover discovery, happy paths, permissions, edge cases, recovery, and regression.
- `SKILL.md:56` — Apps/UIs: action parity, context parity, noun-test coverage, shared workspace, dynamic context injection, prompt-native features, UI reflection of agent mutations, durable links to
- `SKILL.md:78` — - `references/security-recovery.md` — permissions, approval, safety, rollback, privacy, abuse resistance.
- `CHANGELOG.md:15` — - Added deeper references synthesizing the original Compound ideas: action/context parity, noun test, primitives, shared workspace, dynamic context injection, prompt-native behavio
- `references/framework.md:35` — - Explicit prerequisites, permissions, side effects, limits, and failure modes.
- `references/framework.md:90` — - Explicit state endpoints or files for visible UI state, selected records, configuration, permissions, validation rules, active filters, recent activity, and constraints.
- `references/framework.md:91` — - Dynamic context injection when an agent is operating inside an app.
- `references/framework.md:99` — - No way to list changed files/records, current selection, active workspace, or user permissions.
- `references/framework.md:138` — ### 8. Safety, permissions, and governance
- `references/framework.md:218` — - Permissions and ownership.
- `references/framework.md:227` — - Preserve filenames, MIME types, size, hashes, created/modified times, provenance, and permissions.
- `references/audit-playbook.md:25` — - Safety and permissions: auth middleware, policy docs, RBAC, audit logs, destructive operations.
- `references/build-playbook.md:98` — - User identity and permissions.
- `references/surface-guides.md:72` — - Current workspace, project, selected objects, active filters, permissions, limits, and validation rules are available outside the DOM.
- `references/surface-guides.md:81` — - Dynamic context injection: when an embedded agent is used, inject current object IDs, selection, permissions, and relevant state.
- `references/surface-guides.md:239` — - Are permissions and provenance visible?
- `references/scoring-rubric.md:88` — 2: Agents receive partial state but must infer crucial IDs, permissions, limits, or selections.
- `references/scoring-rubric.md:90` — 5: Core resources are readable, but active UI/workspace context, validation rules, permissions, dependencies, or recent changes are missing.
- `references/scoring-rubric.md:92` — 8: Agents can inspect current state, resources, relationships, permissions, constraints, files, and validation rules for important tasks.
- `references/scoring-rubric.md:96` — Evidence to cite: list/get endpoints, state APIs, resources, context payloads, exports, permissions APIs, schemas.
- `references/scoring-rubric.md:126` — ## Dimension 8: Safety, permissions, and governance
- `references/scoring-rubric.md:132` — 5: Basic permissions and confirmations exist, but dry-run, approval, audit logs, or rollback are incomplete.
- `references/evaluation.md:254` — - Context: missing/incorrect IDs, permissions, state, limits, constraints.
- `references/research-notes.md:15` — - **Dynamic context injection**: app-embedded agents should receive current object IDs, selection, permissions, and state.
- `references/agent-native-architecture.md:8` — 2. **Context parity.** Agents need the same domain objects, state, permissions, constraints, recent activity, and completion criteria a competent human operator sees.
- `references/agent-native-architecture.md:11` — 5. **Dynamic context injection.** Static system prompts are not enough. Runtime context should tell the agent what resources exist, what it may do, what state is current, and what 
- `references/agent-native-architecture.md:46` — | Context starvation | Agent sees a static prompt but not current state | Inject workspace, permissions, objects, limits, recent activity |
- `references/agent-native-architecture.md:55` — 1. Find UI actions, route handlers, CLI commands, SDK methods, tool definitions, and system prompt/context construction.
