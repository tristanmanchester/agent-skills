# Reactivity, concurrency, and result ownership

## State

Use reactive when changes should participate in UI refresh/layout as configured.
Use var for reactive behaviour without automatic refresh/layout; it still has
watchers and other reactive features. A plain attribute is appropriate when none
of that machinery is needed. Keep compute_* pure and cheap. Watchers can schedule
work or update UI but should not block. set_reactive supports deliberate initial
values without triggering premature watchers; inspect mounted-widget availability.

## Choose the execution mechanism

An async worker is concurrent with message handling, not a new CPU thread. Await
nonblocking I/O inside it; do not call requests.get, time.sleep, heavy parsing, or
blocking subprocess APIs there and expect responsiveness. Use thread=True for a
blocking I/O API; choose a process/native computation strategy when CPU/GIL cost
requires it. Bound input sizes, subprocess lifetime, and remote request timeouts.

@work wraps a method and returns a Worker when called. Do not await the decorated
method as though it were the original coroutine. Waiting for worker.wait inside a
message handler can still hold up that handler's message processing; use completion
messages/events when appropriate.

## Cancellation and latest-result wins

Exclusive workers cancel earlier work in the applicable group; choose groups so
unrelated operations do not cancel one another. Coroutine cancellation needs
cooperative cleanup and must not be swallowed as a normal success. Thread workers
cannot be forcibly cancelled like a coroutine: check get_current_worker().is_cancelled
and use the underlying operation's own timeout/cancellation support.

For robust result ownership, increment a revision on each new search/selection,
pass it with the request, and check that same revision on the UI thread immediately
before applying success or error. A thread's earlier cancellation check alone has
a race with a new request. Marshal updates through post_message or call_from_thread;
do not mutate widgets/reactive values directly from the worker thread. Ignore
results for a removed screen or obsolete selection.

Do not use latest-request-wins for payments, saves, or deletes as though cancellation
undoes the operation. Persist an operation identity, gate duplicate submissions,
and reconcile unknown outcomes. A cancelled wait does not prove remote cancellation.

## Errors and lifecycle

Worker errors exit the app by default; use exit_on_error=False deliberately for
recoverable failures and handle Worker.StateChanged/error outcomes visibly. Do not
silently swallow exceptions into empty results. Keep PENDING/RUNNING/SUCCESS/ERROR/
CANCELLED distinct, including progress and retry affordances.

Workers are associated with their originating DOM node. Removal/app exit cancels
managed workers, but external threads/processes/network writes still need their
own lifetime controls. Close streams, subprocesses, temporary files, and clients
in cleanup. Stop observers/timers on teardown; do not keep updating removed widgets.

## Streaming views and tests

Batch appropriate UI changes; preserve user navigation and scrollback. Anchor only
when the user is following the tail. Bound retained logs/transcript rows and use
backpressure or sampling rather than indefinitely mounting widgets per token.
Render untrusted text without enabling unintended markup, links, or terminal escapes.

Test out-of-order results, cancellation before/after completion, failure after a
new selection, screen removal, repeated input, timeout, and teardown. Use controlled
fake services and observable state with a deadline; fixed sleeps and snapshot-only
checks miss these races.

Reviewed sources:
- https://textual.textualize.io/guide/workers/
- https://textual.textualize.io/guide/reactivity/
- https://textual.textualize.io/guide/testing/
