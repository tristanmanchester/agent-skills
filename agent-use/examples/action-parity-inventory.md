# Action/context parity inventory

Root: `/Users/tristan/Projects/skills/agent-use`

> Starter inventory only. Confirm important workflows manually and map human context to agent context/action/recovery.

## Candidate capability map

| Human capability | Evidence | Agent path candidate | Context needed | Safety/recovery | Status |
| --- | --- | --- | --- | --- | --- |
| UI action | `examples/action-parity-inventory.md:50` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `examples/action-parity-inventory.md:51` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `examples/action-parity-inventory.md:52` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/agent_use_audit.py:290` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/agent_use_audit.py:291` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/action_parity_inventory.py:16` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| UI action | `scripts/test_agent_use_scanners.py:26` | TBD API/CLI/tool | visible state, IDs, permissions | preview/audit if mutating | needs review |
| Agent/action surface | `examples/action-parity-inventory.md:55` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:56` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:57` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:185` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:288` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:306` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:312` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/test_agent_use_scanners.py:47` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/test_agent_use_scanners.py:48` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/test_agent_use_scanners.py:89` | api_route | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:60` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:61` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:62` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:63` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:64` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:65` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:66` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:67` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:68` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:69` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:70` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:71` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:72` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:73` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:74` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:75` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:76` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:77` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:78` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:79` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `examples/action-parity-inventory.md:80` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:5` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:324` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/web_agent_readiness.py:325` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:5` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:108` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:109` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:128` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/validate_skill.py:129` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |
| Agent/action surface | `scripts/agent_use_audit.py:9` | cli_command | docs/schema/auth | errors/retry/idempotency | candidate |

## Evidence by category

### ui_action
- `examples/action-parity-inventory.md:50` — - `scripts/agent_use_audit.py:257` — r"onClick\s*=", r"onSubmit\s*=", r"addEventListener\(['\"]click", r"<button\b", r"<Button\b",
- `examples/action-parity-inventory.md:51` — - `scripts/agent_use_audit.py:258` — r"onPressed\s*:", r"onTapGesture", r"TouchableOpacity", r"Pressable", r"button_to", r"form_with",
- `examples/action-parity-inventory.md:52` — - `scripts/action_parity_inventory.py:16` — "ui_action":[r"\bonClick\b",r"\bonSubmit\b",r"<button\b",r"Button\(",r"addEventListener\(['\"]click",r"onPressed\b",r"onTap\b"],
- `scripts/agent_use_audit.py:290` — r"onClick\s*=", r"onSubmit\s*=", r"addEventListener\(['\"]click", r"<button\b", r"<Button\b",
- `scripts/agent_use_audit.py:291` — r"onPressed\s*:", r"onTapGesture", r"TouchableOpacity", r"Pressable", r"button_to", r"form_with",
- `scripts/action_parity_inventory.py:16` — "ui_action":[r"\bonClick\b",r"\bonSubmit\b",r"<button\b",r"Button\(",r"addEventListener\(['\"]click",r"onPressed\b",r"onTap\b"],
- `scripts/test_agent_use_scanners.py:26` — write(root / "README.md", "This project talks about OpenAPI, OAuth, MCP, GraphQL, REST, onClick, and JSON output.\n")

