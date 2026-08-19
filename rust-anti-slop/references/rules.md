# rust-anti-slop prose rules

These rules cover what no lint can see. Clippy enforces the mechanical third of
this policy (see `assets/workspace-lints.toml`); everything below is judgment
the agent applies while writing and reviewing. The common thread: **Rust's type
system carries evidence — of fallibility, ownership, thread-safety,
exhaustiveness, and completion. Slop is any pattern that discards that evidence
or fabricates it.** When a rule here conflicts with getting the compiler to
shut up quickly, the rule wins.

## 1. Justify every `.clone()`

A borrow-check error is the compiler handing you an ownership analysis.
Cloning to make it go away throws that analysis in the bin. Every `.clone()`
of non-`Copy` data needs a semantic ownership explanation — the domain needs
two independent values, the receiver stores or outlives the call, the value
crosses a task boundary, a snapshot is intended, or it's a cheap handle copy
(`Arc`, `Rc`, channel senders — prefer `Arc::clone(&x)` so intent is
visible). The explanation should be evident from local data flow or the API
contract; add a comment only when it isn't — do not annotate self-evident
handle clones and value-semantic copies. A clone that exists only because
the borrow checker complained is a design bug: restructure ownership, split
the borrow, pass a reference deeper, or name the lifetime.

```rust
fn render_path(path: &Path) { /* ... */ }

// SLOP: render_path only borrows; this allocation has no ownership role.
let root = config.root.clone();
render_path(&root);

// Instead:
render_path(&config.root);
```

A clone inside a potentially hot or unbounded loop needs both an ownership
reason and a bounded-cost argument — sending owned work to tasks and taking
deliberate snapshots qualify; ending a borrow does not. Never `clone()` a
`String` to call a `&str` parameter. `Cow<'_, str>` covers the
borrow-usually, own-sometimes case, but don't reach for it reflexively — it
spreads lifetime complexity through otherwise simple code.

## 2. Panics carry arguments: `expect("…should…")` and `// SAFETY:`

`.unwrap()` is banned by lint. `.expect()` is legal **only** with a message
that argues the invariant — std's "expect as precondition" style, phrased with
*should*, stating why failure is impossible, not what failed:

```rust
// SLOP: restates the operation; zero evidence
let config = load_config().expect("failed to load config");

// OK: states the invariant a reviewer can check
let re = Regex::new(PATTERN).expect("PATTERN is a hardcoded, tested regex and should compile");
```

If you cannot finish the sentence "…should … because …", you don't have an
invariant — you have a `Result` to propagate. The same standard applies to
`// SAFETY:` comments (state the proof obligation and why it's satisfied, not
"this is safe") and to `#[expect(lint, reason = "…")]` reasons. A message that
merely restates the operation is a violation even though the lint passes.

## 3. Error types follow the crate's role

Libraries, by default: small error enums per unit of fallibility (a
`ParseError` near parsing, a `ConnectError` near connecting — not one
crate-wide `Error` dumpster), derived with `thiserror` or hand-written,
`#[non_exhaustive]` where the failure set will grow, source chains preserved
via `#[source]` — use `#[from]` sparingly, since it silently makes a
dependency's error type part of your public conversion contract. The std
contract: a wrapped source is exposed through `Error::source()` *or* rendered
into the `Display` message, never both (double-rendering produces
"context: context: root cause" chains); this policy chooses `source()`, so
`Display` messages are lowercase, without trailing punctuation, and without
the source's text. Binaries: `anyhow::Result` with
`.context()`/`.with_context()` at every I/O boundary so failures carry an
operation trail.

Never: `Result<T, String>` or `.map_err(|_| MyError::Failed)` — the `|_|`
destroys the source chain that makes the error debuggable (a deliberate
security-redaction boundary carries an `#[expect]` with its reason). `anyhow`
and `Box<dyn Error + Send + Sync>` don't belong in a library's public
signatures, with one exception: a deliberately type-erased boundary (plugin
interfaces, callbacks, framework glue) where erasure *is* the contract —
state that in the API docs.

