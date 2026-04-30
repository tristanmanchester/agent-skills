# Scripts

## `meta_ads_agent.py`

A small safety wrapper around Meta's official Ads CLI.

It can:

- check whether `meta` is installed and auth appears configured;
- classify command risk;
- force JSON-first command execution where possible;
- block writes unless an approval string is supplied;
- require stronger flags for activation, budget, and destructive changes;
- lint and run JSON command plans;
- log redacted execution metadata.

It cannot guarantee Meta-side success or policy compliance. It is a guardrail for agent behaviour, not a substitute for advertiser review.

Examples:

```bash
python3 scripts/meta_ads_agent.py doctor
python3 scripts/meta_ads_agent.py classify -- meta ads campaign update 123 --status ACTIVE
python3 scripts/meta_ads_agent.py run -- meta ads campaign list --limit 25
python3 scripts/meta_ads_agent.py run --approved "User approved pausing ad 123" -- meta ads ad update 123 --status PAUSED
python3 scripts/meta_ads_agent.py lint-plan templates/weekly-report-plan.json
python3 scripts/meta_ads_agent.py run-plan templates/weekly-report-plan.json
```
