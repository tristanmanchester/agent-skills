# Tests that catch bugs

A test is worth its maintenance cost when it fails on a plausible bug and passes on
correct code. Coverage percentage, test count and assertion count do not measure that.

Contents: three questions · weak → strong · oracles · property tests · doubles ·
stateful and failure paths · watch it fail · never buy green · what not to test ·
feedback loop

## Before writing a test, answer three questions

1. **What behaviour does it protect?** Name it in the test's title:
   `rejects_save_when_revision_is_stale`, not `test_save_2`.
2. **What bug would make it fail?** Name a plausible one: an off-by-one boundary,
   a skipped write, an accepted stale response, swapped axes, a missing auth check.
3. **Where does the expected value come from?** It must come from outside the
   implementation.

If any answer is "nothing", delete the test.

## Weak test → strong test

| Weak | Strong |
| --- | --- |
| Expected value computed with the production function or a copy of its formula | A hand-worked example, analytic result, dense reference, trusted external implementation, or a real property |
| Mock the function under test and assert it returned the mocked value | Run the real code; substitute only the network, clock, randomness or third-party service |
| Assert `repo.save` was called once | Read back what was persisted. Check that a failure leaves no partial write |
| Assert the result is defined, has a key, or has the right shape | Assert the actual values, the state change, or the rejection |
| Assert the order internal helpers were called in | Assert the outcome. Assert order only when order is the contract (authorise before writing) |
| Snapshot accepted because it matches today's output | A small, reviewed snapshot of output whose exact form is the contract, such as a CLI help text or a file format |
| A symmetric, square or zero-filled input | Asymmetric, non-square, off-centre input that exposes swapped axes, transposes and sign errors |
| `time.sleep(0.5)` then assert | Control the clock, or wait on the condition with a deadline |
| One test per function or file | One test per behaviour and per failure mode that matters |

## Oracles

The oracle is whatever tells the test the right answer. Choose an independent one:

- **Hand-worked examples.** Small inputs whose answer you computed by reasoning.
  These are often the best tests in the suite.
- **Analytic results.** A closed-form answer: the projection of a disc, the integral
  of a polynomial, the steady state of a simple system.
- **Dense or brute-force reference.** Solve a tiny instance the slow, obvious way
  (an explicit matrix, an exhaustive search) and compare.
- **Trusted external implementation.** Compare against a reference library in tests
  or benchmarks.
- **Properties.** Facts that hold for every input: the adjoint identity, invariance
  under a permutation, conservation, monotonicity, `decode(encode(x)) == x`.

Every oracle has blind spots, so combine them. A round-trip passes when encoder and
decoder share a bug. Idempotence passes for a function that returns a constant. Add
at least one fixed example with a known answer alongside each property.

## Property-based tests

Use Hypothesis (Python), fast-check (TypeScript) or proptest (Rust) when the input
space is large and a real property exists. In Swift, use parameterized
`@Test(arguments:)` over a deliberately chosen input table. Generate inputs
that reach the edges: empty, one element, duplicates, extremes, unicode. Keep the
seed and shrunk counterexample of a failure as a fixed regression example.

## Doubles

- **Real** when it is fast and deterministic: in-memory data structures, SQLite, a temp
  directory, a local Postgres in a container.
- **Fake** (a working in-memory implementation) for owned services across a seam.
- **Stub** for time, randomness and canned remote responses, including failures.
- **Mock assertions** only when the interaction is the contract: an idempotency key was
  sent, no request went out after cancellation, the payment call happened once.

A fake can share the production code's wrong assumptions about transactions, locking,
serialisation or ordering. When the guarantee lives in the database or the wire
format, test against the real one. Never add a production interface only to make a
mock convenient.

## Stateful, concurrent and failure paths

- Test illegal transitions and assert both the rejection and the absence of side effects.
- Test duplicate delivery, out-of-order completion, and a stale result arriving after
  a newer one.
- Test partial failure: the second write fails, so is the first rolled back?
- Test restart: persist, reload, and continue.
- Drive concurrency deterministically with barriers, controllable executors or fake
  clocks. Run the real concurrency mechanism when the guarantee depends on it.

## Watch it fail

A test you have never seen fail is unproven. Spend this effort where being wrong would
hurt most, or where you are least sure the test bites. Break the code in the way that
matters (accept the stale response, skip the write, let the failed rollback leave the
store writable), confirm the test fails for the right reason, and restore the code. A
few well-chosen breaks beat many easy ones.

For a failure path that protects an important guarantee, force the failure for real
(a storage write that throws, a rollback that fails, a crash between two writes). Then
check what the system allows afterwards, what stays visible, and what survives a reopen.

For a bug fix, the regression test must fail on the unfixed code. Mutation tools
(mutmut, Stryker, cargo-mutants) are useful for auditing a suite. Read the survivors
for meaningful gaps instead of chasing a score: a surviving `Display` mutant matters
far less than a surviving "store stays writable after a failed fsync".

## Never buy green

When a test fails, find out which is wrong: the code or the expectation. Change the
expectation only after showing the old one contradicts the intended behaviour, and
say so in the commit. Don't loosen tolerances, raise thresholds, rerun until a flaky
test passes, add `skip` or regenerate snapshots to make a change pass. Never report a
test as passing unless you ran it and saw it pass.

## What not to test

- Constants, type declarations, re-exports, plain getters.
- The framework or language itself (that React renders, that a dataclass stores fields).
- Plain forwarding with no mapping or policy.
- Exact log lines, timing thresholds that depend on the host, and private helpers
  already covered through the interface.

Mechanical changes (renames, moves, formatting) are covered by the existing suite.
Small code can still need strong tests when its behaviour matters: auth, money,
numerics, data migrations.

## Feedback loop

Run the narrowest relevant tests first, then the module's suite, then the project's full
check command. Keep the full suite fast enough to run on every change; mark slow
integration and GPU tests with markers or tags and run them before handing off.
When a failure comes from the environment (missing GPU, no network, no credentials),
report that it is environmental and name what was not run.
