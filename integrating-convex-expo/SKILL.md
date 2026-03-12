---
name: integrating-convex-expo
description: >-
  Use this skill when working on an Expo or React Native app that uses, adds, debugs, or migrates to Convex. It covers `npx convex dev`, `EXPO_PUBLIC_CONVEX_URL` and EAS envs, `ConvexReactClient` and provider wiring in `expo-router` or `App.tsx`, generated `api` imports, schema and index design, queries, mutations, actions, auth (Clerk, Convex Auth, JWT or OIDC), file uploads from Expo URIs, pagination, migrations, and common `useQuery` or `_generated` failures. Do not use it for generic Expo UI or navigation work, or for non-Expo Convex frontends unless the task is specifically about adapting them to this mobile stack.
compatibility: >-
  Designed for coding-agent environments that can inspect and edit an Expo project, run shell commands such as npx and python, and optionally use the internet for current Convex and Expo documentation.
metadata:
  version: "2.0.0"
  domain: "expo-react-native-convex"
  keywords: "convex expo react-native expo-router eas clerk convex-auth migrations uploads"
---

# Integrating Convex with Expo (React Native)

Use this skill to add, repair, extend, or harden a Convex backend for an Expo app without drifting into web-only patterns or generic React Native advice.

## Use this skill for

- Adding Convex to an existing Expo or Expo Router app.
- Fixing broken environment setup, provider wiring, or generated API imports.
- Building an end-to-end feature slice: schema, indexes, backend functions, frontend hooks, and validation.
- Choosing and implementing auth for Expo + Convex.
- Uploading files from Expo URIs into Convex storage.
- Refactoring for pagination, indexes, migrations, or reusable components.
- Hardening a project before preview or production release.

## Do not use this skill for

- Pure Expo UI, animation, navigation, or styling work with no Convex involvement.
- Convex projects whose frontend is not Expo or React Native.
- Generic backend architecture discussions that do not need Expo-specific environment or client wiring.

## Success criteria

A good outcome should leave the project with:

1. A single, correctly scoped Convex client and provider.
2. Working `EXPO_PUBLIC_CONVEX_URL` handling in local development and EAS.
3. Backend functions that match Convex best practices for validators, auth, actions, and query performance.
4. Frontend hooks using generated `api` references with clear loading, empty, and error states.
5. A validation pass using `scripts/validate_project.py`.
6. A clear path for future growth: pagination, indexes, auth wrappers, migrations, and linting.

## Non-negotiables

- Keep `npx convex dev` running while developing or repairing the integration.
- Read the deployment URL from `process.env.EXPO_PUBLIC_CONVEX_URL`.
- Mirror that value into EAS environments for preview and production builds.
- Create exactly one `ConvexReactClient` per app, outside render paths.
- Mount the provider at the true root: `app/_layout.tsx`, `src/app/_layout.tsx`, or `App.tsx`.
- In Expo and React Native, set `unsavedChangesWarning: false`.
- Import generated references from `convex/_generated/api` rather than stringly typed names.
- Treat all client-callable Convex functions as untrusted entry points.
- Add `args` validators to public functions, and prefer `returns` validators as well.
- Keep public wrappers thin; move repeated logic into helpers, internal functions, or custom wrappers.
- Do not use `Date.now()` or `new Date()` inside query logic.
- Do not use Node-only APIs or third-party SDKs inside queries or mutations.
- Put external API calls, heavy compute, or Node-only libraries in `action` or `internalAction` files; if a file starts with `"use node"`, keep it action-only.
- Avoid `.filter()` and unbounded `.collect()` on large tables; prefer indexes plus pagination.
- Await every promise.
- Prefer TypeScript strict mode and the official Convex ESLint plugin.

## First-pass triage

Before making changes, inspect the project and classify the job.

### 1. Identify the app entrypoint

Check for:

- `app/_layout.tsx` or `src/app/_layout.tsx` for Expo Router.
- `App.tsx` or `App.jsx` for classic entrypoints.

### 2. Audit Convex state

Look for:

- `package.json` dependencies: `convex`, `expo`, auth libraries, ESLint tooling.
- `convex/` and `convex/_generated/`.
- `.env.local`, `.env`, `.env.development`, `.env.production`.
- `eas.json` if cloud builds matter.
- Existing provider usage: `ConvexProvider`, `ConvexProviderWithClerk`, or custom auth wrappers.
- Existing schema and indexes in `convex/schema.ts`.
- Existing public functions with missing validators, auth checks, or pagination.

### 3. Run the validator

From the project root:

```bash
python scripts/validate_project.py --root <project-root>
```

