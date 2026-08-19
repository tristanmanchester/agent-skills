---
name: rust-anti-slop
description: Opinionated guardrails that reject low-evidence Rust patterns — unwrap/clone/Arc<Mutex> reflexes, silent error swallowing, lint suppression, stub completion. Use when writing or reviewing Rust code, or when asked to install anti-slop lint policy (workspace lints + clippy.toml) into a Rust repository.
---

# rust-anti-slop

Rust's compiler already rejects most of what a linter must catch in other
languages. What remains — and what LLM-generated Rust reliably produces — is
code that *satisfies* the compiler by discarding the evidence it asked for:
`.unwrap()` discards fallibility, cloning past a borrow error discards the
ownership analysis, a reflexive `Arc<Mutex<T>>` discards the sharing design,
`let _ =` discards `#[must_use]`, `#[allow]` discards the diagnostic,
`todo!()` fabricates completion, and an unargued `unsafe impl Send`
fabricates thread-safety. None of these constructs is illegitimate in itself
— each is illegitimate *without its argument*. This skill demands the
argument.

Enforcement is layered:

1. **Mechanical** — `assets/workspace-lints.toml` (a `[workspace.lints]`
   table: cherry-picked clippy restriction lints plus rustc lints) and
   `assets/clippy.toml` (test exemptions, `disallowed-*` bans). No custom lint
   engine is needed; unlike TypeScript, the platform ships one.
2. **Prose** — `references/rules.md`: the rules no lint can express (clone
   justification, expect-message quality, error-type doctrine, abstraction
   discipline). Read it before writing any substantial Rust.

The escape hatch for a specific, presently known violation is
`#[expect(lint, reason = "…")]` — a suppression that states its case and
(with `unfulfilled_lint_expectations = "deny"`, included) errors the day it
stops being needed. Place it at the narrowest scope that contains the
violation: a broad (module- or crate-wide) expectation is fulfilled as long
as *any* occurrence exists, so it never expires and silently admits every
future occurrence — an open-ended exception dressed as a finite one. When an
entire scope genuinely is the unit of exception (an FFI crate and
`unsafe_code`, generated code, a configuration-dependent false positive),
use an honest *reasoned* `#![allow(lint, reason = "…")]` instead. Outer
`#[allow]` is a rejected pattern — `allow_attributes` deliberately doesn't
see inner attributes, and `allow_attributes_without_reason` still forces
the reason on both.

## Mode A: writing or reviewing Rust

1. Read `references/rules.md` in full.
2. While writing: follow it, plus whatever the mechanical config enforces if
   installed. Match established repository idioms where the alternatives are
   semantically equivalent — consistency outranks this skill's stylistic and
   organizational preferences; it never outranks correctness, safety, error
   causality, lifecycle ownership, or explicit project invariants.
3. While reviewing: order findings most severe first — fabricated evidence
   (unsafe/Send/transmute misuse) > swallowed errors > panic-as-error-handling
   > lifecycle gaps (unowned tasks, unbounded queues) > borrow-checker
   appeasement > structure/abstraction. Every finding must state: the exact
   symbols involved; **which evidence the code discards** (validity,
   ownership, failure causality, lifecycle, safety, exhaustiveness); the
   **concrete failure mode** it enables — not "unidiomatic"; the **smallest
   repair** (prefer deleting or simplifying ownership over adding
   abstraction); how to **prevent recurrence** (a lint, a `disallowed-*`
   entry, a test); and what was inferred rather than proven. Raise no finding
   merely because a function is long, a clone or mutex or `dyn` exists, or a
   trait has one implementation — connect the smell to a failure, or drop it.
4. Never "fix" a finding by erasing its evidence: no unreasoned suppression;
   no error erasure unless erasure is the intentional, documented contract of
   that boundary; no clone whose sole purpose is ending an inconvenient
   borrow; no silent weakening of a behavioral assertion.

## Mode B: installing the lint policy into a repository

1. Inspect before changing: read the repo's agent instructions; check
   `git status` and preserve unrelated changes; find the workspace root
   `Cargo.toml`, any existing `clippy.toml`/`.clippy.toml`, existing
   `[lints]`/`[workspace.lints]` tables, and `#![allow(...)]`/`#![warn(...)]`
   crate attributes that the table will supersede.
