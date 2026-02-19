# Troubleshooting Convex in Expo / React Native

## 1) `useQuery(...)` is always `undefined`
- `useQuery` returns `undefined` while loading. Confirm you eventually see data.
If it never resolves:
1. Confirm `npx convex dev` is running and not reporting TypeScript errors.
2. Confirm `process.env.EXPO_PUBLIC_CONVEX_URL` is defined at runtime.
3. Confirm the app is wrapped in `<ConvexProvider client={convex}>`.
4. Confirm you’re calling `useQuery(api.file.export)` from `convex/_generated/api` (not string names).

## 2) `process.env.EXPO_PUBLIC_CONVEX_URL` is `undefined`
- Make sure `.env.local` exists (created by `npx convex dev`) and includes `EXPO_PUBLIC_CONVEX_URL=...`.
- Restart Metro after adding/changing `.env*`.
- For EAS builds, set the value via `eas env:create ...` (see `references/eas-env.md`).

## 3) The `convex/_generated` folder is missing or stale
- It’s generated/updated by `npx convex dev`.
- Fix TypeScript errors in `convex/` files first; generation can stop if compilation fails.

## 4) “No such module @/convex/_generated/api”
- `@/` is a project-specific TS path alias (common in Expo templates, not universal).
- Use a relative import instead, e.g. `import { api } from "../convex/_generated/api"`.

## 5) Your app builds but crashes at runtime
Common causes:
- Provider not mounted high enough (some screens render without Convex context).
- Mixing multiple Convex clients (creating a new `ConvexReactClient` per render).

## 6) Weird device-only errors about `TextEncoder`, `TextDecoder`, or `crypto.getRandomValues`
These usually come from the JS runtime (Hermes) or other libraries, not Convex itself.
- If you see a missing `TextDecoder` on Hermes, Expo documents an `Encoding` API (UTF-8 only) and there are community polyfills.
- If you see `crypto.getRandomValues` errors, some libraries require a random-values polyfill on Hermes.

Treat these as *environment issues*:
1. Identify which dependency triggers it (stack trace).
2. Apply the smallest polyfill required, as early as possible in app startup.
3. Re-test on both iOS and Android.

## 7) Auth flows show “signed in” but Convex queries act unauthenticated
- When using third-party auth (e.g. Clerk), gate UI and query execution using `useConvexAuth()` / Convex auth helpers.
- Don’t rely on the auth provider’s “signed in” flag alone; Convex still needs a valid token and backend validation.

## Fast validation command
Run from your Expo project root:

```bash
python scripts/validate_project.py
```

