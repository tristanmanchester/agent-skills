---
name: good-engineering
description: Use when implementing a feature, fixing a bug, refactoring, designing a module or API, writing or reviewing tests, starting a new project, or auditing a codebase for correctness, design or agent-readiness, in any language including Python, TypeScript, React/React Native, Rust, Swift and numerical code. Also use when tests look tautological, code is over-engineered, state is tracked with booleans, or a race or stale result is suspected.
---

# Good engineering

You are a strong engineer. This skill describes what good looks like here, why it
matters, and the traps capable agents still fall into. It is a description of
judgment, not a checklist: when a principle would make a particular piece of code
worse, the reason behind the principle wins.

Good code works, says what it guarantees, and lets the next agent change it without
breaking anything. Everything below serves those three things.

## What good looks like

### It works, and you know why you believe that

The job is the working behaviour, not the diff. Run the real thing (the CLI, the app,
the endpoint, the simulator) and look at what it does. A passing unit test suite is
evidence about the units, not about the product. When you report, say what you ran,
what it showed, and what you couldn't check. Never claim a check you didn't run.

### The change is complete

Before editing, read the repository's own instructions and find the checks it requires
for this kind of change. A shared fix or contract change is finished when every variant
of the problem is handled: the other call sites, the sibling forms (a savepoint as well
as a transaction, a single-slice scan as well as a volume, a benchmark as well as the
library), and the docs and fixtures that describe the old behaviour. When you think
you're done, search for anything still using the old behaviour. A complete
cross-cutting change can touch many files. Proportion means every edit belongs to the
change, not that the diff is small. Finish by running the repository's required gates
(guardrails, ratchets, type checks) within the task's limits.

### Guarantees live in the code that can enforce them

For each guarantee your work relies on, know which code makes it true. Comments explain
a guarantee and tests check it; only code, types and constraints enforce it. Put
enforcement where it can't be bypassed:

| Guarantee | Enforced by |
| --- | --- |
| An interval's end is after its start | Private fields and a constructor that checks; nothing can mutate it afterwards |
| Emails are unique | A unique index, with the conflict handled. A pre-check is UX; the index is the enforcer |
| Users edit only their own records | The authorisation check inside the operation that writes |
| A stale response never overwrites newer state | A request id or revision compared where the result is applied |
| A saved note always has a pending sync entry | One transaction that writes both |
| Loaded data is valid | The same constructor everything else uses. Deserialisation is not a back door |

Untrusted input (JSON, files, env vars, user input, network replies) gets parsed once at
the boundary into types that hold only valid values. Inside, trust those types. Defensive
re-checks on values that are already guaranteed are noise that hides the checks that
matter.

### State says what is actually true

Represent the facts the program depends on, in one place, so contradictory
combinations can't exist. Three booleans (`isLoading`, `error`, `data`) that must
change together are really one state with a tag. When what's allowed depends on
history, one owner applies the transitions; an enum alone names states but doesn't
stop anyone assigning them. Ask what fact a flag compresses. Sometimes you need *when*
(a timestamp) or *why* (a denial reason); often a plain boolean is exactly right.

Async work is where state goes wrong most often. When a result lands, check that it
still applies: the same request, revision, screen or account. Cancelling a request
doesn't stop a late response from arriving.

```ts
type Load<T> =
  | { kind: "idle" }
  | { kind: "loading"; requestId: number }
  | { kind: "ready"; data: T }
  | { kind: "failed"; error: AppError };

function onResponse(state: Load<Note[]>, requestId: number, data: Note[]): Load<Note[]> {
  if (state.kind !== "loading" || state.requestId !== requestId) return state; // stale
  return { kind: "ready", data };
}
```

### Callers get a whole job behind a small interface

A module's interface is everything a caller must know: the signature, the call order,
states, errors, effects and performance. Good modules keep that small and do a complete
job behind it. If every caller has to validate, open a transaction, write, enqueue sync
and commit, the callers are doing the module's work; give them
`notes.save(note, { expectedRevision })`. Hide decisions, but expose guarantees: "saved
locally and queued" and "acknowledged by the server" are different promises, and
callers need to know which they got.

Abstractions earn their place by what they take off callers: an invariant, a
transaction, a resource lifetime, a protocol, a concept the caller shouldn't have to
know. Imagine deleting one. If complexity vanishes, it was a pass-through. If it
reappears in every caller, it was earning its keep. A chain of one-caller helpers
carved out of a coherent function is the same function, harder to read. Prefer
deriving a setting from the data to adding an option, because every option is a
behaviour to test and document. Return results together with the settings, revision
or units that produced them, so callers don't have to keep metadata in sync.

When your own method gets a case wrong, improve the method rather than detecting the
case and routing around it: a bypass hides the defect and fails at its threshold.
Distinct regimes that are genuinely part of the method (a piecewise formula, a stable
branch for small values) are design, not bypasses; give them their own tests. A
workaround for someone else's bug names that bug and goes when it does.

[design](references/design.md) goes deeper on seams, coupling and refactoring.

### Things that change together live together

The expensive bugs in a growing codebase come from links nobody can see: a constant
copied in three places, parallel lists of the same actions, a call order callers have
to remember, a global one module sets and another reads. Make these links explicit
with one source of truth, generated code, or a type that forces both sides to change.
Cut the needless links too: callers reaching into internals, and stable code importing
volatile code. Remove what has no reason of its own to exist: pass-through wrappers,
options nothing varies, dead code, `v2` beside `v1`.