### api_route
- `examples/action-parity-inventory.md:55` — - `scripts/web_agent_readiness.py:91` — def fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int) -> tuple[EndpointResult, str]:
- `examples/action-parity-inventory.md:56` — - `scripts/web_agent_readiness.py:178` — r,b=fetch(label, endpoint, accept, timeout, max_bytes); results.append(r)
- `examples/action-parity-inventory.md:57` — - `scripts/web_agent_readiness.py:191` — app=report.get("applicability",{}); lines.append(f"Profile: **{app.get('profile')}** ({app.get('profile_reason')})"); lines += ["","## Scor
- `scripts/web_agent_readiness.py:185` — def fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int) -> tuple[EndpointResult, str]:
- `scripts/web_agent_readiness.py:288` — r,b=fetch(label, endpoint, accept, timeout, max_bytes)
- `scripts/web_agent_readiness.py:306` — if app.get("needs_tool_metadata") and not any(("MCP" in r.label or "A2A" in r.label) and r.ok for r in results): recs.append("Tool/agent surfaces should publish an MCP server card 
- `scripts/web_agent_readiness.py:312` — app=report.get("applicability",{}); lines.append(f"Profile: **{app.get('profile')}** ({app.get('profile_reason')})"); lines += ["","## Scores"]
- `scripts/test_agent_use_scanners.py:47` — def make_fake_fetch(pages: dict[str, tuple[int, str | None, str | None, str]]):
- `scripts/test_agent_use_scanners.py:48` — def fake_fetch(label: str, url: str, accept: str | None, timeout: float, max_bytes: int):
- `scripts/test_agent_use_scanners.py:89` — web_agent_readiness.fetch = make_fake_fetch(pages) # type: ignore[assignment]

### cli_command
- `examples/action-parity-inventory.md:60` — - `scripts/agent_use_audit.py:9` — import argparse
- `examples/action-parity-inventory.md:61` — - `scripts/agent_use_audit.py:240` — r"argparse", r"click\.command", r"typer\.Typer", r"commander", r"yargs", r"oclif",
- `examples/action-parity-inventory.md:62` — - `scripts/agent_use_audit.py:241` — r"cobra\.Command", r"clap::Parser", r"picocli", r"console_scripts", r"\[project\.scripts\]",
- `examples/action-parity-inventory.md:63` — - `scripts/agent_use_audit.py:690` — def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
- `examples/action-parity-inventory.md:64` — - `scripts/agent_use_audit.py:691` — parser = argparse.ArgumentParser(description="Audit a repository/directory for agent-usefulness signals.")
- `examples/action-parity-inventory.md:65` — - `scripts/web_agent_readiness.py:5` — import argparse
- `examples/action-parity-inventory.md:66` — - `scripts/web_agent_readiness.py:202` — def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace:
- `examples/action-parity-inventory.md:67` — - `scripts/web_agent_readiness.py:203` — p=argparse.ArgumentParser(description="Check web/docs agent-readiness discovery endpoints.")
- `examples/action-parity-inventory.md:68` — - `scripts/generate_llms_txt.py:9` — import argparse
- `examples/action-parity-inventory.md:69` — - `scripts/generate_llms_txt.py:181` — def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
- `examples/action-parity-inventory.md:70` — - `scripts/generate_llms_txt.py:182` — parser = argparse.ArgumentParser(description="Generate a draft llms.txt from a docs directory.")
- `examples/action-parity-inventory.md:71` — - `scripts/validate_skill.py:5` — import argparse, json, py_compile, re, subprocess, sys
- `examples/action-parity-inventory.md:72` — - `scripts/validate_skill.py:108` — content=script.read_text(encoding="utf-8", errors="replace"); helpful="argparse" in content or "from validate_skill import main" in content or "
- `examples/action-parity-inventory.md:73` — - `scripts/validate_skill.py:109` — checks.append(Check(f"script-{script.name}","pass" if helpful else "warn","script uses argparse/help patterns or delegates to a validated CLI" i
- `examples/action-parity-inventory.md:74` — - `scripts/validate_skill.py:128` — def parse_args(argv: Optional[Sequence[str]]=None) -> argparse.Namespace:
- `examples/action-parity-inventory.md:75` — - `scripts/validate_skill.py:129` — p=argparse.ArgumentParser(description="Validate an Agent Skill package structure and common agent-use assets.")
- `examples/action-parity-inventory.md:76` — - `scripts/action_parity_inventory.py:8` — import argparse, csv, fnmatch, os, re, sys
- `examples/action-parity-inventory.md:77` — - `scripts/action_parity_inventory.py:18` — "cli_command":[r"argparse",r"click\.command",r"commander\(",r"cobra\.Command",r"yargs",r"clap::",r"process\.argv"],
- `examples/action-parity-inventory.md:78` — - `scripts/action_parity_inventory.py:66` — p=argparse.ArgumentParser(description="Inventory candidate UI actions and agent action paths.")
- `examples/action-parity-inventory.md:79` — - `scripts/generate_agent_assets.py:4` — import argparse, datetime as dt, re, sys
- `examples/action-parity-inventory.md:80` — - `scripts/generate_agent_assets.py:34` — p=argparse.ArgumentParser(description="Scaffold agent-use assets from templates.")
- `scripts/web_agent_readiness.py:5` — import argparse
- `scripts/web_agent_readiness.py:324` — def parse_args(argv: Sequence[str] | None=None) -> argparse.Namespace:
- `scripts/web_agent_readiness.py:325` — p=argparse.ArgumentParser(description="Check web/docs agent-readiness discovery endpoints.")
- `scripts/validate_skill.py:5` — import argparse, json, py_compile, re, subprocess, sys
- `scripts/validate_skill.py:108` — content=script.read_text(encoding="utf-8", errors="replace"); helpful="argparse" in content or "from validate_skill import main" in content or "from agent_use_audit import main" in
- `scripts/validate_skill.py:109` — checks.append(Check(f"script-{script.name}","pass" if helpful else "warn","script uses argparse/help patterns or delegates to a validated CLI" if helpful else "script may not expos
- `scripts/validate_skill.py:128` — def parse_args(argv: Optional[Sequence[str]]=None) -> argparse.Namespace:
- `scripts/validate_skill.py:129` — p=argparse.ArgumentParser(description="Validate an Agent Skill package structure and common agent-use assets.")
- `scripts/agent_use_audit.py:9` — import argparse

### tool_definition
- `SKILL.md:60` — MCP/A2A/tools: clear names/descriptions, typed schemas, examples, resource and prompt support, server/agent cards, consent model, safe defaults, high-signal responses, no hidden si
- `AGENTS.md:15` — - API/SDK/MCP/A2A/tools: `references/api-sdk-mcp-readiness.md`
- `references/audit-playbook.md:46` — MCP/tools:
- `examples/action-parity-inventory.md:83` — - `SKILL.md:54` — MCP/A2A/tools: clear names/descriptions, typed schemas, examples, resource and prompt support, server/agent cards, consent model, safe defaults, high-signal respo
- `examples/action-parity-inventory.md:84` — - `AGENTS.md:15` — - API/SDK/MCP/A2A/tools: `references/api-sdk-mcp-readiness.md`
- `examples/action-parity-inventory.md:85` — - `references/audit-playbook.md:46` — MCP/tools:
- `examples/action-parity-inventory.md:86` — - `scripts/agent_use_audit.py:262` — r"input_schema", r"server\.tool\(", r"\.tool\(", r"@tool", r"function_tool",
- `examples/action-parity-inventory.md:87` — - `scripts/agent_use_audit.py:263` — r"StructuredTool", r"Tool\(", r"tools\s*[:=]", r"tool_choice", r"function_call",
- `examples/action-parity-inventory.md:88` — - `scripts/action_parity_inventory.py:19` — "tool_definition":[r"\btool\s*\(",r"StructuredTool",r"function_call",r"tools\s*[:=]",r"McpServer",r"server\.tool",r"input_schema",r"inpu
- `examples/action-parity-inventory.md:89` — - `assets/schemas/tool-definition.schema.json:6` — "required": ["name", "description", "input_schema"],
- `examples/action-parity-inventory.md:90` — - `assets/schemas/tool-definition.schema.json:20` — "input_schema": {"type": "object"},
- `scripts/agent_use_audit.py:295` — r"input_schema", r"server\.tool\(", r"\.tool\(", r"@tool", r"function_tool",
- `scripts/agent_use_audit.py:296` — r"StructuredTool", r"Tool\(", r"tools\s*[:=]", r"tool_choice", r"function_call",
- `scripts/action_parity_inventory.py:19` — "tool_definition":[r"\btool\s*\(",r"StructuredTool",r"function_call",r"tools\s*[:=]",r"McpServer",r"server\.tool",r"input_schema",r"inputSchema"],
- `assets/schemas/tool-definition.schema.json:6` — "required": ["name", "description", "input_schema"],
- `assets/schemas/tool-definition.schema.json:20` — "input_schema": {"type": "object"},

### context_injection
- `CHANGELOG.md:15` — - Added deeper references synthesizing the original Compound ideas: action/context parity, noun test, primitives, shared workspace, dynamic context injection, prompt-native behavio
- `SKILL.md:43` — 4. Design context parity. Inject current resources, capabilities, constraints, user-visible state, recent activity, domain vocabulary, permissions, and completion criteria into the
- `SKILL.md:46` — 7. Make mutations safe. Add dry-run/preview, idempotency keys, scoped permissions, audit logs, confirmation for high-impact actions, sandbox/test mode, and undo/rollback where prac
- `SKILL.md:48` — 9. Ship evals. Compare baseline versus improved surfaces and cover discovery, happy paths, permissions, edge cases, recovery, and regression.
- `SKILL.md:62` — Apps/UIs: action parity, context parity, noun-test coverage, shared workspace, dynamic context injection, prompt-native features, UI reflection of agent mutations, durable links to
- `SKILL.md:84` — - `references/security-recovery.md` — permissions, approval, safety, rollback, privacy, abuse resistance.
- `references/audit-playbook.md:25` — - Safety and permissions: auth middleware, policy docs, RBAC, audit logs, destructive operations.
- `references/review-recipes.md:25` — - Safety/permissions/recovery.
- `references/build-playbook.md:98` — - User identity and permissions.
- `references/files-mobile-and-long-running-work.md:21` — Mobile agent surfaces must account for battery, network loss, OS background limits, permissions, storage sandboxes, and user-visible approval. Work should checkpoint before suspens
- `references/source-map.md:12` — - Dynamic context injection.
- `references/research-notes.md:15` — - **Dynamic context injection**: app-embedded agents should receive current object IDs, selection, permissions, and state.
- `references/app-ui-and-workspace-readiness.md:13` — Agents need access to current workspace, selected project, active filters, table data, chart underlying data, object IDs, permissions, limits, validation rules, recent activity, an
- `references/app-ui-and-workspace-readiness.md:27` — - Agent has stale or incomplete runtime context.
- `references/original-compound-comparison.md:5` — The deprecated Compound package was opinionated in a good way. It made a strong claim that agent support is not a bolt-on chatbot: the user and the agent should share action paths,
- `references/original-compound-comparison.md:13` — - **Dynamic context injection:** static prompts are not enough; runtime state and capabilities should be injected.
- `references/surface-guides.md:72` — - Current workspace, project, selected objects, active filters, permissions, limits, and validation rules are available outside the DOM.
- `references/surface-guides.md:81` — - Dynamic context injection: when an embedded agent is used, inject current object IDs, selection, permissions, and relevant state.
- `references/surface-guides.md:239` — - Are permissions and provenance visible?
- `references/framework.md:35` — - Explicit prerequisites, permissions, side effects, limits, and failure modes.
- `references/framework.md:90` — - Explicit state endpoints or files for visible UI state, selected records, configuration, permissions, validation rules, active filters, recent activity, and constraints.
- `references/framework.md:91` — - Dynamic context injection when an agent is operating inside an app.
- `references/framework.md:99` — - No way to list changed files/records, current selection, active workspace, or user permissions.
- `references/framework.md:138` — ### 8. Safety, permissions, and governance
- `references/framework.md:218` — - Permissions and ownership.
- `references/framework.md:227` — - Preserve filenames, MIME types, size, hashes, created/modified times, provenance, and permissions.
- `references/agent-native-architecture.md:8` — 2. **Context parity.** Agents need the same domain objects, state, permissions, constraints, recent activity, and completion criteria a competent human operator sees.
- `references/agent-native-architecture.md:11` — 5. **Dynamic context injection.** Static system prompts are not enough. Runtime context should tell the agent what resources exist, what it may do, what state is current, and what 
- `references/agent-native-architecture.md:46` — | Context starvation | Agent sees a static prompt but not current state | Inject workspace, permissions, objects, limits, recent activity |
- `references/agent-native-architecture.md:55` — 1. Find UI actions, route handlers, CLI commands, SDK methods, tool definitions, and system prompt/context construction.
