# Safety, approval, and policy rules

Meta ads operations can spend money, change tracking, affect customer data, and create compliance risk. This skill uses a conservative safety model.

## Absolute rules

1. No activation without explicit approval.
2. No budget or bid change without showing before/after values.
3. No delete/remove/force unless the user explicitly requested destructive cleanup.
4. No targeting IDs guessed from names.
5. No secrets in chat, logs, screenshots, or plan files.
6. No regulated category shortcuts.
7. Stop after failed writes; do not continue a multi-step plan unless the failure is understood.

## What counts as a write

Treat these actions as writes:

- `create`
- `update`
- `delete`
- `remove`
- `connect`
- `disconnect`
- `upload`
- `pause`
- `activate`
- `archive`
- any command using `--force`
- any command setting `status`, budgets, bids, targeting, URLs, creative copy, datasets, catalogs, product feeds, conversion settings, or tracking associations

## High-risk writes

High-risk commands require both user approval and an extra guard flag.

| High-risk type | Signals | Guard flag |
|---|---|---|
| Activation | `activate`, `--status ACTIVE`, `status=ACTIVE` | `--allow-active` |
| Budget/bid | `--daily-budget`, `--lifetime-budget`, `--bid-amount`, `--spend-cap`, `budget`, `bid` | `--allow-budget` |
| Destructive | `delete`, `remove`, `--force` | `--allow-destructive` |

## Safe launch defaults

For new campaign structures:

- create campaign first;
- create ad set second;
- create creative third;
- create ad fourth;
- keep all delivery-capable objects paused;
- verify each returned ID;
- only activate after user reviews structure, budget, targeting, creative, destination URL, tracking, and billing/account.

## Budget unit caution

Meta APIs and CLIs often express budgets in minor currency units. For many currencies, `5000` means 50.00 in the account currency. Always verify:

- account currency;
- CLI help for the budget flag;
- current budget values from the object;
- intended human amount.

Report both forms when possible:

```text
Daily budget: 5000 minor units (= 50.00 EUR if 100 minor units per EUR)
```

Do not assume every currency has 100 minor units. Use the account's currency and Meta's current behaviour.

## Regulated/special categories

Escalate for human review when a request involves:

- housing;
- employment;
- credit;
- elections, politics, social issues;
- health or medical conditions;
- minors;
- financial hardship;
- sensitive personal attributes;
- retargeting based on sensitive behaviour;
- location, demographic, or lookalike targeting that may be restricted.

For these, the agent should:

1. identify the category;
2. avoid narrow targeting suggestions;
3. check the account/campaign requirements in the installed CLI and official docs;
4. ask for confirmation from a human advertiser/compliance owner before creation or changes.

## Token hygiene

Do not run commands that reveal secrets, such as:

```bash
cat .env
printenv
meta auth token
```

If diagnosing auth, use:

```bash
meta auth status
python3 scripts/meta_ads_agent.py doctor
```

The guard script redacts common token-like arguments in logged command lines, but agents should still avoid passing secrets in command arguments. Prefer environment variables or the official CLI's secure config path.

## Approval examples

Good:

```text
I approve increasing ad set 123 daily budget from 5000 to 7500 minor units in account act_456.
```

Good:

```text
I approve activating campaign 123 after reviewing its budget, targeting, creative, URL, and tracking setup.
```

Bad:

```text
yes
```

Bad:

```text
go
```

Bad:

```text
looks fine
```