One concept has one name across code, CLI, API and docs. When you replace something,
migrate its callers and delete the old path. Keep a compatibility shim only for a real
external consumer. Data is the exception: changing a schema means migrating the data
too.

### Failure is designed, not discovered

Decide what each failure means to the caller, and make it say that.

- Never let a failure pass as success: `catch { return [] }` makes "you have no notes"
  indistinguishable from "we couldn't load your notes".
- Catch where you can act (retry, translate into a domain error, show the user).
  Everywhere else, let the error propagate with its cause.
- Distinguish optimistic visibility from durable completion. When a write fails, it
  should be clear what stays visible, what stays pending, and whether it will be
  retried. A rejected operation must not quietly become committed through a later one.
- A timeout doesn't mean the remote operation failed, so retried writes need an
  idempotency key. Loops around remote calls (retries, rebases, polls) end somewhere
  with a clear error.
- Every task, subscription, connection, transaction and timer has an owner that ends
  it on success, failure and cancellation. Races are fixed by waiting on the condition
  or making the operation atomic, never by sleeping.

[state](references/state.md) covers lifecycles, concurrency, retries, outboxes and time.

### Tests are evidence

A good test fails on a plausible bug and passes on correct code. That one idea
explains everything else here:

- The expected value comes from somewhere independent of the code: a hand-worked
  example, an analytic result, a brute-force reference, a real property. An expectation
  computed by the code under test, or by a copy of its formula, proves nothing. Oracle
  logic in a test is fine as long as it is simpler than, and independent of, the
  production algorithm.
- Test through the interface callers use, and keep focused tests on hard internals:
  parsers, numerics, state machines, concurrency.
- Substitute only across real seams: network, clock, randomness, third-party and
  remote services. Mocking the unit under test, or asserting a mock was called when
  the real question is whether the result is right, tests the test.
- When the guarantee depends on database, filesystem or protocol behaviour, test
  against the real thing (an in-memory SQLite, a temp directory) and reproduce the
  actual failure. Choose inputs so the plausible wrong implementation gives a different
  result. A test that passes whether or not the code does its job proves nothing.
- Put the strongest evidence on the guarantees you'd least like to get wrong. For
  those, break the code on purpose and confirm the test notices. Force the failures
  that protect important guarantees (a failed rollback, a conflict, a crash between two
  writes), then check what is allowed, visible and durable afterwards.
- A failing test is information. Change an expectation only once you've shown it was
  wrong; never loosen a tolerance or regenerate a snapshot just to get green.
- Constants, type declarations, plain forwarding and framework behaviour don't need
  tests. Mechanical changes ride on the existing suite.

[testing](references/testing.md) has oracles, doubles, property tests and failure testing.

### Proportion

The best change is the smallest one that does the whole job. Reach for what already
exists first: this repo's helpers, the standard library, the platform, an installed
dependency. Add a dependency when it removes real correctness burden. Grow structure
from responsibilities that exist today; split a module when it has two reasons to
change, not because it got long. Tooling and checks earn their place like code does.
A long-lived library wants strict types, lint, a single check command and enforced
boundaries early. A one-off script wants to run and be checked. When a rule matters
and keeps getting broken, make a machine enforce it, with an error message that says
how to fix the problem. Keep unrelated cleanup out of the change, and stop when the
work is done.

## Traps capable agents still fall into

- Casting external data (`as User`, `cast()`, `!`, `.unwrap()`) instead of parsing it.
- Keeping the old implementation beside the new one "for safety".
- Adding an interface, protocol or trait only so a test can mock it.
- Wrapping everything in `try/catch` that logs and carries on.
- Adding a flag or parameter instead of choosing the right behaviour.
- Writing a test's expected value by running the code and pasting the output.
- Stopping when the code is written instead of when the behaviour works.
- Reporting tests as passing when they didn't run, or only some did.
- Docstrings that restate the signature, and comments that restate the line.
- Tidying unrelated code in the same change.

## Kinds of work

**Changing existing code.** Find the code that owns the behaviour and follow one real
call through it before deciding where the change goes. Then reach everything the change
touches (callers, types, fixtures, config, docs) and remove what it replaces.

**Fixing a bug.** Reproduce it first, ideally as a failing test, so you know the fix
fixes it. Fix the cause where it lives. Sibling instances with the same cause belong in
the fix; unrelated ones go in the report.

**Starting a project.** Get the thinnest real path working end to end, with a way to run
and check it. Model the domain's states and invariants early, since that's cheap now
and expensive later. Read [agent-readiness](references/agent-readiness.md) for setting
up a repo that agents can work in.

**Auditing or reviewing.** Read [audit](references/audit.md). Findings come from tracing
and running code, with a concrete trigger and consequence, not from file sizes, scores
or taste. "Nothing worth fixing" is a valid result.

## References

Read the one that matches the work. Follow the repository's own conventions and
toolchain wherever they exist.

- [design](references/design.md): modules, seams, coupling, dependency direction, refactors.
- [state](references/state.md): lifecycles, async, concurrency, persistence, retries, time.
- [testing](references/testing.md): oracles, doubles, property tests, failure and mutation checks.
- [boundaries](references/boundaries.md): enforcing module boundaries and API surfaces.
- [audit](references/audit.md): auditing a codebase or reviewing a diff.
- [agent-readiness](references/agent-readiness.md): making a repo easy for agents to run, check and change.
- [numerical](references/numerical.md): numerical, scientific, array, GPU and ML code.
- Languages: [python](references/python.md), [typescript](references/typescript.md),
  [react](references/react.md), [rust](references/rust.md), [swift](references/swift.md).