Use `--json` for machine-readable output or `--fail-on-warning` when you want stricter gating.

### 4. Choose the workflow

- **Bootstrap / repair baseline**: missing Convex setup, env vars, provider, or generated API.
- **Build a feature slice**: add backend data and UI together.
- **Auth**: add or repair sign-in and backend authorization.
- **File uploads**: move media or documents from device URIs into Convex storage.
- **Scale / harden**: indexes, pagination, components, linting, production checklist.
- **Migration**: reshape existing tables or gradually move from another backend.

## Workflow A — Bootstrap or repair the baseline integration

### Step 1: Install or confirm the client package

```bash
npx expo install convex
```

### Step 2: Create or reconnect the Convex project

```bash
npx convex dev
```

Expect this to:

- create or connect a Convex project,
- create `convex/` if missing,
- generate `convex/_generated/`,
- write `EXPO_PUBLIC_CONVEX_URL` to `.env.local`,
- and keep syncing while the command runs.

### Step 3: Ensure the root provider exists

For Expo Router:

```tsx
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Stack } from "expo-router";

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!, {
  unsavedChangesWarning: false,
});

export default function RootLayout() {
  return (
    <ConvexProvider client={convex}>
      <Stack />
    </ConvexProvider>
  );
}
```

For classic `App.tsx`, wrap the top-level navigation tree the same way.

### Step 4: Confirm generated imports

Use:

```ts
import { api } from "../convex/_generated/api";
```

or the correct relative path for the project layout. Do not hand-write function names.

### Step 5: Verify development and build environments

Read [references/eas-env.md](references/eas-env.md) and ensure the same deployment URL policy is reflected in EAS.

### Step 6: Validate and smoke-test

- Start the Expo app.
- Confirm `useQuery(...)` moves from `undefined` to real data.
- Run `python scripts/validate_project.py --root <project-root>`.
- If needed, scaffold the canonical example with `python scripts/scaffold_tasks_example.py --root <project-root>`.

## Workflow B — Build a feature slice end to end

Build each feature in the order below.

### 1. Model the access pattern first

Before touching code, answer:

- Is the data public, user-scoped, org-scoped, or admin-only?
- Will the list stay small, or should it paginate?
- Which fields are lookup keys and therefore need indexes?
- Does any step require an external API, AI SDK, Stripe, or Node API?

### 2. Design the schema

Add or extend `convex/schema.ts` before the function layer whenever the model is stabilising.

Use [references/schema-and-indexes.md](references/schema-and-indexes.md) for:

- flat relational modelling,
- foreign-key indexing,
- compound indexes around actual query shapes,
- bounded array guidance,
- and pagination thresholds.

### 3. Implement backend functions

Use [references/functions.md](references/functions.md) for the detailed patterns.

Default rules:

- `query` for deterministic reads.
- `mutation` for writes.
- `action` or `internalAction` for external APIs, third-party SDKs, or Node-only code.
- `internalQuery` or `internalMutation` for logic that should never be callable from the client.

### 4. Enforce access on the backend

If the feature is not public, do one of these:

- explicit `ctx.auth.getUserIdentity()` checks in each function, or
- reusable custom wrappers via `convex-helpers`.

See [references/auth.md](references/auth.md) and [references/components-and-helpers.md](references/components-and-helpers.md).

### 5. Wire the frontend

Use [references/frontend-patterns.md](references/frontend-patterns.md).

Always handle:

- loading: `useQuery(...) === undefined`,
- empty state,
- mutation pending state where relevant,
- recoverable errors,
- and pagination for unbounded lists.

### 6. Validate the slice

Before finishing:

- run the validator with the project root,
- run lint and typecheck if the project has them,
- verify the feature on device or simulator,
- and update or add indexes before shipping.

## Workflow C — Authentication and authorization

Pick one auth story and keep the stack coherent.

### Option 1: Clerk

Good when the app already uses Clerk or wants a polished auth product.

### Option 2: Convex Auth

Good when you want a Convex-native auth stack and are comfortable adopting a beta library.

### Option 3: Existing JWT or OIDC provider

Good when the product already depends on Auth0, WorkOS, a company IdP, or another OIDC flow.

### Rules regardless of provider

- Backend authorization is mandatory; client-side gating is only for UX.
- If you persist users in Convex, index by a stable identifier such as `tokenIdentifier`.
- Check ownership, organisation membership, or role on every protected function.
- Prefer helper functions or custom wrappers instead of repeating auth boilerplate.
- Use internal functions for privileged internal-only operations.

Read [references/auth.md](references/auth.md) for a decision matrix and implementation patterns.

## Workflow D — File uploads from Expo

Use Convex upload URLs rather than trying to push raw files through a mutation.

