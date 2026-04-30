# Troubleshooting

## Missing CLI

Symptoms:

- `meta: command not found`
- guard `doctor` reports no `meta` executable

Fix:

```bash
python3.12 -m pip install meta-ads
meta --help
```

Confirm Python 3.12+ for the official CLI.

## Auth errors

Public launch material lists exit code `3` for authentication errors.

Use:

```bash
meta auth status
```

Do not print tokens. Do not ask the user to paste secrets into chat unless there is no other safe channel.

Common causes:

- `ACCESS_TOKEN` not exported or expired;
- token lacks required permissions;
- token user/system user lacks access to the ad account/page/catalog/dataset;
- app/business assets not assigned correctly;
- wrong ad account ID.

## API errors

Public launch material lists exit code `4` for API errors.

Stop and inspect:

- object ID and resource type;
- account ID;
- permissions;
- required fields;
- special ad category requirements;
- budget unit/currency;
- page/dataset/catalog ownership;
- asset file validity;
- whether the installed CLI flag name differs from this skill.

## Non-JSON output

If the guard cannot parse JSON:

1. re-run with `meta --output json ads ...`;
2. verify output flag placement with `meta --help`;
3. if JSON is not available for that command, parse conservatively and report uncertainty.

## Interactive prompts

Agents should avoid hanging on prompts. If the CLI supports `--no-input`, use it after verifying help text. If a command asks for confirmation, stop and convert the action into an explicit plan for the user.

## Rate limits or transient errors

If the CLI reports rate limiting or transient API errors:

- reduce page size/scope;
- avoid broad `--fetch all` style requests unless needed;
- wait before retrying;
- do not repeat writes blindly;
- for reporting, use smaller date ranges or fewer breakdowns.

## Partial plan failure

For multi-step plans:

1. Stop at the first failed write.
2. Record completed step IDs and returned object IDs.
3. Verify any objects already created.
4. Tell the user what exists and what did not run.
5. Do not “repair” by creating duplicate objects unless explicitly approved.

## When the CLI does not cover the task

1. Run `meta ads --help` and resource-specific help to confirm coverage.
2. Search official Meta docs if available.
3. Explain the limitation to the user.
4. Offer a lower-level Marketing API workaround only if the user accepts it.
5. Use a separate dry-run/approval/verification model for any raw API call.

V2 intentionally does not ship a full raw Graph API client. The official CLI is canonical, and raw API work should be explicit, rare, and carefully reviewed.
