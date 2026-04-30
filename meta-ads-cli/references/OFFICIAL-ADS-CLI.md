# Official Ads CLI reference for agents

## What the CLI is for

Meta's Ads CLI is a command-line interface for Meta Ads and Commerce operations. It is aimed at developers and AI agents that need to manage campaigns without writing Marketing API boilerplate.

The CLI handles common mechanics that v1 attempted to implement manually:

- authentication/configuration;
- pagination;
- output formatting;
- error handling;
- create/list/update/delete operations for ads objects;
- Insights/reporting;
- catalog and product operations;
- datasets/pixels and conversion tracking links.

## Basic grammar

```bash
meta ads <resource> <action> [options]
```

Common resource/action examples:

```bash
meta ads campaign list
meta ads campaign create --name "Summer Sale" --objective OUTCOME_SALES --daily-budget 5000
meta ads campaign update CAMPAIGN_ID --status ACTIVE

meta ads adset create CAMPAIGN_ID --name "My Ad Set" \
  --optimization-goal LINK_CLICKS \
  --billing-event IMPRESSIONS \
  --bid-amount 500 \
  --targeting-countries US

meta ads creative create --name "Hero Banner" \
  --page-id 111222333 \
  --image ./banner.jpg \
  --body "50% off everything!" \
  --title "Shop Now" \
  --link-url https://example.com/sale \
  --call-to-action SHOP_NOW

meta ads ad create ADSET_ID --name "Hero Banner Ad" --creative-id CREATIVE_ID

meta ads insights get --campaign_id CAMPAIGN_ID \
  --fields impressions,conversions,spend \
  --date-preset last_7d
```

## Installation and auth

Meta's setup docs list the package as `meta-ads` and require Python 3.12+.

```bash
python3.12 -m pip install meta-ads
meta --help
meta auth status
```

The docs show token-based auth using:

```bash
export ACCESS_TOKEN=<ACCESS_TOKEN>
meta auth status
```

Use the CLI's installed docs for exact current config keys:

```bash
meta auth --help
meta ads --help
meta ads --ad-account-id <AD_ACCOUNT_ID> campaign list
```

## Output formats

Prefer JSON for agents:

```bash
meta --output json ads campaign list
```

Known output formats include:

- `table` — human-readable default;
- `json` — machine-readable;
- `plain` — tab-separated/plain output for shell tools.

The guard script inserts `--output json` into many `meta ads ...` commands when no output format is already present. If the installed CLI rejects the placement, run `meta --help` and update the command for that version.

## Automation flags and exit codes

Public launch material describes automation-friendly flags such as `--no-input` and `--force`, plus standard exit codes including:

- `0`: success;
- `3`: authentication errors;
- `4`: API errors.

Do not spam retries on exit code `3`. Fix auth first. For API errors, parse the returned error if available, reduce scope, verify IDs/permissions, and retry only when the error is transient.

## Default paused behaviour

Launch material says campaigns are created in `PAUSED` state by default to reduce accidental live spend. Agents must still be conservative:

- explicitly set or verify `PAUSED` when creating spend-capable objects;
- never assume an ad set/ad is paused unless read back;
- never run activation commands without explicit approval.

## Help-discovery strategy

Ads CLI is new and likely to change. Agents should not rely solely on this file. Before using a resource/action combination for the first time in a session, run:

```bash
meta ads <resource> --help
meta ads <resource> <action> --help
```

If a flag differs from this skill, prefer the installed CLI's help text.
