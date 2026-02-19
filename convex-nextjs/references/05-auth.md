# Authentication patterns

## Decide: client-only vs server+client
- **Client-only**: easiest; UI gates in Client Components; server code doesn’t need `ctx.auth`.
- **Server+client**: required if you need authenticated SSR, Server Components, or Route Handlers to access data gated by `ctx.auth`.

## Client-only (example shape)
- Wrap your provider in the auth provider (Auth0/Clerk/etc).
- Use the relevant `ConvexProviderWith…` adapter (provider-specific package).
- Use `<Authenticated>`, `<Unauthenticated>`, `<AuthLoading>` from `convex/react` to show appropriate UI.

## Server+client (high level)
- Use a Next.js-compatible SDK to obtain a JWT token on the server.
- Pass `{ token }` to `preloadQuery` / `fetchQuery` when rendering on the server.
- In Convex functions, use `ctx.auth.getUserIdentity()` to access user identity and enforce access control.

## Storing users in Convex
- Option A: on login, client calls a mutation to upsert user info from `ctx.auth`.
- Option B: set up a webhook from your identity provider to sync users.
- Some auth solutions (e.g., Convex Auth) may store user information for you.

## Debugging auth
- Verify the browser is sending the auth token to Convex (Network tab).
- In Convex functions, log/inspect `ctx.auth.getUserIdentity()` in development.
