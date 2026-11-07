# Rust

Run `cargo fmt`, `cargo clippy --all-targets -- -D warnings` and `cargo test` for the
affected features and targets. Use the project's MSRV and edition.

## Types carry the invariants

- Newtypes for identifiers and units (`struct NoteId(Uuid)`, `struct Millimetres(f64)`)
  so they can't be mixed up.
- Fields stay private when they carry an invariant. Construct through `new` / `TryFrom`
  that checks it, and offer no `&mut` access that could break it.
- **Deserialisation goes through the same check.** `#[derive(Deserialize)]` on a
  type with private invariants is a back door. Route it through the checking
  constructor:

  ```rust
  #[derive(Deserialize)]
  #[serde(try_from = "RawInterval")]
  pub struct Interval { start: Timestamp, end: Timestamp }

  impl TryFrom<RawInterval> for Interval {
      type Error = IntervalError;
      fn try_from(raw: RawInterval) -> Result<Self, Self::Error> {
          Interval::new(raw.start, raw.end)
      }
  }
  ```

- Enums with data for states (see [state](state.md)). Transitions consume `self` and
  return the next state, so an old state can't be reused.
- Typestate (`Connection<Open>`) when the compiler should forbid a call order and the
  state is known statically. For runtime-driven or persisted states, use a private enum
  with checked methods, since typestate pushes the state into every caller's types.
- `#[non_exhaustive]` on public enums and structs that will grow.

## Errors

- `Result` for anything that can fail at runtime. Use `thiserror` enums in libraries,
  with variants callers handle differently, and `anyhow` (with `.context(...)`) in
  binaries.
- `unwrap()` and `expect()` are for invariants the code has already established, and
  `expect` says which: `.expect("regex literal is valid")`. Both are fine in tests.
- Never swallow errors with `let _ =`, `.ok()` or `unwrap_or_default()` on operations
  whose failure matters.
- Real checks are `if ... { return Err(...) }` or `assert!`, never `debug_assert!`, which
  disappears in release builds.

## Ownership is design information

Don't add `.clone()`, `Rc<RefCell<_>>`, `Arc<Mutex<_>>`, `'static` bounds or `unsafe` to
silence the borrow checker. The error is showing that ownership is unclear: decide who
owns the data and who borrows it. Shared mutable state across threads gets one owner
(an actor task with a channel) or a lock with a documented scope.

`unsafe` stays in small functions, each with a `// SAFETY:` comment stating what makes it
sound. Wrap it in a safe API that upholds those conditions for every caller.

## Async (Tokio)

- Never hold a `std::sync::Mutex` guard across `.await`; clippy's `await_holding_lock`
  catches it. Use `tokio::sync::Mutex` only when the critical section really must await.
- Every `tokio::spawn` handle is owned. Join it, put it in a `JoinSet`, or keep it in a
  struct that aborts it on drop. A dropped `JoinHandle` detaches the task and loses
  its panic.
- `select!` drops the losing branches. Only race futures that are cancel-safe, or a
  partial read or write gets lost.
- Blocking or CPU-heavy work goes in `spawn_blocking` or on a rayon pool.
- Pass a `CancellationToken` down to long-running work and leave state valid when it
  fires.

## Teardown

`Drop` is for cleanup that can't fail meaningfully. When the outcome of teardown
matters (flushing a file, committing a transaction), provide `fn finish(self) ->
Result<...>` and make the drop path the abort path. Don't panic or block in `Drop`.

## Boundaries and traits

- `pub(crate)` by default for anything that isn't the crate's API. Workspace crates for
  enforced layering ([boundaries](boundaries.md)).
- Add a trait at a seam with two real implementations, or for an extension point that
  outside crates use. Generic parameters and trait objects with one implementation are
  indirection.

## Tests

- Unit tests in `mod tests` for internals; integration tests in `tests/` against the
  public API.
- proptest for parsers, codecs and numerical properties. Keep shrunk failures as
  fixed cases.
- `cargo-mutants` to audit whether the suite catches injected faults.
- Run with `--all-features` and the feature combinations you support.
