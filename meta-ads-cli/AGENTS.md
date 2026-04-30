# Instructions for AI coding/terminal agents

You are operating Meta ads through Meta's official Ads CLI. Read `SKILL.md` before acting.

Use this execution pattern:

1. Run `python3 scripts/meta_ads_agent.py doctor` if CLI/auth/account access is uncertain.
2. Use `meta ads ... --help` to verify unfamiliar command syntax.
3. Run read-only commands through `python3 scripts/meta_ads_agent.py run -- ...`.
4. Before any write, create a plan with exact commands, object IDs, risks, and verification steps.
5. Do not write until the user gives specific approval.
6. Activation needs `--allow-active`; budget/bid changes need `--allow-budget`; delete/remove/force needs `--allow-destructive`.
7. Verify after every write.
8. Never print tokens, `.env`, cookies, app secrets, or auth config.

Prefer JSON output and concise business summaries. Do not invent IDs or results.
