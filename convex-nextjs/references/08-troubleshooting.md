# Troubleshooting cheat sheet

## “NEXT_PUBLIC_CONVEX_URL is undefined”
- Re-run `npx convex dev` (it typically writes `.env.local`)
- Ensure your hosting environment has the env var set.
- For SSR helpers (`convex/nextjs`): env var must be present OR pass `url` option.

## “useQuery can’t be used here” / React hook errors
- Ensure the file is a Client Component: add `"use client"` at the top.
- Ensure your component is wrapped by `<ConvexProvider>` (via `ConvexClientProvider`).

## Generated code missing / type errors
- Keep `npx convex dev` running, or run `npx convex codegen`.
- Commit `convex/_generated/*` if your repo expects typechecking in CI.

## Data doesn’t update in real time
- Verify you’re using `useQuery` (reactive) rather than server-only `fetchQuery`.
- Ensure there isn’t a second Convex client instance being created during navigation.

## Debugging basics
- Open the Convex dashboard and inspect tables, indexes, logs.
- Use `rg` to locate all Convex calls in frontend.
