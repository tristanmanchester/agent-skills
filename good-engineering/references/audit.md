# Auditing a codebase or a change

An audit finds where the code can break its promises and where it makes change
expensive, and proves each finding. It produces a short list someone can act on,
not a score.

## Scope

- If the user named a concern, area or diff, start there.
- Otherwise, find the hot spots: `git log --since=6.months --name-only --format= | sort | uniq -c | sort -rn | head -30`.
  Code that changes often is where design problems cost the most.
- Read `AGENTS.md`, `CONTRIBUTING.md`, ADRs and design docs first. Don't re-propose a
  decision the project already recorded unless you have new evidence.

## Read

1. **Run the project.** Set it up from its own instructions and run its check command.
   Note every step that failed or needed knowledge the repo doesn't contain.
2. **Trace two or three real operations** end to end, through entry point, validation,
   policy, state, effects and errors. Most design and correctness findings come from
   these traces.
3. **Check the invariants** you discover. For each, find the enforcer. A guarantee
   with no enforcer, or with a back door (a setter, a raw SQL path, a deserialiser,
   a second writer), is a finding.
4. **Read the tests for the code you traced.** Would they fail if the code were wrong?
   Break something and check.
5. **Look for the coupling patterns** in [design](design.md): hidden links, needless
   links, surplus, special cases.

Use subagents to summarise or sweep large areas, then confirm every finding yourself
in the code. Treat scanner and linter output as leads, never as findings.

## What counts as a finding

A finding has a concrete trigger and a concrete consequence:

- **Defect**: an input, interleaving or sequence that produces a wrong result, data
  loss, a security hole or a crash. Show the trigger.
- **Risk**: a plausible path to a defect that you could not trigger here, such as one
  that needs production load or a specific device. Say what would confirm it.
- **Change cost**: a change that should be local but forces edits in several places
  (show which), or a guarantee an agent would break without knowing it existed.
- **Weak evidence**: a test or check that would pass on broken code. Show the
  mutation it misses.

These are not findings: a long file with one responsibility, a pattern you would have
written differently, a missing abstraction with no current cost, low coverage on
trivial code, or a high churn count on its own.

## Report

Group findings under the root cause that explains them, with the fix first.
Order the groups by consequence: data loss, security and wrong results first, then
change cost.

```md
## 1. Sync state is spread across three booleans and two writers   [defect]

**Fix:** Replace `isSyncing`, `syncFailed` and `hasPending` with one `SyncState` owned by
`SyncQueue`; route the background task and the settings screen through `SyncQueue.retry()`.

- `sync/queue.ts:88`: the retry handler sets `isSyncing = false` before the request
  finishes, so a second retry can start (trigger: tap Retry twice within 300 ms;
  two uploads of the same note).
- `settings/Sync.tsx:41` writes `syncFailed = false` directly, bypassing the queue.
- `sync/queue.test.ts` mocks `upload()` and asserts it was called. It still passes if
  the duplicate upload happens.

**Evidence:** reproduced the double upload with the test in `/tmp/audit/double-retry.test.ts`.
```

End with:

- **Inspected**: the areas and paths you read, and the commands you ran.
- **Not covered**: what you could not run or reach.
- **Top fix**: the single change you would make first, and why.

If nothing is worth fixing, say so plainly and list what you inspected.

## When asked to fix the findings

Fix them in root-cause order, each as one coherent change with its tests. Remove the
special cases the redesign makes unnecessary. Re-run the traces and the full check at
the end, and confirm behaviour is unchanged apart from the defects you fixed.

## Reviewing a diff

Review the change against the rules in SKILL.md, then:

- Does every caller of a changed function still work? Search for them.
- Is anything the change replaced still present?
- Would each new test fail without the change? Run it against the base commit, or
  mentally revert the change.
- Did the change touch unrelated code?

Report only findings with a concrete failure or cost, ranked by severity.
