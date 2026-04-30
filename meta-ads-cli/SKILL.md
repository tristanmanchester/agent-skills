---
name: meta-ads-cli
version: 2.0.0
description: Use this skill when an AI agent needs to manage, audit, report on, create, pause, update, or troubleshoot Meta/Facebook/Instagram ads through Meta's official Ads CLI (`meta ads ...`). It is designed for any shell-capable agent, not just OpenClaw. It focuses on safe command planning, JSON output, confirmation gates, read-before-write behaviour, paused-by-default launches, reporting workflows, datasets/pixels, catalog/product operations, and failure handling.
license: MIT. See LICENSE.txt
compatibility: Requires a shell, Python 3.9+ for the optional guard script, and Meta's official Ads CLI (`pip install meta-ads`, Python 3.12+ per Meta docs). Works with OpenClaw, Claude Code, Codex CLI, Cursor, Aider, Goose, Crew/Autogen agents, and CI runners that can execute terminal commands.
metadata: {"author":"OpenAI","skill_type":"agent-agnostic-shell-skill","primary_cli":"meta ads","wrapped_cli":"scripts/meta_ads_agent.py","risk_model":"read-plan-approve-write-verify","created":"2026-04-30"}
---

# Meta Ads CLI Agent Skill

This skill teaches an AI agent to operate Meta ads through Meta's official **Ads CLI** instead of reimplementing the Marketing API.

The core command shape is:

```bash
meta ads <resource> <action> [options]
```

Examples from the official Ads CLI pattern include:

```bash
meta ads campaign list
meta ads campaign create --name "Summer Sale" --objective OUTCOME_SALES --daily-budget 5000
meta ads adset create CAMPAIGN_ID --name "My Ad Set" --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS --targeting-countries US
meta ads creative create --name "Hero Banner" --page-id 111222333 --image ./banner.jpg --body "50% off" --title "Shop Now" --link-url https://example.com/sale --call-to-action SHOP_NOW
meta ads ad create ADSET_ID --name "Hero Banner Ad" --creative-id CREATIVE_ID
meta ads insights get --campaign_id CAMPAIGN_ID --fields impressions,conversions,spend --date-preset last_7d
```

Use the bundled guard script as the default execution path:

```bash
python3 scripts/meta_ads_agent.py doctor
python3 scripts/meta_ads_agent.py classify -- meta ads campaign list
python3 scripts/meta_ads_agent.py run -- meta ads campaign list --limit 25
```

The guard script does **not** replace Meta's CLI. It wraps it so agents behave safely and consistently.

## Highest-priority rules

1. **Use Meta's official CLI first.** Do not call Graph API directly unless the official CLI cannot do the task and the user explicitly accepts a lower-level workaround.
2. **Read before write.** Inspect the relevant account/object/performance state before changing it.
3. **No spend-affecting change without explicit user approval.** Writes, budget changes, activation, delete/remove, dataset/catalog connections, and creative uploads need approval.
4. **Never activate by accident.** New objects should remain `PAUSED` unless the user explicitly asks to activate. `ACTIVE`, `activate`, `delete`, `remove`, and `--force` are high-risk.
5. **Prefer machine-readable output.** Use JSON whenever possible: `meta --output json ads ...`. Use table output only for human presentation.
6. **One write step at a time.** Apply one mutation, verify it, then continue.
7. **Do not invent IDs.** Resolve account, campaign, ad set, creative, page, pixel/dataset, catalog, product set, and targeting IDs from the CLI or user-provided values.
8. **Keep tokens out of chat and logs.** Never print access tokens, app secrets, cookies, or `.env` contents.
9. **Ask for missing material only when blocking.** For reads, proceed with defaults. For writes, collect exact account, IDs, budget, date range, page/dataset/catalog, destination URL, and approval.
10. **Treat regulated/special categories carefully.** Housing, employment, credit, politics, social issues, health, financial services, minors, and sensitive audiences require extra review and conservative targeting.

## Recommended agent flow

For almost every request, follow this order:

```text
1. Classify request: read-only, ordinary write, budget/write, activation, destructive, regulated.
2. Run doctor/auth check if account access is uncertain.
3. Read current state with compact JSON output.
4. Produce a short plan with exact commands, risks, assumptions, and verification commands.
5. For read-only tasks: run commands and summarise.
6. For writes: wait for explicit approval, then run through scripts/meta_ads_agent.py.
7. Verify state after every write.
8. Report what changed, object IDs, before/after values, and any unresolved issues.
```

