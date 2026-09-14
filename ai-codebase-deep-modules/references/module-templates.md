# Module sketches, not mandates

A deep module hides useful complexity behind a clear contract. Directory depth,
export counts, and a universal Result type do not establish that property.
Choose types/functions/classes and error semantics that fit the existing language
and consumer expectations; a blanket ban on exceptions is not required.

## TypeScript

A possible source layout is:

```text
src/auth/
  index.ts              public operations/types, when a facade fits loading semantics
  types.ts              public data contract
  internal/             implementation owned by auth
  auth.contract.test.ts behaviour through the public interface
```

Keep server/client code and expensive imports separated when the framework requires
it. Public error categories should be actionable and preserve appropriate cause
context; don't leak internal messages, passwords, or tokens merely to be explicit.
A generic not-implemented function and a test of that stub are scaffolding only,
not a feature or verified contract.

## Python

__init__.py can expose the intended interface, while implementation lives in
private-named or internal modules. __all__ controls star-import behaviour, not
access control. Keep import side effects, packaging layout, and test imports correct
for the real project. A module does not need several wrappers just because this
sketch has multiple files.

## Go

Choose packages around ownership and cohesive operations. internal restricts
imports relative to its parent tree; place it deliberately. Use an external test
package when testing the consumer-facing API is useful, plus internal tests for
important algorithms. Do not invent service interfaces before there is a concrete
substitution or dependency-direction need.

## JVM

Use Java package-private collaborators in the same exact package as their facade,
or design explicit module exports/architecture rules for a multi-package module.
A child package does not inherit access to its parent's package-private members,
or vice versa. Kotlin visibility follows its own module rules. Verify the actual
compiler and build rather than copying a Java layout into Kotlin mechanically.

## Contract worksheet

For a proposed seam, record the consumer's job, operations, validated inputs,
outputs/errors, invariants, state ownership, side effects, resource lifetime,
permitted dependencies, and tests. Fill only the parts relevant to the task.
Keep an implementation detail private because callers should not depend on it,
not because the folder name claims privacy.

The former automatic scaffold is removed; implement a real slice through the
normal patch workflow and verify actual consumers. See boundary-enforcement.md
for source-backed language and linter distinctions.
