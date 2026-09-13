# Jobs and monitoring

Inspect installed help before optional flags; the current source is the
[official CLI documentation](https://docs.parallel.ai/integrations/cli) and
[maintained implementation](https://github.com/parallel-web/parallel-web-tools).
Reviewed 2026-09-13. No old CLI alias compatibility is required.

## Research

Choose a processor from `parallel-cli research processors --json`; do not bake a
premium tier into every request. For an authorised asynchronous submission:

```bash
parallel-cli research run "$QUESTION" --processor "$PROCESSOR" --no-wait --json
parallel-cli research status "$RUN_ID" --json
parallel-cli research poll "$RUN_ID" --timeout 120 --json
```

The example's 120 seconds is one bounded wait, not an estimate of task duration.
Keep a total deadline across polls. On expiry, return the pending ID/status or
cancel only through a supported, authorised operation. A cancelled local process
does not cancel a remote run. Inspect output/basis and sources before summarising;
verify actual `.json`/`.md` files when using `-o` rather than inventing paths.

## Enrichment

Use a small sample and explicit typed output columns before processing a large
input. Preserve stable source row IDs and distinguish zero, empty, unknown, and
failed fields. Avoid duplicating rows or overwriting original data on a retry.

```bash
parallel-cli enrich run \
  --source-type csv --source "$INPUT" --target "$OUTPUT" \
  --source-columns '[{"name":"company","description":"Company identity"}]' \
  --enriched-columns '[{"name":"website","description":"Official website"}]' \
  --dry-run --json
```

Review the preview, budget, input scope, and destination before the authorised
run. Use `--no-wait` when splitting submission from polling; retain `taskgroup_id`
and inspect `enrich status`/`enrich poll` help. Reconcile partial rows using their
original identities. An AI-suggested schema is a proposal, not permission to
collect additional personal data or spend on unrequested columns.

## FindAll

Define entity identity and matching criteria separately. Choose the documented
generator (`base`, `core`, or `pro`) and a bounded match count. Do not confuse
fast `entity-search` ranking with per-candidate verification.

```bash
parallel-cli findall run "$OBJECTIVE" --generator core --match-limit 25 --dry-run --json
```

**This preview calls the ingest endpoint.** It avoids creating the FindAll run;
it is not a wholly offline/no-network operation. Do not promise zero cost without
checking the applicable billing contract.

With `--no-wait`, the current CLI returns after ingest/create; suggested enrichments
are not automatically applied as in the synchronous workflow. Use the documented
`findall enrich` step when needed. Persist the run ID, inspect status/results, and
retain match evidence/rejections/partial failures. Cancellation is a separate
operation; a failed poll is not a reason to create another discovery run.

## Monitors

Creating a monitor schedules ongoing provider work and can deliver externally.
Use only for explicitly authorised Parallel monitoring, with a clear frequency,
objective, processor/cost policy, and verified notification destination.

```bash
parallel-cli monitor create "$OBJECTIVE" --frequency 1d --json
parallel-cli monitor get "$MONITOR_ID" --json
parallel-cli monitor events "$MONITOR_ID" --json
```

Current syntax uses `--frequency` (`1h`, `1d`, `1w`, etc.), not the old `--cadence`.
`event_stream` monitors a query; `snapshot` monitors a Task Run's output and needs
its task-run ID. Define the intended event schema where supported and avoid
sending sensitive results to an unverified webhook URL.

`monitor trigger` runs a **real off-schedule check**, not a synthetic webhook
simulation. `monitor cancel` permanently stops future runs and is irreversible;
it is not a pause/resume toggle. Read state and explain that consequence before
an authorised cancellation. Listing defaults to active monitors; include cancelled
state deliberately when reconciling history. Do not claim notification delivery
from monitor creation alone; verify events and the receiving endpoint.

## Failure triage

Distinguish usage/auth/API errors from timeout. Resolve actual permissions rather
than broadening credentials reflexively. For a malformed response or transport
failure after submission, preserve the original request metadata and reconcile
whether the job was created. Retrying a paid submission with a new identity can
duplicate work. Existing provider-side processing may continue even when this
conversation or CLI exits.
