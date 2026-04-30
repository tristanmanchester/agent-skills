# Source notes

These source notes were used while creating v2 on 2026-04-30.

Official Meta URLs supplied by the user:

- https://developers.facebook.com/blog/post/2026/04/29/introducing-ads-cli/
- https://developers.facebook.com/documentation/ads-commerce/ads-ai-connectors/ads-cli/ads-cli-overview

The direct fetch of these pages can be rate-limited, so the skill is written to re-check the installed CLI with `meta ... --help` instead of relying on static command details.

Publicly visible source snippets and accessible summaries indicate:

- command grammar: `meta ads <resource> <action> [options]`;
- package: `meta-ads` on PyPI;
- Python 3.12+;
- auth status command: `meta auth status`;
- token example: `export ACCESS_TOKEN=<ACCESS_TOKEN>`;
- account flag example: `meta ads --ad-account-id <AD_ACCOUNT_ID> campaign list`;
- output formats: `table`, `json`, `plain`;
- automation flags such as `--no-input` and `--force`;
- exit codes including `0`, `3` for auth errors, and `4` for API errors;
- campaign/adset/creative/ad creation and update examples;
- Insights examples with `--date-preset` and `--fields`;
- catalog, product item, product set, dataset/pixel examples.

Because Ads CLI is new, any agent using this skill should prefer the local installed help text when there is a difference.
