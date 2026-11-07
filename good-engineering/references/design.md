# Design: modules, seams and coupling

Contents: find the real cost · coupling and special cases · shape a deep module ·
classify dependencies · dependency direction · design it twice · refactor procedure ·
decision log · comments

**Depth** is the behaviour a caller gets per unit of interface they must learn.
Shallow means the interface is nearly as complex as the implementation. A **seam** is
where one module's interface meets its callers; where it goes is a design decision of
its own.

## Find the real cost first

Start from a concrete change, not from the folder tree. Trace one representative
operation from a real caller through policy, state and effects, and ask:

1. What must a maintainer remember to update somewhere else?
2. Which unrelated changes force edits here?
3. Which code has no reason of its own to change?

`git log --name-only` shows which files change together. Use it to find hot spots
and hidden links, then confirm each one in the code.

## Coupling and special cases

SKILL.md defines hidden links, needless links and surplus. Forms that are easy to miss:

- A module that reads a global, file or env var another module sets (hidden link).
- One feature split across folders by layer, so every change touches all of them
  (hidden link).
- A general function with a parameter only one workflow understands (needless link).
- A shallow module whose interface changes whenever its internals do (needless link).

**Special cases are symptoms.** An `if` for one value, a parameter for one caller, a
swallowed exception, a retry or sleep, a disabled test: each marks a requirement the
design never absorbed. Find the one design change that makes several of them
unnecessary, rather than patching them one by one.

## Shape a deep module

Run these three exercises on any boundary you create or change:

1. **Write the caller.** Write a real caller, including its failure handling. If it must
   know internal ordering, storage layout, lock or transaction rules, or which
   internal error type means what, the interface is leaking.
2. **Change the inside.** Imagine swapping the storage, algorithm or retry policy. If
   callers have to change, the interface exposes a decision it should hide.
3. **Trace a failure.** From the caller's side, can you tell which operation failed,
   whether anything was committed, and whether a retry is safe? Deep does not mean
   opaque.

Then apply the **deletion test**. If removing the module makes complexity vanish, it
was a pass-through: remove it. If complexity reappears across callers, it earns its
place.

**One implementation can justify a module or a seam.** A module that owns an
invariant, a transaction, a resource lifetime or a platform API earns its place with a
single implementation. The same goes for an abstract interface that isolates authority,
lifetime or a difficult dependency. What doesn't earn a seam is speculation: an
interface added because something *might* vary one day, or only so a test can mock it.

**Pure inside, effects at the edge.** Pull pure calculation into functions that take
values and return values. Do not push the orchestration onto every caller to make the
inner part pure: the module still owns its effects and their order.

**Expose capabilities, not a manager.** `notes.save`, `notes.archive` and `notes.search`
beat a `NotesManager.execute(action, mode, options)`. Several deliberate entry points
are fine: a server entry and a client entry, a cheap import and a heavy lazy one, a
public API and an `.api` module for expert users.

**Options are keyword-only and few.** A call takes the one or two arguments it is about,
then named options (`reconstruct(scan, "cgls", iterations=50)`). No positional
booleans.

## Classify dependencies before you deepen

The category decides how you test the module once it is deeper.

| Dependency | Example | How to test across it |
| --- | --- | --- |
| In-process | Pure computation, in-memory state | Merge freely; test through the new interface |
| Local stand-in exists | SQLite, PGlite, a temp directory | Run the real stand-in in tests; no port needed |
| Remote but owned | Your own HTTP or queue service | Port at the seam; HTTP adapter in production, in-memory adapter in tests |
| True external | Stripe, APNs, an LLM API | Port at the seam; fake adapter in tests; a small contract test against the real one |

## Dependency direction

- Point dependencies from volatile code to stable code: UI → application → domain → core types.
- A direct, acyclic call through another module's public interface is the simplest
  link. Use it.
- Invert a dependency (accept a port) when the stable side must not know the volatile
  side, or when you need a second adapter.
- Use events when the publisher really must not wait for or know its consumers. Events
  bring delivery, ordering, duplicate and debugging obligations; they hide coupling
  rather than remove it.
- Shared code is for things that are genuinely shared. It is not where disputed types go.

## Design it twice

For an interface that will be expensive to change (a public API, a persistence
format, a module many callers will use), sketch two or three different shapes before
building one: the smallest possible interface, one optimised for the most common
caller, and one built around ports. For each, write the caller code and list what the
implementation hides. Pick one and say why. Routine changes don't need this.

## Refactor procedure

1. Pin behaviour with tests at the interface you are keeping. Add them first if they
   are missing.
2. Make the structural change in one coherent pass: the interface, the implementation,
   every caller, and the dependency rules.
3. Replace tests rather than layering them. Delete tests of the removed shallow
   pieces once the interface tests cover the same behaviour. Keep focused tests of
   hard internals (numerics, parsers, concurrency); they diagnose failures faster.
4. Delete the old path. No re-export aliases, no `legacy/` folder.
5. Confirm behaviour is unchanged, apart from bugs the refactor deliberately fixed.

## Decision log

For any multi-step redesign, write the problems first, then group them under the fix
that removes them. Keep it in the PR, or as a checked-in plan file when the work spans
sessions. Delete it when the work lands.

```md
- Make every user action a command with a name, a handler and an undo, so toolbar,
  menu, shortcuts, palette and undo history run from one list.
  - `ui/Toolbar.tsx:40` and `ui/Menu.tsx:22` each check when actions are disabled.
  - `shortcuts/keymap.ts:18` switches over actions separately from the menu list.
  - `ui/CommandPalette.tsx:55` keeps its own list and misses the newer actions.
  - Every handler calls `track()` by hand, and some forget.
- Make `Dialog` restore focus to whatever had it before opening, so the wait and the
  global flag both go.
  - `ui/LogoutDialog.tsx:30` waits 100 ms and hopes the input can take focus.
  - `ui/SettingsDialog.tsx:61` sets a global `skipRefocus` flag.
```

## Comments

Comment what the code cannot show: a constraint from outside the code ("the proxy
drops websockets, so we poll"), a non-obvious invariant, the reason a simpler
approach fails. Delete comments that restate the code. A comment explaining a
workaround goes away with the workaround.
