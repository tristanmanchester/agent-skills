# Review recipes

## Full repository audit

1. Run `scripts/audit_agent_use.py --root <repo> --markdown --output agent-use-report.md --json-output agent-use-report.json`.
2. Run `scripts/action_parity_inventory.py <repo> --output action-parity-inventory.md --csv-output capability-map.csv` for app/tool repos.
3. Inspect the generated capability map and manually classify high-value workflows.
4. Open the main routes/controllers/tools/CLI commands and verify implementation-level evidence.
5. Score only applicable dimensions and produce a prioritized plan.

## Pull request review

1. Identify changed user actions, tool/API/CLI surfaces, prompts, auth/safety code, and docs.
2. Ask whether each new human action has an agent path and each new agent path has context, safety, and verification.
3. Do not require full parity for unrelated old code unless the PR worsens it.
4. Recommend small patches: schema field, JSON output flag, dry-run option, docs link, eval, or capability-map row.

## Parallel review

For a large product, split reviewers by principle:

- Action parity.
- Context parity.
- Tool/API/CLI contract quality.
- Safety/permissions/recovery.
- Web/docs discovery.
- Evals/observability.

Merge by capability map, not by file list, so duplicate findings collapse into user-visible workflows.

## Acceptance tests for fixes

A fix is done when a fresh agent can discover the surface, choose the right action, provide required context/credentials, execute or preview safely, parse output, verify final state, and recover from one common error.
