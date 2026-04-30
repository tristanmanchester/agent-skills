# Command patterns and discovery

This file is intentionally compact. Ads CLI is new; installed help text is the source of truth.

## Universal command discovery

```bash
meta --help
meta ads --help
meta ads campaign --help
meta ads campaign create --help
meta ads insights get --help
```

If a command in this skill fails because an option moved or changed, run the relevant `--help`, update the command, and continue safely.

## JSON output

Prefer:

```bash
meta --output json ads campaign list
```

If global output placement differs in your installed version, use whatever `meta --help` documents.

## Account scoping

Prefer explicit account flags until defaults are known:

```bash
meta ads --ad-account-id act_123 campaign list
```

Do not assume a default account when a user has multiple ad accounts.

## Campaigns

```bash
meta ads campaign list --limit 25
meta ads campaign create --name "Name" --objective OUTCOME_SALES --daily-budget 5000
meta ads campaign update CAMPAIGN_ID --status PAUSED
meta ads campaign update CAMPAIGN_ID --status ACTIVE
```

Activation is high-risk and requires `--allow-active` in the guard.

## Ad sets

```bash
meta ads adset create CAMPAIGN_ID --name "Ad Set" --optimization-goal LINK_CLICKS --billing-event IMPRESSIONS --bid-amount 500 --targeting-countries US
meta ads adset update ADSET_ID --status PAUSED
```

For nested or advanced targeting, use installed CLI help. If the CLI does not support the needed targeting shape, do not invent a flag.

## Creatives

```bash
meta ads creative create --name "Creative" --page-id PAGE_ID --image ./image.jpg --body "Primary text" --title "Headline" --link-url https://example.com --call-to-action SHOP_NOW
```

Check local asset existence before running creative creation.

## Ads

```bash
meta ads ad create ADSET_ID --name "Ad" --creative-id CREATIVE_ID
meta ads ad update AD_ID --status PAUSED
```

## Insights

```bash
meta ads insights get --date-preset last_7d --fields spend,impressions,clicks,ctr,cpc
meta ads insights get --campaign_id CAMPAIGN_ID --date-preset last_7d --fields impressions,conversions,spend
```

Use `--level` and `--breakdowns` if supported and needed.

## Catalogs/products

```bash
meta ads catalog create --name "My Catalog"
meta ads product-item create --catalog-id CATALOG_ID --retailer-id sku_a --name "Blue Shirt" --url https://example.com/blue-shirt --price "999" --currency USD --image-url https://example.com/blue-shirt.jpg
meta ads product-set list --catalog-id CATALOG_ID
```

## Datasets/pixels

```bash
meta ads dataset create --name "Website Pixel"
meta ads dataset connect DATASET_ID --ad-account-id AD_ACCOUNT_ID --catalog-id CATALOG_ID
```

`dataset connect` is a tracking-affecting write. Require approval.

## Commands agents should avoid

Avoid unless explicitly necessary and approved:

```bash
meta ads campaign delete ...
meta ads campaign update ... --status ACTIVE
meta ads adset update ... --status ACTIVE
meta ads ad update ... --status ACTIVE
meta ads ... --force
```

Avoid commands that reveal secrets:

```bash
cat .env
printenv
```