## Install and auth checklist

```bash
# Meta docs list meta-ads as the package name.
python3.12 -m pip install meta-ads

# Confirm the CLI is available.
meta --help
meta ads --help

# Auth status. Meta docs show ACCESS_TOKEN for token-based auth.
export ACCESS_TOKEN=<ACCESS_TOKEN>
meta auth status

# Prefer an explicit ad account for every command until a default is proven.
meta ads --ad-account-id <AD_ACCOUNT_ID> campaign list
```

Do not guess config keys if auth fails. Run:

```bash
meta auth status
meta ads --help
meta ads <resource> --help
```

Then follow the official CLI setup/configuration docs for the installed version.

## Using the guard script

### Check readiness

```bash
python3 scripts/meta_ads_agent.py doctor
```

### Classify command risk without executing

```bash
python3 scripts/meta_ads_agent.py classify -- meta ads campaign update 123 --status ACTIVE
```

### Run a read-only command

```bash
python3 scripts/meta_ads_agent.py run -- meta ads campaign list --limit 25
```

### Run a write after approval

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "User approved creating the paused campaign named Summer Sale in account act_123" \
  -- meta ads campaign create --name "Summer Sale" --objective OUTCOME_SALES --daily-budget 5000
```

### Run an activation after stronger approval

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "User approved activating campaign 123 after reviewing it" \
  --allow-active \
  -- meta ads campaign update 123 --status ACTIVE
```

### Lint or run a multi-step plan

```bash
python3 scripts/meta_ads_agent.py lint-plan templates/weekly-report-plan.json
python3 scripts/meta_ads_agent.py run-plan templates/weekly-report-plan.json
```

Write-heavy plans require `--approved ...`; activation/destructive plans require additional flags.

## Fast task routing

| User intent | First action | Main workflow |
|---|---|---|
| “Show performance” | Read-only | `references/REPORTING.md` |
| “What should I pause?” | Read insights, then propose | `references/WORKFLOWS.md#performance-triage` |
| “Pause this ad/campaign” | Read object + metrics | `references/WORKFLOWS.md#safe-pause` |
| “Increase budget” | Read currency, current budget, delivery | `references/WORKFLOWS.md#budget-change` |
| “Launch campaign” | Build paused launch plan | `references/WORKFLOWS.md#paused-launch` |
| “Create catalogue/product set” | Check account/catalog context | `references/WORKFLOWS.md#catalogs-and-products` |
| “Check pixel” | Dataset and insights audit | `references/WORKFLOWS.md#datasetpixel-audit` |
| “Use another endpoint” | Verify official CLI coverage first | `references/TROUBLESHOOTING.md#when-the-cli-does-not-cover-the-task` |

## Output expectations

For read-only analysis, return:

```text
- what was queried
- date range and attribution assumptions
- top findings with numbers
- caveats about missing/zero/odd metrics
- recommended next actions separated from actual changes
```

For writes, return:

```text
- object IDs touched
- before/after values
- command(s) run, redacted where needed
- verification result
- anything still paused/not live
- any follow-up the user must perform in Ads Manager
```

## References in this skill

- `references/CRITICAL-ANALYSIS-v1.md` — what v1 got right/wrong and why v2 changed direction.
- `references/OFFICIAL-ADS-CLI.md` — concise Ads CLI reference for agents.
- `references/AGENT-OPERATING-MODEL.md` — how agents should reason, plan, execute, and recover.
- `references/SAFETY.md` — approval gates, budget/activation/destructive rules.
- `references/WORKFLOWS.md` — account audits, reporting, launch, pause, budget, dataset/catalog workflows.
- `references/REPORTING.md` — Insights fields, date ranges, breakdowns, and interpretation.
- `references/COMMANDS.md` — command patterns and help-discovery strategy.
- `references/OPTIMISATION-DECISIONING.md` — how to turn metrics into cautious recommendations.
- `resources/command-catalog.json` and `resources/risk-rules.json` — machine-readable aids for agents.
- `agent-prompts/` and `AGENTS.md` — ready-made prompts/instructions for general shell agents.
- `references/TROUBLESHOOTING.md` — auth, exit codes, output parsing, rate limits, API errors.
- `references/PORTABILITY.md` — using this skill in non-OpenClaw agents.
- `templates/` — JSON plan templates and schema.
- `scripts/meta_ads_agent.py` — optional safe command runner.
- `evals/` — behavioural evals for agent skill quality.
