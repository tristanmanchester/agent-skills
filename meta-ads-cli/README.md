# Meta Ads CLI Agent Skill v2

A general-purpose skill for AI agents that manage Meta/Facebook/Instagram ads via Meta's official Ads CLI.

V2 is deliberately different from v1:

- v1 implemented a custom Marketing API wrapper.
- v2 assumes Meta's official `meta ads ...` CLI should handle auth, pagination, object operations, output formats, and API edge cases.
- v2 adds what agents still need: safety gates, command planning, JSON-first execution, verification workflows, evals, and cross-agent instructions.

## Quick start

```bash
python3.12 -m pip install meta-ads
meta auth status
python3 scripts/meta_ads_agent.py doctor
python3 scripts/meta_ads_agent.py run -- meta ads campaign list --limit 25
```

## Directory layout

```text
SKILL.md                         Primary skill instructions
scripts/meta_ads_agent.py         Safety wrapper around Meta Ads CLI
references/                       Agent playbooks and deep references
templates/                        Machine-readable plan templates and schema
evals/                            Behavioural tests and rubric
```

## Safe execution pattern

Read-only commands can be run directly through the guard:

```bash
python3 scripts/meta_ads_agent.py run -- meta ads insights get --date-preset last_7d --fields spend,impressions,clicks,ctr
```

Writes require approval:

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "User approved pausing ad 120000000000000" \
  -- meta ads ad update 120000000000000 --status PAUSED
```

Activation requires an extra flag:

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "User approved activating campaign 120000000000000" \
  --allow-active \
  -- meta ads campaign update 120000000000000 --status ACTIVE
```