**Log once.** An error is logged at the boundary that decides its fate —
where it's retried, dropped, or reported — and nowhere else. Lower layers add
typed context and propagate; they do not `tracing::error!` and then return the
same error for every caller above them to log again. Log-and-propagate is
double-counting: it turns one failure into five log lines and makes incident
triage lie about error rates.

## 4. Parse, don't validate

*Structural* invariants — this string is syntactically an email address,
this integer is non-zero, this digest has the right length — are parsed once
at each untrusted representation boundary, through a fallible constructor
returning an invariant-carrying type. Interior code takes `EmailAddress`,
`Port`, `NonEmptyVec<T>` — not `String` plus a prayer that someone upstream
checked; a function that begins by re-checking a structural property its
parameter type could carry has the wrong parameter type. *Contextual*
invariants — the user still exists, the token hasn't expired, the resource
is still owned by the caller — are different: they are checked where the
authority and current state live, and re-established after storage, wire,
FFI, or other trust boundaries the type's proof doesn't survive. Parse,
don't validate is not "never check a fact twice"; it's "don't re-check what
the type already proves." Make invalid states unrepresentable: an enum with
data per state, not
`is_connected: bool` alongside `session: Option<Session>`. Replace boolean and
`Option` parameter soup with two-variant enums or a config struct.

**`Default` must mean something.** Derive `Default` only when a natural,
valid, unsurprising default exists. "Serde wants it," "tests are easier," and
"zero values compile" are not defaults — they are invalid states with a
constructor, converting construction errors into later runtime errors. Use a
fallible constructor, a builder, or named presets (`Config::development()`)
instead.

## 5. `Arc<Mutex<T>>` is a decision, not a default