Recommended flow:

1. public or protected mutation returns `ctx.storage.generateUploadUrl()`,
2. client loads the local `file://` URI with `fetch(uri)` and converts it to a `Blob`,
3. client `POST`s the blob to the upload URL,
4. second mutation stores the returned `storageId` plus app-specific metadata,
5. optional scheduled or action-based post-processing happens afterwards.

Read [references/file-uploads.md](references/file-uploads.md).

## Workflow E — Scale and harden

Once the baseline works, raise the quality bar.

### Performance

- Replace `.filter()` scans with indexed queries where possible.
- Replace unbounded `.collect()` with `take`, `first`, or paginated queries.
- Use `usePaginatedQuery` for growing feeds, notifications, and infinite-scroll screens.
- Push repeated or reusable feature areas into Convex components when boundaries are clear.

### Safety

- Add validators consistently.
- Keep privileged logic behind internal functions.
- Use `ConvexError` or clear return shapes for expected failures.
- Never trust IDs from the client without checking ownership or membership.

### Maintainability

- Turn on `@convex-dev/eslint-plugin`.
- Use TypeScript strict mode.
- Keep wrappers thin and move shared logic into plain TypeScript helpers.
- Separate `"use node"` action files from regular runtime files.

Read [references/production-checklist.md](references/production-checklist.md).

## Workflow F — Migrations

When changing a live schema, prefer additive transitions.

Default migration strategy:

1. add new fields or tables in a backwards-compatible way,
2. dual-read or dual-write if the shape is changing,
3. backfill existing documents in idempotent batches,
4. switch readers and writers,
5. then remove the old shape.

Use internal functions or scheduled jobs for backfills, and keep migrations restart-safe.

Read [references/migrations.md](references/migrations.md).

## Fast troubleshooting path

If the app is broken, check these in order:

1. Is `npx convex dev` running and free of TypeScript errors?
2. Does `.env.local` contain `EXPO_PUBLIC_CONVEX_URL`?
3. Was Metro restarted after the env file changed?
4. Is there exactly one `ConvexReactClient`?
5. Is the provider mounted at the real root?
6. Does `convex/_generated/api` exist, and are imports pointing at it correctly?
7. Are public functions missing `args` or `returns` validators?
8. Is a query using `Date.now()`, `.filter()`, or unbounded `.collect()`?
9. Is a `"use node"` file incorrectly mixing queries or mutations?
10. Is auth mismatched between the client provider and the backend config?

See [references/troubleshooting.md](references/troubleshooting.md).

## Available scripts

- `scripts/validate_project.py`
  - Validates the project rooted at `--root` or, if copied into a repo, the current working tree.
  - Validates Expo and Convex dependencies.
  - Checks env files, provider wiring, generated code, validator presence, `"use node"` misuse, and common query anti-patterns.
  - Supports `--json`, `--root`, and `--fail-on-warning`.

- `scripts/scaffold_tasks_example.py`
  - Dry-run by default.
  - Can generate `sampleData.jsonl`, `convex/schema.ts`, `convex/tasks.ts`, and an optional Expo screen file.
  - Supports `--write`, `--overwrite`, `--ui-file`, and `--json`.

## References

Load only the file that matches the current task.

- [references/eas-env.md](references/eas-env.md) — local envs, EAS envs, and deployment URL handling.
- [references/tasks-example.md](references/tasks-example.md) — canonical minimal example for the stack.
- [references/schema-and-indexes.md](references/schema-and-indexes.md) — schema design, indexes, query shape mapping, and pagination triggers.
- [references/functions.md](references/functions.md) — query, mutation, action, internal function, validators, and runtime boundaries.
- [references/frontend-patterns.md](references/frontend-patterns.md) — provider placement, hook usage, loading and error states, and paginated lists.
- [references/auth.md](references/auth.md) — Clerk, Convex Auth, JWT or OIDC, user mapping, and server-side authorization.
- [references/file-uploads.md](references/file-uploads.md) — upload URLs, Expo URI handling, metadata storage, and post-processing.
- [references/components-and-helpers.md](references/components-and-helpers.md) — Convex components and `convex-helpers` patterns.
- [references/migrations.md](references/migrations.md) — additive rollout, backfills, dual reads and writes, and batched migrations.
- [references/production-checklist.md](references/production-checklist.md) — pre-release hardening checklist.
- [references/troubleshooting.md](references/troubleshooting.md) — common failures and exact fixes.
- [references/evaluation.md](references/evaluation.md) — how to use the bundled trigger and output eval files.
- [references/sources.md](references/sources.md) — upstream docs and materials used for this rewrite.