2. Merge `assets/workspace-lints.toml` into the workspace root `Cargo.toml`.
   Keep every existing lint entry; on conflict, keep the repo's stricter
   level and report the difference. In a single-crate repo without a
   workspace, use `[lints.rust]`/`[lints.clippy]` directly. Normalize
   priorities: this table is all named lints, but if the repo's existing
   table contains *group* entries (`pedantic = "warn"`, `nursery = …`),
   those must sit at a lower priority than the named lints that override
   them — rewrite them as `{ level = "…", priority = -1 }`, never rely on
   TOML entry order (same-priority group-vs-lint resolution is undefined;
   `clippy::lint_groups_priority` flags it). Preserve deliberate existing
   priorities and report any conflict.
3. Opt members into the workspace table, case by case (skip in single-crate
   repos). A member with no `[lints]` table gets `[lints] workspace = true`.
   A member with existing local lint entries CANNOT combine them with
   `workspace = true` — Cargo rejects that manifest; either migrate its
   entries into the workspace table (if they're general) or leave the crate
   on local lints and merge the anti-slop entries into them, reporting which.
   A special-profile crate (FFI, no_std, codegen) may stay opted out with a
   stated reason.
4. Merge `assets/clippy.toml` into the repo's `clippy.toml`, preserving
   existing `disallowed-*` entries and config keys.
5. Propose architectural bans — often the highest-value step. From the repo's
   own structure, identify APIs that should only be reachable through a
   project-owned seam (unbounded channels, raw `tokio::spawn`, wall clock,
   `std::env`, `process::exit`, raw fs access, `println!` in non-CLI crates)
   and activate the corresponding `disallowed-methods` templates in
   `clippy.toml` — but only where a real replacement already exists and owns
   actual policy (bounds, supervision, injection, context). Never ban an API
   whose "replacement" merely renames it; list the candidates without a
   replacement as recommendations instead.
6. Validate against the repo's pinned toolchain: run
   `cargo clippy --workspace --all-targets` and confirm no
   `unknown lint` / `removed lint` / config-parse warnings. Lint names drift
   across clippy versions; drop or rename entries that this toolchain
   rejects and report each one.
7. If findings appear in existing code, report counts per lint. Fix them only
   if the user asked for a cleanup; fix real causes, never launder (step 4 of
   Mode A). If the volume is large, propose demoting specific deny entries to
   `warn` as a migration step rather than sprinkling suppressions.
8. For CI, recommend: `cargo fmt --all --check`, then
   `cargo clippy --workspace --all-targets` over the repository's *existing*
   feature matrix (do not impose `--all-features` — projects with mutually
   exclusive features have their own combination strategy). Do NOT append
   `-D warnings`: it would promote the deliberately-advisory warn tier (and
   every default rustc/clippy warning) to failures, erasing the deny/warn
   distinction this policy encodes — the deny tier already fails the build
   on its own. A team that wants the warn tier enforced should promote
   specific lints to `deny` in the table, where the choice is explicit and
   versioned. Add `cargo-deny` and `cargo-machete` if supply-chain and
   dependency hygiene are wanted.
9. Report: files changed, lints enabled at which levels, entries dropped for
   toolchain compatibility, findings remaining.

## Tuning expectations

The deny tier is meant to survive contact with real projects; the warn tier
includes nursery lints (`redundant_clone`, `needless_collect`,
`significant_drop_tightening`) that are known to have false positives and
negatives — they are tripwires backing the prose rules, not the policy itself.
`indexing_slicing` and `wildcard_enum_match_arm` are the most contested
entries: keep them for application code, expect pushback in parser/math-heavy
crates, and demote there with a stated reason rather than repo-wide. This
profile is deliberately orthogonal to style — it can coexist with or without
`clippy::pedantic`; add pedantic separately if the team wants taste enforced,
and never enable `clippy::restriction` as a group.

Toolchain floor: the full policy requires Rust 1.82+ (`[lints]` table 1.74+,
`#[expect]`/`reason` 1.81+, `unused_result_ok` 1.82+). Below that, run in
compatibility mode: omit unsupported entries and substitute reasoned
`#[allow]` where `#[expect]` is unavailable — and say so in the report, since
the self-expiring suppression model is the part that changes.

Per-crate escalations, applied as guidance rather than shipped as separate
profiles: public libraries add `missing_errors_doc = "warn"`,
`missing_panics_doc = "warn"` (failure modes are part of the contract) and
keep `avoid-breaking-exported-api = true`; internal applications may set it
to `false` in `clippy.toml` for full API-shape coverage. Safety-critical or
no-panic crates escalate `panic`, `indexing_slicing`, `string_slice`, and
even `expect_used` to `deny` — a level that would be overkill as the default.

The last test for every rule, mechanical or prose: could following it cause
an agent to replace a correct, explicit design with a more abstract or more
complicated one solely to satisfy the wording? Where the answer is yes, the
rule's job is to demand the design's argument — not to prescribe a syntax or
an architecture.
