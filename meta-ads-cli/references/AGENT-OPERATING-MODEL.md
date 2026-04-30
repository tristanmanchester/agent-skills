# Agent operating model

## The role of the agent

The agent is not a black-box optimiser. It is an operator that:

1. collects context;
2. translates intent into explicit CLI commands;
3. classifies risk;
4. gets approval for changes;
5. executes one safe step at a time;
6. verifies results;
7. explains outcomes in business language.

## Command lifecycle

Every command should pass through this lifecycle:

```text
Intent -> Context read -> Command plan -> Risk classification -> Approval gate -> Execute -> Parse -> Verify -> Report
```

### 1. Intent

Identify the user's goal:

- analysis/reporting;
- diagnosis;
- pause/resume;
- budget change;
- launch;
- creative rollout;
- catalog/product work;
- dataset/pixel work;
- cleanup/delete;
- regulated category operation.

### 2. Context read

Read the smallest useful context first:

```bash
meta --output json ads adaccount list
meta --output json ads campaign list --limit 25
meta --output json ads insights get --date-preset last_7d --fields spend,impressions,clicks,ctr
```

Use explicit `--ad-account-id` when multiple accounts may exist.

### 3. Command plan

For any mutation, show the user a compact plan:

```json
{
  "goal": "Pause ad 120000000000000 due to high CPA",
  "risk": "write",
  "reads_completed": ["ad details", "last 7 days ad-level insights"],
  "commands_to_run": [
    "meta ads ad update 120000000000000 --status PAUSED"
  ],
  "verification": [
    "meta ads ad get 120000000000000"
  ],
  "requires_user_approval": true
}
```

### 4. Risk classification

Use this hierarchy:

| Risk | Examples | Approval |
|---|---|---|
| `read` | list/get/insights/help | No approval needed |
| `write` | create/update/connect/upload/pause/archive | Explicit approval |
| `budget` | daily/lifetime budget, bid amount, spend cap | Explicit approval + before/after budget |
| `active` | `--status ACTIVE`, `activate` | Strong approval + `--allow-active` |
| `destructive` | delete/remove/force | Strong approval + `--allow-destructive` |
| `regulated` | housing/employment/credit/political/social issue/sensitive targeting | Human review; do not improvise |

### 5. Approval gate

Approval must be specific. Bad approval:

```text
ok
```

Good approval:

```text
I approve pausing ad 120000000000000 in account act_123 after reviewing the 7-day CPA.
```

### 6. Execute

Run through the guard script for consistency:

```bash
python3 scripts/meta_ads_agent.py run \
  --approved "I approve pausing ad 120000000000000 in account act_123" \
  -- meta ads ad update 120000000000000 --status PAUSED
```

### 7. Parse

Prefer JSON. If the CLI returns table/plain output:

- do not invent missing fields;
- re-run with `meta --output json ...`;
- if still not JSON, summarise only what is directly visible.

### 8. Verify

After every write, run a read:

```bash
meta --output json ads ad get 120000000000000
```

If the exact `get` action differs, use the installed CLI help to find the equivalent read.

### 9. Report

Report concise results:

```text
Paused ad 120000000000000.
Before: status ACTIVE, effective_status ACTIVE.
After: status PAUSED, effective_status PAUSED.
No campaign/ad set budgets were changed.
```

## How to handle uncertainty

- If the user supplied an object ID but not its type, read it or ask the CLI to identify it.
- If the account is ambiguous, list accounts and ask or use the account named by the user.
- If a metric is missing, say it is missing; do not infer conversions or ROAS from clicks.
- If a command fails, stop and diagnose before continuing to additional writes.
- If the installed CLI differs from this skill, prefer `meta ... --help`.

## Working files

Agents should create a local `work/` folder when they need durable state:

```text
work/meta_ads_context.json        account, page, dataset, catalog IDs
work/current_insights.json        latest report output
work/command_plan.json            reviewed plan before writes
work/run_log_notes.md             human-readable notes
```

Never store secrets in `work/`.
