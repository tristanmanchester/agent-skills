# Changelog

## 2.0.0 — 2026-06-29

- Added web discovery following from `Link` headers and RFC 9727 Linkset JSON so linked OpenAPI/OAuth/API catalog surfaces count even across origins.
- Added docs/API/tool web profiles and stopped recommending MCP/A2A cards unless the scanned surface is actually a tool/agent surface.
- Added evidence provenance and confidence to local repo audits so scanner internals, templates, generated reports, and reference prose no longer count as implementation evidence.
- Added scanner regression tests for linked web discovery, docs/API profile inference, and keyword-only repo false positives.
- Fixed stale script references and restored working v2 command names plus v1 compatibility entry points.
- Fixed validation from the current directory by resolving the skill directory before comparing the frontmatter name.
- Added Python compilation and script `--help` validation, JSON resource validation, trigger-query checks, and output-directory creation.
- Fixed generated-report recursion so self-audits, validation reports, and generated `llms.txt` drafts are skipped by default by the local audit scanner.
- Fixed hidden-directory scanning so `.well-known` and `.github` are not accidentally missed.
- Fixed the API catalog template to use RFC-style Linkset JSON rather than an ad-hoc list.
- Added `/.well-known/mcp.json` as the primary MCP discovery path while keeping the legacy alternate check.
- Added profile-aware web scoring so content-only sites are not penalized for API/app-only capability endpoints.
- Added action parity inventory tooling with Markdown and CSV outputs.
- Added agent-asset scaffolding for AGENTS.md, llms.txt, web discovery headers, capability maps, API/CLI contracts, permission matrices, API catalog, MCP card, A2A card, skills index, and eval seeds.
- Added deeper references synthesizing the original Compound ideas: action/context parity, noun test, primitives, shared workspace, dynamic context injection, prompt-native behavior, self-modification guardrails, mobile/offline constraints, and product feedback loops.
- Expanded guidance across websites/docs, CLIs/TUIs, APIs, SDKs, MCP/A2A/tools, app UIs, files/workspaces, security, evals, and Agent Skill packaging.
