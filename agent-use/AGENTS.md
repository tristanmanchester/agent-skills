# AGENTS.md

This package is an Agent Skill for auditing and designing systems so AI agents can use them reliably and safely.

## Canonical entry points

- Skill workflow: `SKILL.md`
- Framework: `references/framework.md`
- Scoring: `references/scoring-rubric.md`
- Audit process: `references/audit-playbook.md`
- Build process: `references/build-playbook.md`
- Original Compound synthesis: `references/agent-native-architecture.md`
- Web/docs: `references/web-and-docs-readiness.md`
- CLI/TUI: `references/cli-tui-readiness.md`
- API/SDK/MCP/A2A/tools: `references/api-sdk-mcp-readiness.md`
- App/workspace: `references/app-ui-and-workspace-readiness.md`
- Files/mobile/long-running work: `references/files-mobile-and-long-running-work.md`
- Security and recovery: `references/security-recovery.md`
- Evaluation: `references/evaluation.md`
- Source synthesis: `references/source-map.md`

## Safe commands

```bash
python scripts/validate_agent_assets.py --skill-dir . --run-help --py-compile --markdown
python scripts/audit_agent_use.py --root . --markdown --output examples/self-audit.md --json-output examples/self-audit.json
python scripts/action_parity_inventory.py . --output examples/action-parity-inventory.md --csv-output examples/action-parity-inventory.csv
python scripts/generate_llms_txt.py . --site-url https://example.com/agent-use --title agent-use --output examples/generated-llms.txt
```

The web probe performs network requests; only run it when the target URL is meant to be checked:

```bash
python scripts/web_agent_readiness.py https://example.com/docs --markdown --profile auto --output examples/web-agent-readiness.md
```

## Editing rules

- Keep `SKILL.md` concise and route detail into `references/`.
- Keep scripts non-interactive and safe by default.
- Preserve markdown references when moving files.
- Do not include secrets, credentials, private URLs, or user-specific data.
- Update templates and eval seeds when new audit dimensions are added.
- Run validation before packaging.

## Generated examples

Files in `examples/` are illustrative outputs from bundled scripts. Regenerate them after substantial script changes.
