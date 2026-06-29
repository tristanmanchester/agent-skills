# agent-use skill v2

A comprehensive Agent Skill for auditing and designing systems that AI agents can use well.

Use it for repositories, websites, documentation sets, CLIs, TUIs, APIs, SDKs, MCP/A2A/tool servers, Agent Skills, app UIs, files/workspaces, mobile/offline flows, and other automation surfaces.

## Install/use

Zip the `agent-use/` directory or install it wherever your Agent Skills runtime expects skills. The main entry point is `SKILL.md`. Detailed playbooks are in `references/`; reusable helpers are in `scripts/`; templates and schemas are in `assets/`; eval seeds are in `evals/`.

## Quick commands

```bash
python scripts/audit_agent_use.py --root /path/to/repo --markdown --output agent-use-report.md --json-output agent-use-report.json
python scripts/action_parity_inventory.py /path/to/repo --output action-parity-inventory.md --csv-output capability-map.csv
python scripts/web_agent_readiness.py https://example.com/docs --markdown --profile auto --output web-agent-readiness.md
python scripts/generate_llms_txt.py ./docs --site-url https://example.com/docs --output llms.txt
python scripts/generate_agent_assets.py --root ./project --project-name "Example" --surface all --dry-run
python scripts/validate_agent_assets.py --skill-dir ./agent-use --run-help --py-compile --markdown
```

V1-compatible entry points remain available: `scripts/agent_use_audit.py` and `scripts/validate_skill.py`.

## What it produces

A good audit includes an overall agent-use score, applicability notes, dimension-by-dimension evidence, an action/context parity map, safety and recovery findings, a concrete remediation plan, and evals/acceptance criteria.

## Design philosophy

Agent-usefulness comes from reducing ambiguity: agents need to discover the right surface, read compact current context, execute typed primitive actions, parse bounded outputs, verify final state, and recover safely when something fails.
