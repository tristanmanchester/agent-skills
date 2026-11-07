# State, concurrency and effects

Contents: model the lifecycle · booleans and what they hide · async results ·
enforcement scope · retries and idempotency · the outbox · time · resources and
cancellation

## Model the lifecycle

For anything with a lifecycle (an order, an upload, a sync job, a connection, a
reconstruction run), write down:

- the states, each carrying only the data valid in that state;
- the legal transitions, and the event or guard behind each one;
- the single owner that applies transitions;
- the effects each transition causes;
- what happens to an illegal event: reject it with an error, or ignore it on purpose.

A plain linear flow (`load → parse → save`) is ordinary control flow and needs no
state machine. Reach for explicit states when operations depend on history, when
fields are only valid in combination, or when events arrive out of order.

```rust
pub struct Upload(State); // nothing outside this module can build a State

enum State {
    Pending { path: PathBuf },
    Sending { path: PathBuf, attempt: u32, started: Instant },
    Done { remote_id: RemoteId },
    Failed { path: PathBuf, error: UploadError, attempts: u32 },
}

impl Upload {
    pub fn on_success(self, remote_id: RemoteId) -> Result<Upload, Transition> {
        match self.0 {
            State::Sending { .. } => Ok(Upload(State::Done { remote_id })),
            other => Err(Transition::illegal("success", &other)),
        }
    }
}
```

Anyone can construct a variant of a `pub enum`, so its transitions mean nothing on
their own. Wrap the enum in a struct with a private field, or keep it `pub(crate)` and
expose only the methods. The same applies in every language: if callers can assign
the state directly, the transition methods are decoration.

**Persisted state** needs a stored state column (an enum or check-constrained text),
the timestamps of the events you care about, and transitions written as conditional
updates so two writers cannot both win:

```sql
UPDATE jobs SET state = 'running', started_at = now()
WHERE id = $1 AND state = 'queued';   -- 0 rows updated = someone else got it
```

**Derived state is computed, not stored.** If a value can be computed from other
state, compute it. When you must store it (for a cache or an index), write both values
in the same transaction or update, and own them in one place.

## Booleans and what they hide

Ask what fact a flag compresses, and keep the richer fact only when something in the
contract needs it. A one-way `attempted` flag that only gates a decision is a fine
boolean; a `confirmedAt` is worth it when the time matters to someone.

| You see | It may really be | Use, when the contract needs it |
| --- | --- | --- |
| `isConfirmed` set once by an event | When it happened | `confirmedAt: Instant \| null` |
| `isQueued`, `isRunning`, `isFailed` | Mutually exclusive states | One `status` enum, with timestamps per event if needed |
| `isAdmin`, later `isGuest`, `isSuperAdmin` | A role, or a set of capabilities | An enum for exclusive roles; a set for independent capabilities |
| `canEdit(): boolean` | A decision with a reason | `Allowed \| Denied { reason }` |
| `darkMode: boolean` | An independent setting | Keep the boolean |

## Async results must still be valid when they land

The question for every async completion is: **what makes this result still valid when
it arrives?**

- Tag each request with an id, revision or generation. Compare it at the point the
  result is applied, and drop stale results.
- Scope work to its owner: the screen, session, account or request. When the owner
  goes away, cancel the work *and* ignore anything that completes late.
- Check-then-act across an `await` is a race. Re-check after the await, or make the
  check and the act a single atomic step.
- Swift actors are reentrant at every `await`. In JavaScript and Python asyncio, any
  other task can run during an `await`. Either way, every invariant must hold at each
  suspension point, not just at the end of the function.

## Choose enforcement at the scope of the invariant

| Invariant spans | Enforce with |
| --- | --- |
| One object | Private fields and checked constructors or methods |
| One process | A mutex, an actor, or a single-owner task with a channel |
| Many processes or machines | A database constraint, conditional update, transaction or lease |
| Your system and someone else's | Idempotency keys, reconciliation, an outbox |

An in-process lock does nothing for a second worker. "SELECT, then INSERT if missing"
loses under concurrency; use a unique constraint and handle the conflict, or use
`INSERT ... ON CONFLICT`.

## Retries and idempotency

- Retry only failures that can succeed on a retry: timeouts, 429, 503, connection
  resets. Never retry validation errors or 4xx responses that will fail again.
- Bound retries by count *and* deadline, with exponential backoff and jitter. Honour
  `Retry-After`.
- A timed-out write may have happened. Send an idempotency key, or reconcile by reading
  back before retrying.
- Retries happen inside the operation's owner, not stacked at every layer. Three layers
  of three retries is 27 attempts.
- There is no "exactly once" over a network. Make handlers idempotent and deliver
  at least once.

## Local write plus remote effect: the outbox

When a local change must eventually reach another system (sync, email, webhook),
write the change and an outbox row in the same transaction. A worker sends outbox rows
and marks them done. Never "commit, then call the API": a crash between the two loses
the effect, and the reverse order loses the data.

## Time

- Store instants in UTC with an explicit type. Convert to local time only for display.
- Measure durations and timeouts with a monotonic clock (`Instant`, `performance.now()`,
  `time.monotonic()`), never wall-clock time.
- Inject the clock into code whose behaviour depends on time, so tests control it.
- Wait on conditions, never on fixed sleeps. A sleep in a test is a flake that hasn't
  happened yet.

## Resources and cancellation

- Scope resources to a block that releases them: `with`, `using`, `defer`, RAII,
  `try/finally`.
- Structured concurrency first: task groups, `TaskGroup`, `JoinSet`, `async let`.
  JavaScript has no equivalent: `Promise.all` rejects on the first failure but leaves
  the siblings running, so pass an `AbortSignal` when they should stop. A spawned task
  outliving its parent needs an explicit owner that cancels it and observes its failure.
- Cancellation must leave state valid. Commit atomically or roll back, and never leave
  a half-applied transition.
- Teardown that can fail needs an explicit `close()` or `finish()` that reports the
  error. Destructors can't report failure at all. A `finally` block can, but an
  exception thrown there replaces the original one, so decide which failure the caller
  should see.

## Optimistic local state

A local-first app shows a change before it is durable, and that's correct. What must
be designed is the failure. When the durable write fails, decide what stays visible,
what stays pending, and whether it retries. The choices are rollback, a visible
"unsaved" state, or retryable pending work. The bug is ambiguity: a rejected operation
whose change lingers in memory and is then silently persisted or uploaded by the next
successful write.

In a queue, decide what happens to an item that fails permanently. Parking it may be
right, but if order is part of the contract, the items after it that depend on it have
to wait or fail too.
