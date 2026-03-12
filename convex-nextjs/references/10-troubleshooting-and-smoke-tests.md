# Troubleshooting and smoke tests

## Quick smoke test sequence
1. `npx convex dev`
2. confirm `_generated/api.ts` exists
3. confirm the app wraps a Convex provider
4. confirm `NEXT_PUBLIC_CONVEX_URL` exists
5. render one tiny query in a Client Component
6. mutate one record and confirm the UI updates

## Common failures

### `NEXT_PUBLIC_CONVEX_URL` is missing
- rerun `npx convex dev`
- check `.env.local`
- check hosting env vars
- pass an explicit URL to server helpers if needed

### React hook or client/server errors
- add `"use client"` to files using Convex React hooks
- keep hooks out of Server Components
- ensure the provider actually wraps the route tree

### Generated code missing or stale
- keep `npx convex dev` running
- run `npx convex codegen`
- confirm the functions directory path from `convex.json`

### Query is slow or returns too much data
- add an index
- replace `.filter(...)` with `.withIndex(...)`
- paginate instead of `.collect()`
- return a smaller, deliberate payload

### Auth is always null
- confirm the auth provider is wired to Convex on the client
- confirm server-side calls pass a token when needed
- log the result of `ctx.auth.getUserIdentity()` in development

### Node runtime issues
- if a library only works in Node, move it to an action file with `"use node"`
- do not mix queries or mutations into that file

### Scheduled jobs are callable from the client
- schedule `internal.*` functions, not public `api.*` functions

## Useful commands
```bash
python {baseDir}/scripts/validate_project.py --root .
python {baseDir}/scripts/validate_project.py --root . --strict
npx convex codegen
npx convex dashboard
```
