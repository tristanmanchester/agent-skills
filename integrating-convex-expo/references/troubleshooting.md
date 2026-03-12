# Troubleshooting Expo + Convex

Use this file when the integration mostly exists but something is clearly off.

## `useQuery(...)` stays `undefined`

Remember: `undefined` is normal during the initial load.

If it never resolves, check these in order:

1. `npx convex dev` is running.
2. `convex/_generated/api` exists.
3. the provider is mounted at the app root.
4. the app can read `process.env.EXPO_PUBLIC_CONVEX_URL`.
5. the query reference comes from generated `api`.
6. the backend function is compiling successfully.

## `EXPO_PUBLIC_CONVEX_URL` is `undefined`

Most common causes:

- `.env.local` was never created because `npx convex dev` has not run,
- Metro was not restarted after the env file changed,
- the code uses the wrong variable name,
- a different `.env*` file overrides the expected value.

## `convex/_generated` is missing or stale

Causes:

- `npx convex dev` is not running,
- TypeScript errors in `convex/` stopped generation,
- or the working directory for `npx convex dev` was wrong.

Fix:

1. run `npx convex dev` from the Expo project root,
2. fix any backend compile errors,
3. wait for generation to complete.

## “Cannot find module '../convex/_generated/api'”

Usually one of these:

- the relative path is wrong for the screen’s location,
- the project uses `src/app` but the import assumes `app`,
- or `convex/_generated` has not been generated yet.

## The app crashes after adding Convex

Common causes:

- provider is mounted too low in the tree,
- multiple `ConvexReactClient` instances exist,
- or a screen renders before the root provider is available.

## Query is stale or behaves strangely around time

If a query uses `Date.now()` or `new Date()` internally, the reactivity model will not behave the way you expect.

Fix:

- pass time as an argument,
- or maintain a stored status field updated elsewhere.

## Slow screens or expensive queries

Look for:

- `.filter()` on large tables,
- unbounded `.collect()`,
- missing indexes on foreign keys,
- or screens trying to load entire feeds at once.

Fix:

- add indexes,
- switch to `.withIndex(...)`,
- use `take(...)` or paginated queries,
- and update the screen to `usePaginatedQuery` where appropriate.

## Node or third-party SDK errors in backend files

If a query or mutation tries to use:

- `fetch` to third-party APIs,
- `Buffer`,
- `crypto`,
- Stripe,
- OpenAI,
- filesystem access,

move that logic into an action. If the file needs Node APIs, start it with `"use node"` and keep it action-only.

## Auth says signed in but backend is unauthenticated

Check all three layers:

1. client auth provider is mounted correctly,
2. Convex auth provider configuration matches the client provider,
3. backend functions actually read and enforce `ctx.auth.getUserIdentity()`.

Do not trust only the UI provider’s “signed in” flag.

## File uploads succeed but the app cannot find the file later

Check:

- the second metadata mutation was awaited,
- the correct `storageId` was persisted,
- the query returning file data is authorized,
- the UI is asking for the correct file record.

## ESLint or validation warnings about public functions

Typical fixes:

- add `args: { ... }`,
- add `returns: ...`,
- move internal-only logic to internal functions,
- replace scans with indexes,
- or split `"use node"` code into a separate action file.

## Remote agent or CI environment cannot run `npx convex dev`

Only cloud agents or CI-like environments that cannot log in should consider:

```bash
CONVEX_AGENT_MODE=anonymous npx convex dev
```

Do not add this by default for local development. Local work should usually use your normal authenticated Convex setup.

## Quick recovery sequence

When the project is messy and you need to stabilise it fast:

1. stop Metro,
2. start `npx convex dev`,
3. run `python scripts/validate_project.py --root <project-root>`,
4. fix env issues,
5. fix provider placement,
6. fix generated API imports,
7. restart Metro,
8. re-test with a small known-good query such as the tasks example.

## Useful commands

```bash
python scripts/validate_project.py --root <project-root>
python scripts/validate_project.py --root <project-root> --json
python scripts/scaffold_tasks_example.py --root <project-root>
```