A lock is a design statement: "concurrent mutation of this exact state is
required here." `Arc<Mutex<T>>` introduces shared ownership plus serialized
access to that particular state (it does not make non-`Send` data `Send`,
and it does not serialize the whole program) — the smell is reaching for it
reflexively, adopting shared mutation without identifying its owner,
invariant, contention scope, or shutdown semantics. Match the mechanism to the
sharing shape rather than walking a hierarchy: one serial owner with command
semantics → a state-owning task and channels (an actor buys ordering but
costs queues, shutdown, and partial-failure handling — it isn't free);
shared immutable snapshots → `Arc<T>`; independent scalar state → an atomic
(only when the invariant really is one atomic operation); a short
synchronous critical section → `Mutex<T>`, guard scoped tight;
demonstrably read-dominated state → perhaps `RwLock<T>`; an I/O resource
intentionally held across awaits → an async mutex or, better, an owner task.
Prefer a synchronous mutex (`std::sync` or `parking_lot`) for ordinary data
in async code — the std guard is `!Send`, so the compiler rejects holding it
across `.await` in spawned (work-stealing) tasks, though not in
`LocalSet`/`block_on` contexts, so the discipline still needs review. An
async mutex requires an explicit reason why the guard must cross an await
(a shared I/O resource is the classic legitimate one); where it does,
consider whether an owner task gives clearer ordering and lifecycle
semantics.

`unsafe impl Send`/`Sync` written to make a compiler error disappear is
fabricated evidence. A manual implementation is legitimate only in
quarantined unsafe code (raw-pointer containers, FFI handles) with a
`// SAFETY:` argument covering ownership, aliasing, thread affinity,
destruction, and the generic bounds — the Rustonomicon's standard, not a
one-line "this is fine."

## 6. Ownership in signatures follows semantics

Borrow when the callee only observes the value for the duration of the call:
`&str` not `&String`, `&[T]` not `&Vec<T>` (the `&String`/`&Vec` forms force
the caller's representation for no gain). Own when the callee stores,
returns, transfers to a task or closure, consumes, or deliberately snapshots
the value — taking `&str` and immediately `.to_owned()` hides an allocation
the caller could have moved. Use exact parameter types inside the codebase;
add `impl AsRef<Path>`/`impl Into<String>` conveniences at caller-facing
boundaries only where they materially improve the API. Preserve iterator
laziness when laziness is part of the contract; collecting is deliberate —
justified by sorting, deduplication, a snapshot, multiple passes, ownership
transfer, or ending a borrow — not a reflex between two adapter chains.
Return `impl Iterator` when callers may not need a `Vec`, but not where it
locks a public API's evolution or leaks awkward lifetimes. Choose iterator
vs index loops by semantics: `for x in &v` when the index is meaningless,
indexed iteration when the index itself carries meaning or several
collections move in step.

## 7. No fake completion

`todo!()` and `unimplemented!()` are banned by lint; this rule bans their
prose cousins: `// for now`, `// in a real implementation`,
`// TODO: handle errors`, `// simplified version`, stub functions returning
`Default::default()`, and hardcoded values dressed as logic. Code that
compiles is not code that's done — a stub is fabricated completion evidence.
Either implement it, return a typed `Unsupported`/`NotYetImplemented` error
variant that callers can see, or say plainly in the summary that the piece is
missing. And the typed variant is not a loophole: `Unsupported` is complete
only when "unsupported" is an accepted, documented, tested product state;
`NotYetImplemented` is an honest representation of *partial* work and never
satisfies an implementation request or gets reported as finished. Comments
explain *why*, never narrate *what* (`// increment counter`
is noise); doc comments on public items document contracts, panics
(`# Panics`), errors (`# Errors`), and safety (`# Safety`).

## 8. Tests measure behavior, not vibes

Assert the complete semantic outcome: `assert_eq!(result, expected)` —
whole-structure comparison (`pretty_assertions`, `insta` snapshots,
`expect-test`) when the full representation is the contract, targeted field
assertions when it isn't — never bare `assert!(result.is_ok())`, which
passes when the function returns the wrong answer. No tautology tests: a
test must be able to fail for a reason the implementation controls
(generated tables and platform assumptions can warrant tests even when the
expected value is statically written down; `assert_eq!(2 + 2, 4)` cannot).
`#[should_panic]` only for a *documented* panic contract, and then with
`expected = "..."` pinning the message; recoverable failures assert the
`Err`/`None` value explicitly. No mocking frameworks
by default: keep logic pure (functional core, imperative shell / sans-io) so
most tests need no doubles, and where a seam is required, write a small trait
with a hand-rolled in-memory fake. A proliferation of `#[automock]` is a
design smell, not a testing strategy. Property tests (`proptest`) for
parser-shaped and invariant-shaped code. **Never silently weaken a test or
alter it solely to accommodate the implementation.** A specified behavior
change may legitimately require updating tests — then the changed contract
and the changed assertion are surfaced explicitly as part of the change, and
a test that documents an obsolete requirement is updated, not preserved.

## 9. Private by default, concrete before generic

Every `pub` is an API commitment — for a published crate, a semver promise;
for a workspace-internal crate, still coupling that needs an intentional
owner. Items are private until a caller outside the module exists;
`pub(crate)` for contracts shared across modules *of the same crate*
(sibling workspace crates are external — sharing with them requires an
intentional `pub` API from the owning crate); a curated `pub use` facade at
the crate root where it clarifies the surface, explicit public modules where
the module boundaries themselves are the concept. Catch-all modules whose
contents share no owner, invariant, or capability are rejected; a generic
name (`utils`, `helpers`, `common`, `manager`) is the review signal that
demands that question, not a violation by itself — `test_utils` with one
clear job can be fine.
Abstractions must answer for themselves: a trait with one implementation must
justify an open boundary (a downstream extension point, a runtime `dyn`
boundary, a deterministic test seam, a platform contract) — absent one, use
the concrete type; a single-use helper must buy naming, safety, a shorter
borrow, or independent testability — not just fewer lines at the call site;
`Box<dyn Trait>` must be answering real runtime heterogeneity, not
shortening a signature. Write the concrete version first; generalize
when the second caller arrives with different needs. Exhaustive `match` on
your own enums — adding a variant should be a compile error at every site
that must care, which is the entire point of sum types.

## 10. Search before writing

Reinvented near-duplicates are the top failure of generated code in large
repos. Before adding a type, error variant, helper, or dependency: search the
workspace for the existing one. Match the surrounding crate's idioms (error
style, module layout, naming) where the alternatives are semantically
equivalent — consistency outranks this document's stylistic and
organizational preferences; it never outranks its correctness, safety,
error-causality, or lifecycle rules.

## 11. Async discipline

Every spawned task ends in exactly one of four explicit states: awaited
directly; registered with a supervisor (`JoinSet`/`TaskTracker` plus a
`CancellationToken`); aborted and joined during shutdown; or deliberately
detached through a *named* API whose semantics are documented. A dropped
`JoinHandle` is none of these — it's a task whose panics and errors vanish.
"Background task" is not a lifecycle policy: the owner defines what happens on
`Err`, on panic, on sibling failure, and in what order things stop.

Queues are bounded by default, and the capacity is tied to a named overload
policy — backpressure, rejection, coalescing, drop-oldest — stated in a
comment at the construction site. An unbounded channel converts overload into
memory growth; an arbitrary `channel(1024)` with no stated policy merely
delays the same failure.

Audit every `select!` in a loop for cancellation safety: the losing branch's
future is *dropped*, so a partially-completed `read_exact`/`write_all` loses
data; hold long-lived futures pinned outside the loop, and ask of each
important `.await` whether a dropped future is equivalent to rollback.
Abandoning a cancellation-unsafe operation is legitimate when the partial
progress is explicitly disposable (terminal shutdown); otherwise preserve
progress in an owner or state machine, or make the operation restartable.
`select! { biased; … }` makes polling-order fairness the programmer's
problem: every use must say why order is semantically required and why a
continuously-ready early branch can't starve the rest — test shutdown and
deadline branches under a permanently ready work source. A task must yield
before its uninterrupted synchronous work violates the runtime's
scheduling-latency budget — the budget comes from the workload's tail-latency
requirements (Alice Ryhl's guidance for tokio's default runtime is 10–100µs
between awaits; a generic library may have no executor at all — don't insert
arbitrary yields to satisfy a number): synchronous I/O goes to
`spawn_blocking` (itself bounded and owned — it cannot be cancelled once
running), substantial CPU work to `rayon` or a bounded pool, and loops that
never await to a dedicated thread. Don't
mark functions `async` speculatively, and don't make a library
async when a sync core with an async adapter (sans-io) serves both kinds of
caller.

## 12. Effects live at the composition root

The wall clock, environment, filesystem, process exit, global RNG, and raw
task spawning are ambient capabilities; *domain* code that reaches for them
from arbitrary modules is untestable and hides its dependencies. `main` (or
the composition root) owns process-global selection and lifecycle: it reads
and validates configuration once, constructs concrete resources, wires them,
starts supervision, and translates the final result into logging and an exit
status. Domain code below receives validated values or narrow capabilities —
an injected clock, a config struct, a task group — and never calls
`std::process::exit`, configures global logging, or reads `std::env`. But an
infrastructure *adapter* may call the ambient API it explicitly owns: a
filesystem module whose stated job is filesystem access calls `std::fs`
directly — the module boundary is the seam, and putting a `FileSystem` trait
in front of every syscall in a small binary is over-abstraction, not
hygiene. Inject clocks, RNGs, and process services when determinism,
authority, platform substitution, or fault testing requires it. Enforce
mechanically per project via `disallowed-methods` (see `assets/clippy.toml`)
— but never ban an API until a real replacement owns meaningful policy; a
wrapper that merely renames `std::fs::read` is abstraction laundering.
