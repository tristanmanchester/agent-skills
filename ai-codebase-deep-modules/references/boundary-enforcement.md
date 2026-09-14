# Enforce real dependency boundaries

First define ownership and permitted dependencies. Then choose enforcement that
matches the language, resolver, and build. Prevent foreign access to implementation
details without blocking a module's own facade or internal collaborations.

## JavaScript and TypeScript

Current ESLint uses flat configuration. Add a narrowly scoped rule to the existing
config rather than replacing it with an obsolete .eslintrc.js. For example, an
alias-based rule for a particular external consumer region could be:

```js
// A fragment for the existing eslint.config.mjs, not a complete TS configuration.
export default [{
  files: ['src/billing/**/*.{js,jsx,mjs,cjs,ts,tsx,mts,cts}'],
  rules: {
    'no-restricted-imports': ['error', {
      patterns: [{ group: ['@/auth/internal', '@/auth/internal/**'],
        message: 'Use the public auth contract from billing.' }],
    }],
  },
}];
```

Derive the file patterns from the repository's actual extensions and generated-file
policy. This example covers JS/TS module and JSX/TSX extensions; configure the
appropriate parser for each, and test a prohibited static import in every matched
extension plus an allowed public import. File matching does not add parsing support.

This does not block auth's own internal imports. It also does **not** resolve every
relative-path/alias spelling or dynamic import. The core rule covers static imports
and relevant re-exports, not all require()/import() calls. For stronger guarantees,
use an appropriate resolver-aware dependency rule/check and test the project's
actual syntax, including type-only imports, re-exports, aliases, and generated code.
Do not call a grep match a resolved dependency graph.

TypeScript paths affects type/module resolution; it does not rewrite emitted
imports. Keep runtime/bundler/test resolution consistent and avoid unnecessary
baseUrl configuration. An alias is ergonomic naming, not a privacy boundary.
Workspace package exports can define supported consumer entry points; do not claim
those boundaries protect secrets from code running in the same trusted process.

Sources reviewed 2026-09-13:
- https://eslint.org/docs/latest/use/configure/configuration-files
- https://eslint.org/docs/latest/rules/no-restricted-imports
- https://www.typescriptlang.org/tsconfig/paths.html

## Python

A package facade and __all__ document an intended public interface; they do not
prevent explicit imports of internal modules. Packaging a distribution also does
not automatically hide its installed implementation. Use the actual project's
import-linter or architecture-test contract, accounting for relative imports,
plugins, dynamic imports, and test-only exceptions. A lightweight AST/grep check
is useful only with its stated limitations and positive/negative fixtures.

Source: https://docs.python.org/3/tutorial/modules.html#packages

## Go

An internal directory restricts imports to code within its parent tree, as defined
by the Go toolchain. It does not prohibit every sibling domain dependency when
those siblings fall within that permitted parent. Place internal at the boundary
you intend, and use package dependency checks for additional architecture rules.

Source: https://pkg.go.dev/cmd/go#hdr-Internal_Directories

## Java and Kotlin

Java package-private visibility applies to the exact package, not a hierarchy.
com.acme.auth and com.acme.auth.internal are different packages; a package-private
class in the latter is not accessible to a facade in the former. Keep collaborating
package-private types together or use a deliberate module/public bridge and an
architecture rule. Do not widen every implementation type publicly just to match
a folder sketch. Kotlin internal is module visibility, not Java package-private;
use the actual build/module boundary and account for tests/friend modules.

Source: https://docs.oracle.com/javase/specs/jls/se25/html/jls-6.html#jls-6.6.1
Check the installed Kotlin/compiler/build contract when applying the Kotlin case.

## Acceptance tests

Include an allowed own-internal import; forbidden foreign-internal import;
allowed public cross-domain dependency; forbidden cycle; relative and alias forms;
type-only/re-export forms; dynamic/plugin paths; test-only exception; and an actual
runtime build resolving the approved imports. Scope exceptions narrowly and explain
why they exist. A boundary rule without negative fixtures can silently do nothing;
a global ban without positive fixtures can forbid the architecture it describes.
