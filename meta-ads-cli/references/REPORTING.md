# Reporting and Insights guide

## Reporting goals

Ads reporting should answer the business question, not just dump fields. Start with the smallest level/date range that answers the user's request.

## Common date ranges

Use `--date-preset` when possible:

```bash
meta ads insights get --date-preset yesterday
meta ads insights get --date-preset last_7d
meta ads insights get --date-preset last_30d
```

Use explicit date ranges only when requested or required by the user's business cadence. Verify the installed CLI's date-range syntax with:

```bash
meta ads insights get --help
```

## Field bundles

### Traffic snapshot

```text
spend,impressions,reach,clicks,inline_link_clicks,ctr,cpc,cpm
```

### Conversion snapshot

```text
spend,impressions,clicks,ctr,cpc,actions,action_values,purchase_roas,cost_per_action_type
```

### Campaign/adset/ad identification

Add level-specific IDs/names:

```text
campaign_id,campaign_name
adset_id,adset_name,campaign_id,campaign_name
ad_id,ad_name,adset_id,adset_name,campaign_id,campaign_name
```

## Suggested commands

Campaign-level weekly report:

```bash
python3 scripts/meta_ads_agent.py run -- \
  meta ads insights get \
  --level campaign \
  --date-preset last_7d \
  --fields campaign_id,campaign_name,spend,impressions,clicks,ctr,cpc,actions,action_values,purchase_roas
```

Ad-level creative diagnosis:

```bash
python3 scripts/meta_ads_agent.py run -- \
  meta ads insights get \
  --level ad \
  --date-preset last_7d \
  --fields ad_id,ad_name,adset_id,campaign_id,spend,impressions,clicks,ctr,cpc,actions,action_values,purchase_roas
```

Placement split:

```bash
python3 scripts/meta_ads_agent.py run -- \
  meta ads insights get \
  --level ad \
  --date-preset last_7d \
  --fields ad_id,ad_name,spend,impressions,clicks,ctr,cpc,actions,action_values,purchase_roas \
  --breakdowns publisher_platform,platform_position
```

Demographic split:

```bash
python3 scripts/meta_ads_agent.py run -- \
  meta ads insights get \
  --level adset \
  --date-preset last_30d \
  --fields adset_id,adset_name,spend,impressions,clicks,ctr,cpc,actions,action_values \
  --breakdowns age,gender
```

## Interpretation rules

- Do not call something “profitable” unless revenue/ROAS data is present and credible.
- Do not rank ads by CPA when conversion counts are tiny unless you say it is directional.
- Separate low CTR problems from poor conversion-rate problems.
- Check spend volume before recommending pause/scale.
- State attribution window assumptions when available.
- For ROAS, confirm whether `purchase_roas` or action values reflect the user's purchase event.
- If all conversions are zero, distinguish between no conversions and missing/failed tracking.

## Report shape

Use this structure for most user-facing reports:

```text
Period:
Scope:
Data pulled:

1. Executive summary
2. Top performers
3. Underperformers / risks
4. Diagnosis
5. Recommended actions
6. Caveats / data quality checks
```

For client-friendly reports, avoid jargon. Translate:

- CTR -> “how often people clicked after seeing the ad”;
- CPC -> “average cost per click”;
- ROAS -> “revenue returned per unit of spend”;
- CPA -> “cost per conversion/action”.

## Large reports

The official launch material emphasises pagination handling, but large reports can still be slow or verbose. For large date ranges, many breakdowns, or ad-level exports:

- keep fields tight;
- save output to a file;
- avoid dumping raw output into chat;
- summarise after parsing.

Example:

```bash
python3 scripts/meta_ads_agent.py run --output-file work/ad_level_last_30d.json -- \
  meta ads insights get --level ad --date-preset last_30d --fields ad_id,ad_name,spend,clicks,ctr,cpc,actions,action_values,purchase_roas
```
