# Agent readiness

Agents build most software now. A codebase is ready when a fresh agent, with only the
repository and its tools, can find the right code, run it, change it, check the change
and diagnose failures, without a human filling gaps. Whatever the agent can't see
from the repo or its tools doesn't exist for it.

Contents: the six capabilities · new project setup · AGENTS.md · legibility ·
keeping entropy down · auditing readiness

When an agent struggles, ask what capability is missing, then build that capability
into the repo. Another paragraph of instructions is the last resort. Turn
repeated mistakes into checks.

## The six capabilities

| Capability | Ready looks like |
| --- | --- |
| **Find** | Names match the domain. Each behaviour has one obvious owner. A short `AGENTS.md` points to entry points and deeper docs. Generated code is marked and says how to regenerate it. |
| **Understand** | States, invariants and effects are explicit in types and owners. Non-obvious constraints are written down next to the code or in `AGENTS.md`. |
| **Run** | One command sets up from a clean checkout. One command runs the app or CLI. Seed data and fixtures reproduce realistic states. |
| **Check** | One command runs format, lint, typecheck and tests; a faster one covers the inner loop. Failures say what broke and how to fix it. |
| **Diagnose** | Errors name the operation, the input and the cause. Logs are structured and readable from the terminal. The agent can inspect the database, UI, simulator or GPU state it needs. |
| **Work in parallel** | Each worktree can run its own instance with its own port, database and cache, so two agents never collide. |

## Set up a new project

Every project needs a repeatable way to run it and check it. How much more to add depends
on how long the code will live and how many agents will work in it. A throwaway script
needs to run. A library or app that will be maintained benefits from these early,
because they are cheap at the start and expensive to retrofit:

- **A pinned toolchain**: `.python-version` + `uv.lock`, `.nvmrc` + lockfile,
  `rust-toolchain.toml`, the Xcode version in the README.
- **Strictness from the start**: pyright/mypy strict, `"strict": true` with
  `noUncheckedIndexedAccess`, `clippy -D warnings`, Swift 6 language mode. Turning
  these on later means a migration.
- **One command that checks everything** (`just check`, `make check`, `pnpm check`),
  plus `setup` and `dev` if they aren't obvious.
- **A short `AGENTS.md`**: a map, not a manual (see below).
- **Boundary checks** from [boundaries](boundaries.md) once a dependency rule matters
  enough that breaking it would hurt, or keeps getting broken.

## AGENTS.md

Keep it under about 80 lines. Every line should change what an agent does. Include:

- What the project is and what "good" means for it, in two or three sentences.
- **Constraints an agent would get wrong by default**, stated flatly. These are the
  most valuable lines.
- The commands: setup, run, check, CI, and how long each takes.
- What "ready to hand off" means here.
- Pointers to deeper docs, each with when to read it: "Read `docs/sync.md` before
  touching anything under `sync/`."

Leave out: directory listings, generic best practice, anything the code already shows,
and history. Measured studies find that repository overviews add cost without improving
results. Non-obvious constraints are what help.

A good example of the constraint section:

```md
## Constraints
- The backprojector stays the exact transpose of the forward projector.
- Breaking changes are fine before 1.0; no compatibility shims.
- A faster or lower-residual result only counts once reconstruction error is checked too.
- Real data is within a few orders of magnitude of 1; don't engineer for 1e-30 or 1e30.
- Fix a method that gets a case wrong; don't detect the case and bypass it.
```

## Make the system legible

- **Errors carry context**: the operation, the identifiers involved, the state and the
  cause chain. Never include secrets.
- **Custom lint and check messages contain the fix.** "Use `notes.save()`; direct
  writes to `notes` skip the sync outbox" teaches the agent at the moment it errs.
- **Expose runtime state to the agent**: a CLI or script to dump the relevant
  database rows, queue contents or app state; logs in a file it can read; screenshots
  and accessibility snapshots for UI; deterministic fixtures for each hard state.
- **Prefer boring, well-known dependencies** whose behaviour agents can predict. When a
  library's behaviour is opaque and the needed subset is small, a short in-repo
  implementation with tests can be easier to reason about.
- **Plans and decisions live in the repo** when work spans sessions: a checked-in plan
  with progress, decisions and open questions. Delete it when the work lands; the
  code and commit history are the record.

## Keep entropy down continuously

Agents copy whatever patterns exist, including bad ones. Encode the "golden rules" as
checks (API-surface snapshot, ratchets, import contracts, banned patterns with
fix-it messages) and clean up drift in small, regular passes, not quarterly rewrites.

## Auditing readiness

Grade each capability by the strongest evidence you have:

1. **Documented**: a doc claims it.
2. **Configured**: the config or script exists.
3. **Executed**: you ran it and it worked.
4. **Challenged**: you broke something and it caught the break.
5. **Demonstrated**: a fresh agent completed a real task with it.

A test command in CI YAML is "configured". The suite passing is "executed". The suite
failing on an injected bug is "challenged". Report blockers (the app doesn't start,
the check command runs zero tests) above everything else, and never average them away.

The best readiness test is direct: give a fresh agent, with no conversation context,
a real task from the backlog. Watch where it stalls (finding the owner, starting the
app, choosing which tests to run, understanding a failure) and fix that capability.
Include a task where the right answer is a small change, to check the agent knows when
to stop.
