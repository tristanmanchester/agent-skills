# Workflow playbook

Use these workflows rather than improvising command sequences.

## Account snapshot

Goal: understand account access, active objects, and recent performance without changing anything.

```bash
python3 scripts/meta_ads_agent.py doctor
python3 scripts/meta_ads_agent.py run -- meta ads adaccount list
python3 scripts/meta_ads_agent.py run -- meta ads campaign list --limit 50
python3 scripts/meta_ads_agent.py run -- meta ads insights get --date-preset last_7d --fields spend,impressions,clicks,ctr,cpc
```

Report:

- account(s) found;
- currency/timezone if available;
- active/paused campaign counts;
- spend and traffic trend;
- obvious anomalies.

## Weekly performance report

Goal: produce a client-friendly weekly report.

1. Confirm ad account.
2. Pull campaign-level Insights for `last_7d`.
3. Pull ad/adset level only when needed.
4. Separate factual findings from recommendations.

```bash
python3 scripts/meta_ads_agent.py run -- \
  meta ads insights get \
    --date-preset last_7d \
    --fields campaign_id,campaign_name,spend,impressions,clicks,ctr,cpc,actions,action_values,purchase_roas
```

If `purchase_roas`, `actions`, or `action_values` are unavailable, state that conversion tracking or field support may need checking.

## Performance triage

Goal: decide what to scale, pause, or investigate.

1. Campaign-level spend and ROAS/CPA.
2. Ad set-level breakdown for campaigns with meaningful spend.
3. Ad-level breakdown for creative diagnosis.
4. Recommend actions; do not mutate until approved.

```bash
python3 scripts/meta_ads_agent.py run -- meta ads insights get --level campaign --date-preset last_7d --fields campaign_id,campaign_name,spend,actions,action_values,purchase_roas
python3 scripts/meta_ads_agent.py run -- meta ads insights get --level adset --date-preset last_7d --fields adset_id,adset_name,campaign_id,spend,clicks,ctr,cpc,actions,action_values,purchase_roas
python3 scripts/meta_ads_agent.py run -- meta ads insights get --level ad --date-preset last_7d --fields ad_id,ad_name,adset_id,spend,clicks,ctr,cpc,actions,action_values,purchase_roas
```

Use thresholds only if the user provides them or the account has enough data. Otherwise call recommendations “candidates”.

## Safe pause

Goal: pause an underperforming object.

1. Read the object.
2. Read recent performance.
3. Explain the basis for pausing.
4. Get explicit approval.
5. Update status to `PAUSED`.
6. Verify.

```bash
python3 scripts/meta_ads_agent.py run -- meta ads ad get AD_ID
python3 scripts/meta_ads_agent.py run -- meta ads insights get --ad_id AD_ID --date-preset last_7d --fields spend,clicks,ctr,cpc,actions,action_values,purchase_roas
python3 scripts/meta_ads_agent.py run --approved "User approved pausing ad AD_ID" -- meta ads ad update AD_ID --status PAUSED
python3 scripts/meta_ads_agent.py run -- meta ads ad get AD_ID
```

If `ad get` is not supported in the installed CLI, run `meta ads ad --help` and use the equivalent read/list filter.

## Budget change

Goal: change spend safely.

1. Read account currency/timezone.
2. Read current object budget.
3. Convert/confirm human amount to CLI units.
4. Build command plan with before/after.
5. Get explicit approval.
6. Run with `--allow-budget`.
7. Verify.

```bash
python3 scripts/meta_ads_agent.py run -- meta ads adaccount list
python3 scripts/meta_ads_agent.py run -- meta ads adset get ADSET_ID
python3 scripts/meta_ads_agent.py run \
  --approved "User approved changing ad set ADSET_ID daily budget from 5000 to 7500 minor units" \
  --allow-budget \
  -- meta ads adset update ADSET_ID --daily-budget 7500
python3 scripts/meta_ads_agent.py run -- meta ads adset get ADSET_ID
```

