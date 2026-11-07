# Enforcing boundaries

Contents: procedure · TypeScript/JavaScript · Python · Rust · Swift · Go ·
Kotlin/Java · guarding the public surface and the debt

A boundary exists when a tool rejects code that crosses it. Folder names, leading
underscores, `__all__`, barrel files and path aliases are conventions. They tell
people where the boundary is, but nothing stops code from crossing it.

## Procedure

1. Write down the rule in one sentence: "Nothing outside `billing/` imports
   `billing/internal`", or "`core` imports nothing above it".
2. Pick the tool that resolves imports the way the build does (below).
3. Add **two fixtures**: an allowed import (the module using its own internals, or a
   consumer using the public entry) and a forbidden one (a foreign module reaching into
   internals). Run the check and see the forbidden one fail and the allowed one pass.
   A rule with no failing fixture can silently match nothing. A rule with no passing
   fixture can ban the module's own implementation.
4. Write the error message as a fix: `Import from "@/billing" instead; billing/internal
   is private to billing.` Agents read it and correct themselves.
5. Wire the check into the project's single check command and CI.

Cover every way the language can spell an import that your codebase uses: relative
paths, aliases, re-exports, type-only imports, dynamic `import()` or
`importlib`, and generated code.

## TypeScript / JavaScript

Use **dependency-cruiser** for real resolution (it follows `tsconfig` paths, aliases
and re-exports):

```js
// .dependency-cruiser.cjs
module.exports = {
  forbidden: [
    {
      name: "billing-internals-private",
      comment: "Import from '@/billing' instead; billing/internal is private to billing.",
      severity: "error",
      from: { pathNot: "^src/billing/" },
      to: { path: "^src/billing/internal/" },
    },
    { name: "no-cycles", severity: "error", from: {}, to: { circular: true } },
  ],
  options: {
    tsConfig: { fileName: "tsconfig.json" },
    tsPreCompilationDeps: true, // also see `import type` edges
    doNotFollow: { path: "node_modules" },
  },
};
```

For a lightweight rule in an existing ESLint flat config, `no-restricted-imports`
matches import *strings*, not resolved paths, so it misses relative spellings:

```js
// eslint.config.mjs (fragment)
{
  files: ["src/**/*.{ts,tsx}"],
  ignores: ["src/billing/**"],
  rules: {
    "no-restricted-imports": ["error", { patterns: [{
      group: ["@/billing/internal", "@/billing/internal/**", "**/billing/internal/**"],
      message: "Import from '@/billing' instead; billing/internal is private to billing.",
    }] }],
  },
}
```

- `package.json` `"exports"` defines the entry points a workspace package offers. It
  is the strongest boundary in a monorepo: normal package-subpath imports of anything
  not exported fail. It is not encapsulation against a deliberate absolute-path import,
  and it is not a security boundary.
  TypeScript honours it only with `moduleResolution` set to `bundler`, `node16` or
  `nodenext`.
- `tsconfig` `paths` changes type resolution only. It does not rewrite emitted imports,
  so bundler, runtime and test runner need matching aliases.
- Keep server-only code out of client bundles with the `server-only` package or the
  framework's equivalent, and never with a naming convention.

## Python

Use **import-linter** with contracts in `.importlinter` or `pyproject.toml`:

```ini
[importlinter]
root_package = myapp

[importlinter:contract:layers]
name = Layer direction
type = layers
layers =
    myapp.cli
    myapp.workflows
    myapp.domain
    myapp.core

[importlinter:contract:alignment-facade]
name = CLI uses the alignment facade, not its internals
type = forbidden
source_modules = myapp.cli
forbidden_modules = myapp.alignment._model
```

`layers` stops lower layers importing higher ones. `forbidden` blocks specific edges.
`independence` keeps sibling packages apart. Leading underscores and `__all__` are
conventions only; `import myapp.alignment._model` works regardless.

## Rust

Visibility is enforced by the compiler, so use it:

- Keep fields private and use `pub(crate)` and `pub(super)` for internals. Don't make
  everything `pub` so tests can reach it: unit tests in a child `mod tests` already
  see private items.
- **Workspace crates are hard boundaries.** A crate can only use what another crate
  exports, and `Cargo.toml` dependencies make the dependency graph explicit and acyclic.
  Split a crate when you need a dependency direction enforced.
- Mark public enums and structs `#[non_exhaustive]` when downstream crates must not
  match exhaustively or construct them with literals.
- Run `cargo public-api` or `cargo semver-checks` to snapshot a library's public
  surface and catch unintended changes.

## Swift

- **Swift packages are the boundary.** Each target is a module. `internal` (the default)
  hides a declaration from other modules; `package` shares it within the package;
  `public` exports it. Split features into SPM targets to enforce direction. Xcode
  groups enforce nothing.
- Use `@testable import` only in the module's own tests. Test other modules through
  their `public` API.
- Target dependencies in `Package.swift` define the allowed graph; a target can only
  import what it declares.

## Go

An `internal/` directory restricts importers to the tree rooted at `internal`'s parent.
Place it at the boundary you mean. Use `go list -deps` checks or depguard for rules
between sibling packages.

## Kotlin and Java

Java package-private is per exact package: `auth` and `auth.internal` can't see each
other's package-private members. Kotlin `internal` is per Gradle module. Use Gradle
modules as the real boundary and ArchUnit or Konsist for layer rules.

## Guard the public surface and the debt

Add these once a public API exists, or once more than one agent lands changes
regularly. Two cheap structural tests then keep the codebase from drifting:

- **API surface snapshot.** Generate a sorted list of exported names and signatures and
  commit it (`api_surface.txt`). A test fails when the surface changes, so every
  addition shows up in review. Update the file in the same commit as an intended change.
- **Ratchets on specific debt you are paying down.** Count something you have decided
  to eliminate, such as `any` uses, lint suppressions or env-var reads outside config,
  and fail if the count rises. Don't build a basket of proxy metrics (file length,
  complexity scores, config fields): agents will split, rename and shuffle code to
  satisfy them without making it better. Never raise a ratchet just to get a change
  through.
