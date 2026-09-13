---
name: ai-codebase-deep-modules
description: >-
  Design or refactor cohesive modules with small, useful public contracts and
  enforceable dependency boundaries. Use for concrete architecture, coupling,
  refactoring, or agent-editability problems. Do not restructure a working
  codebase merely because an AI agent will edit it.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# Deep modules and fast feedback

Hide meaningful complexity behind a contract that lets callers do useful work.
The objective is lower cognitive/change cost with preserved behaviour, not more
folders, a prescribed export count, or an abstraction around every function.
Agent productivity is a hypothesis to measure, not a benefit proved by the tree shape.

## Inspect a real change path

Start from the task and trace the relevant entry point through domain policy,
state/data ownership, side effects, callers, and tests. Read actual dependencies,
not only README architecture. Identify which information callers must know and
which coordinated edits recur. A large file can be cohesive; a tiny wrapper can
leak a complicated protocol. Do not equate lines of code with module depth.

State the behaviour to preserve, the specific coupling or duplication to remove,
and the smallest proposed seam. For a review, deliver actionable findings. For an
implementation request, make the coherent patch and tests; do not stop at a
mandatory nine-section architecture plan. Use the existing plan asset only when
a substantial design decision needs it.

## Design the contract around ownership

Define operations, input/output types, errors, state transitions, resource ownership,
lifetime, authority, and concurrency/cancellation semantics. Keep invariants with
the module that owns them. Separate validation at an external boundary from already-
validated internal values without duplicating defensive checks everywhere.

Expose domain operations rather than a bag of internals or a universal manager.
A public entry point can be a useful convention, but several intentional surfaces
may better fit types, platform adapters, lazy loading, or server/client boundaries.
Avoid a giant root barrel that changes import side effects or bundles server-only
code into a client. Preserve the language/framework's actual loading contract.

Draw an explicit dependency direction. A direct acyclic dependency through another
domain's public contract can be simpler than a new event bus. Use inversion when
the dependency/ownership problem calls for it, and events when temporal decoupling
is actually useful. Events add delivery, ordering, idempotency, and observability
obligations; they do not make coupling disappear. Keep shared code genuinely shared,
not the destination for every disputed type.

## Enforce and test the seam

Read [boundary enforcement](references/boundary-enforcement.md) before writing a
lint rule. A rule must distinguish a module using its own internals from a foreign
consumer crossing that boundary. Test allowed and forbidden imports through every
supported spelling/resolver. Filenames, __all__, and grep are conventions/signals,
not universal privacy or security mechanisms.

Create behavioural tests at the public boundary, including meaningful failure,
empty/boundary data, state/restart, cancellation, and concurrency cases where
applicable. Retain focused internal tests when they diagnose important algorithms.
Mocks of the implementation's own call sequence do not prove its contract; a test
that the stub returns not-implemented does not implement the domain behaviour.

Use the fastest relevant test/lint/typecheck first, then the actual build/integration
path touched by the refactor. Measure feedback cost and correctness, not a fixed
quota of mocks or files. Read [testing and feedback](references/testing-and-feedback.md)
for a deeper checklist, adapting it to the project's tooling and risks.

## Refactor as one coherent change

Use the existing [module examples](references/module-templates.md) as sketches,
not scaffolding to install unchanged. Update the interface, implementation,
consumers, dependency rules, and tests together. Do not create compatibility aliases,
dead wrappers, speculative exports, or a second implementation when no consumer
contract requires them. A destructive data/schema transition still needs an explicit
rollout/recovery plan; removing source compatibility is not permission to lose data.

The old scaffold_deep_module.py is removed. It interpolated unchecked names into
paths/source, skipped existing files while reporting them as created, and generated
placeholder APIs/tests rather than a useful domain contract. Create the actual
requested files through the normal reviewed patch workflow. No replacement CLI
is needed to make four empty files.

## Deliver evidence

Explain the seam, what it hides, dependencies it permits, and why it reduces the
specific change burden. Report tests actually run and unresolved integration risks.
Do not claim architecture enforcement because one import example fails, or that
agent speed improved without a comparative task measurement. Keep project-specific
assumptions explicit and avoid a blanket clean-architecture rewrite.

References are relative to this installed skill, not target-project folders.
Authoring baseline reviewed 2026-09-13: https://agentskills.io/specification.
Current language/linter sources are recorded in the boundary reference.