## Paused launch

Goal: create a new campaign/ad set/creative/ad without accidental live spend.

1. Confirm account, page ID, dataset/pixel, catalog if relevant, destination URL, objective, budget, schedule, market, creative assets.
2. Run `--help` for each resource if command options are unfamiliar.
3. Create campaign. Capture ID.
4. Create ad set. Capture ID.
5. Create creative. Capture ID.
6. Create ad. Capture ID.
7. Read back all objects.
8. Leave paused unless activation is separately approved.

Example sequence:

```bash
python3 scripts/meta_ads_agent.py run --approved "User approved creating paused campaign Summer Sale" --allow-budget -- \
  meta ads campaign create --name "Summer Sale" --objective OUTCOME_SALES --daily-budget 5000

python3 scripts/meta_ads_agent.py run --approved "User approved creating paused ad set for Summer Sale" --allow-budget -- \
  meta ads adset create CAMPAIGN_ID --name "Broad US" --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS --targeting-countries US

python3 scripts/meta_ads_agent.py run --approved "User approved creating creative for Summer Sale" -- \
  meta ads creative create --name "Hero Banner" --page-id PAGE_ID --image ./banner.jpg --body "Copy" --title "Headline" --link-url https://example.com --call-to-action SHOP_NOW

python3 scripts/meta_ads_agent.py run --approved "User approved creating paused ad for Summer Sale" -- \
  meta ads ad create ADSET_ID --name "Hero Banner Ad" --creative-id CREATIVE_ID
```

## Creative test rollout

Goal: add creative variants without changing budget or activating unexpectedly.

1. Read existing ad set and campaign.
2. Confirm test naming convention.
3. Create creatives from local files or existing assets.
4. Create paused ads or confirm status behaviour.
5. Verify creative-to-ad mapping.
6. Summarise variant IDs and copy.

Use clear variant names:

```text
<campaign> | <angle> | <format> | <YYYY-MM-DD>
```

## Catalogs and products

Goal: manage commerce catalog objects.

Known patterns:

```bash
meta ads catalog create --name "My Catalog"
meta ads product-item create --catalog-id CATALOG_ID --retailer-id sku_a --name "Blue Shirt" --url https://example.com/blue-shirt --price "999" --currency USD --image-url https://example.com/blue-shirt.jpg
meta ads product-set list --catalog-id CATALOG_ID
```

Safety notes:

- product feed changes can affect dynamic ads;
- verify retailer IDs and currency;
- avoid duplicate SKU creation unless intended;
- read existing catalog/product set state first.

## Dataset/pixel audit

Goal: check conversion tracking setup without making changes.

1. List or identify datasets/pixels through CLI support.
2. Check account/catalog connections if available.
3. Pull recent conversion-related Insights.
4. Report status: green/yellow/red.

Known patterns:

```bash
meta ads dataset create --name "Website Pixel"
meta ads dataset connect DATASET_ID --ad-account-id AD_ACCOUNT_ID --catalog-id CATALOG_ID
```

Do not run `dataset create` or `dataset connect` during an audit unless the user explicitly asks to create/connect tracking and approves it.

## Activation

Goal: turn paused structure live only after review.

Checklist before activation:

- correct ad account;
- billing/payment status known;
- campaign objective;
- budget/bid/schedule;
- audience and special category constraints;
- creative copy/media;
- destination URL and UTM parameters;
- page/Instagram actor;
- dataset/pixel and conversion event;
- catalog/product set if commerce;
- all IDs read back.

Command pattern:

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "User approved activating campaign CAMPAIGN_ID after reviewing budget, targeting, creative, URL, and tracking" \
  --allow-active \
  -- meta ads campaign update CAMPAIGN_ID --status ACTIVE
```

Activate campaign, ad set, and ads only as needed. Verify effective status after each step.
