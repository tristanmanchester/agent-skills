# TypeScript

Use the project's compiler settings, linter and test runner. Good defaults for a new
project that will be maintained: `strict`, `noUncheckedIndexedAccess`,
`exactOptionalPropertyTypes`, `noImplicitOverride`; typescript-eslint with type-aware
rules; Vitest; dependency-cruiser once boundaries matter.

## External data is `unknown` until parsed

`as`, `!`, generics on `fetch<T>()` and `JSON.parse(...) as T` validate nothing. Parse
with Zod, Valibot or the project's schema library at the boundary, and derive the type
from the schema so the two can't drift:

```ts
const Note = z.object({
  id: z.string().brand<"NoteId">(),
  title: z.string().min(1),
  updatedAt: z.coerce.date(),
});
type Note = z.infer<typeof Note>;

const note = Note.parse(await res.json()); // throws with a path to the bad field
```

This applies to API responses, `localStorage`, URL params, env vars, `postMessage` and
messages from workers.

## States are discriminated unions

```ts
type Upload =
  | { kind: "pending"; file: File }
  | { kind: "sending"; file: File; attempt: number }
  | { kind: "done"; remoteId: RemoteId }
  | { kind: "failed"; file: File; error: UploadError };

function label(u: Upload): string {
  switch (u.kind) {
    case "pending": return "Waiting";
    case "sending": return `Sending (try ${u.attempt})`;
    case "done": return "Uploaded";
    case "failed": return u.error.message;
    default: return u satisfies never; // adding a variant breaks the build here
  }
}
```

- Prefer string-literal unions and `as const` objects to `enum`.
- Brand identifiers (`NoteId`, `UserId`) so they can't be swapped.
- `readonly` and `Readonly<T>` are compile-time and shallow.

## Promises have owners

- Turn on `@typescript-eslint/no-floating-promises` and `no-misused-promises`. Every
  promise is awaited, returned or explicitly handled. `void promise` silences the
  lint, not the failure: the rejection still crashes Node as an unhandled rejection.
- Pass an `AbortSignal` through every cancellable operation (`fetch`, your own async
  functions), and check a request id when applying the result. Aborting does not
  cancel work already finished.
- `Promise.all` rejects on the first failure and leaves the others running. Use
  `Promise.allSettled` when every result matters.

## Absence

Model `undefined`, `null`, `0`, `""` and a missing key on purpose. `value || default`
replaces `0` and `""`; use `??`. With `exactOptionalPropertyTypes`, `{ x?: number }`
means "absent", not "present and undefined".

## Errors

- Throw `Error` subclasses (or return a typed result) carrying `cause`:
  `throw new SyncError("upload failed", { cause: e })`.
- `catch (e)` gives `unknown`; narrow it before use.
- Pick one error style per layer: throwing in application code, or result types in a
  core library. Don't mix both in the same layer.

## Modules

- Barrel files (`index.ts` re-exporting everything) slow builds and drag server code
  into client bundles. Export a package's public surface deliberately, with
  `package.json` `"exports"` in workspaces.
- `paths` aliases change type resolution only; keep the bundler, runtime and test
  config in step.
- No side effects at import time.

## Types stay proportional

Prefer plain types and functions. Reach for conditional types, deep generics and
type-level programming only when they stop a real class of caller error. A type
nobody can read is worse than a runtime check.

## Tests

- Vitest or the project's runner. Use `msw` to stub HTTP at the network layer, not by
  mocking your own client.
- Use fast-check for parsers and pure logic with real properties.
- Use fake timers (`vi.useFakeTimers()`) for time, never real waits.
