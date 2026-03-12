# Authentication and authorization for Expo + Convex

This reference is about choosing an auth stack and then enforcing access correctly on the backend.

## First principle

Authentication answers **who the user is**.

Authorization answers **what that user may do**.

Expo screens can help with auth UX, but authorization must live in Convex functions.

## Decision matrix

### Choose Clerk when

- the app already uses Clerk,
- you want polished hosted auth flows,
- you want a familiar Expo-friendly product auth layer,
- or the team already knows Clerk.

### Choose Convex Auth when

- you want a Convex-native auth stack,
- you do not want a separate auth SaaS for this project,
- and you are comfortable adopting a beta library.

### Choose an existing JWT or OIDC provider when

- the company already uses Auth0, WorkOS, an enterprise IdP, or a custom OIDC flow,
- the app needs to plug into an existing identity estate,
- or migrations would be more expensive than keeping the current provider.

## Backend rules that never change

- Never rely on a client-provided `userId` without verifying it.
- Every protected function should derive the current user from `ctx.auth.getUserIdentity()`, directly or via a wrapper.
- Check ownership, membership, or role before returning data or performing writes.
- Use internal functions for privileged operations that should not be directly public.

## Users table pattern

If the product needs user profiles in Convex, create a `users` table keyed by a stable identity field.

```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    tokenIdentifier: v.string(),
    email: v.string(),
    name: v.string(),
    imageUrl: v.optional(v.string()),
    role: v.union(v.literal("user"), v.literal("admin")),
  })
    .index("by_token", ["tokenIdentifier"])
    .index("by_email", ["email"]),
});
```

## Identity lookup helper

```ts
import type { MutationCtx, QueryCtx } from "./_generated/server";

export async function getCurrentUser(ctx: QueryCtx | MutationCtx) {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) {
    throw new Error("Not authenticated");
  }

  const user = await ctx.db
    .query("users")
    .withIndex("by_token", (q) =>
      q.eq("tokenIdentifier", identity.tokenIdentifier),
    )
    .unique();

  if (!user) {
    throw new Error("User not found");
  }

  return user;
}
```

## Clerk notes

Typical stack:

- `@clerk/clerk-expo` on the client,
- Convex configured with Clerk as an auth provider,
- a root provider that combines Clerk and Convex,
- backend functions that still perform access checks.

Patterns to remember:

- UI can be gated with Clerk state and Convex auth helpers.
- Convex should still validate the token and enforce access on reads and writes.
- If the app stores user documents, sync them from a protected mutation rather than trusting client state.

## Convex Auth notes

Use this when you want auth directly in the Convex backend.

What to watch:

- it supports React Native,
- but it is still beta,
- so check current docs before making it the default for a production-critical app.

For teams already committed to a separate identity provider, Convex Auth may not be the cheapest migration.

## Generic JWT or OIDC notes

When keeping an existing provider:

- configure Convex to validate the provider’s JWTs,
- ensure the token contains a stable subject or identifier,
- map that identifier to the `users` table when needed,
- keep the backend checks exactly as strict as with any other provider.

## Custom function wrappers with `convex-helpers`

If many functions repeat the same auth and tenant checks, use wrappers.

### Example: authenticated query wrapper

```ts
import { customQuery, customMutation } from "convex-helpers/server/customFunctions";
import { query, mutation } from "../_generated/server";
import { getCurrentUser } from "./auth";

export const authedQuery = customQuery(query, {
  args: {},
  input: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    return { ctx: { ...ctx, user }, args };
  },
});

export const authedMutation = customMutation(mutation, {
  args: {},
  input: async (ctx, args) => {
    const user = await getCurrentUser(ctx);
    return { ctx: { ...ctx, user }, args };
  },
});
```

### Example: org-scoped wrapper

```ts
import { customQuery } from "convex-helpers/server/customFunctions";
import { query } from "../_generated/server";
import { v } from "convex/values";
import { getCurrentUser } from "./auth";

export const orgQuery = customQuery(query, {
  args: {
    organizationId: v.id("organizations"),
  },
  input: async (ctx, args) => {
    const user = await getCurrentUser(ctx);

    const membership = await ctx.db
      .query("organizationMembers")
      .withIndex("by_org_and_user", (q) =>
        q.eq("organizationId", args.organizationId).eq("userId", user._id),
      )
      .unique();

    if (!membership) {
      throw new Error("Not authorized for this organization");
    }

    return {
      ctx: {
        ...ctx,
        user,
        organizationId: args.organizationId,
        role: membership.role,
      },
      args,
    };
  },
});
```

## Backend authorization patterns

### Owner-only resource

- verify the current user,
- fetch the resource,
- compare `resource.userId` with `user._id`,
- reject mismatches.

### Team or org membership

- store membership rows in a join table,
- index by `(organizationId, userId)` or `(teamId, userId)`,
- check membership before loading or mutating resources.

### Role-based admin access

- keep a `role` field on the user or membership row,
- centralise the check in a helper or wrapper,
- and avoid copying role logic across dozens of files.

## Common mistakes

### UI says signed in but Convex behaves unauthenticated

Usually caused by one of these:

- the root provider pairing is incomplete,
- the backend provider config does not match the client provider,
- or the client is rendering too early before Convex auth has finished initialising.

### Resource access keyed by email alone

Do not use mutable or user-controlled fields like email as the only access key. Resolve the verified identity first.

### Repeating auth logic everywhere

If the same auth and tenant boilerplate appears in three or more places, wrap it.

## Review checklist

- [ ] Auth provider choice matches the project’s existing stack.
- [ ] Protected functions derive identity from Convex auth, not from the client alone.
- [ ] A stable identity field such as `tokenIdentifier` is indexed.
- [ ] Ownership or membership checks are implemented on the backend.
- [ ] Repeated auth boilerplate is centralised in helpers or wrappers.
- [ ] Privileged workflows are moved behind internal functions when appropriate.
