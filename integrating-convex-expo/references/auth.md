# Authentication options for Expo + Convex

## Choose an auth strategy (quick decision)
1. **Convex Auth** (Convex-native)
   - Lowest integration surface area if you only need “log in + get user identity in functions”.
   - Recommended if you don't already depend on an auth vendor.

2. **Clerk + Convex**
   - Popular for Expo apps and provides rich UI components / social login.
   - Convex provides `<ConvexProviderWithClerk>` via `convex/react-clerk`.

3. **Other OIDC / JWT providers**
   - Works well when you already have a provider (Auth0, WorkOS, custom).
   - Your Convex backend validates JWTs via `auth.config.ts`, then you enforce access control in functions.

## Clerk + Convex (Expo-friendly outline)
High-level steps (details vary by Clerk SDK, but the Convex side stays consistent):
1. Create a Clerk app and a **Convex JWT template** named `convex` (don’t rename it).
2. In `convex/auth.config.ts`, configure the provider with your issuer domain (often stored as a Convex env var like `CLERK_JWT_ISSUER_DOMAIN`).
3. Replace `<ConvexProvider>` with `<ConvexProviderWithClerk>` and wrap it in `<ClerkProvider>`.
4. Use Convex auth helpers (`Authenticated`, `Unauthenticated`, `AuthLoading`) and `useConvexAuth()` for gating UI.

### Convex-side config (example)
```ts
import { AuthConfig } from "convex/server";

export default {
  providers: [
    {
      domain: process.env.CLERK_JWT_ISSUER_DOMAIN!,
      applicationID: "convex",
    },
  ],
} satisfies AuthConfig;
```

## Access control: always enforce on the backend
Even with auth, treat the client as untrusted:
- Use `ctx.auth` in queries/mutations to check the current user.
- Filter data by user/team/org inside the function.
- Never rely on client-side checks for security.

## Storing user profiles
Depending on your provider, you may want to store a “user profile” document in Convex:
- store identity fields you need for querying (display name, avatar URL, org memberships)
- use indexes for lookups by `tokenIdentifier` or provider subject

(See upstream docs linked in `references/sources.md`.)

