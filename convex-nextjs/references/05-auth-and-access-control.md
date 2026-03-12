# Auth and access control

## Decide the auth shape
- **Client-only auth**: easiest if only client UI needs auth-gated data.
- **Server + client auth**: required when Server Components, Server Actions, or Route Handlers need user-scoped access.
- **App-level multi-tenant auth**: add explicit tenant or workspace membership checks early.

## Users table baseline
```ts
users: defineTable({
  tokenIdentifier: v.string(),
  name: v.optional(v.string()),
  email: v.optional(v.string()),
  role: v.optional(v.union(v.literal("user"), v.literal("admin"))),
}).index("by_token", ["tokenIdentifier"]),
```

## Helper-first pattern
Create helpers before inventing wrappers:

```ts
import type { QueryCtx, MutationCtx } from "./_generated/server";
import type { Doc } from "./_generated/dataModel";

type AuthCtx = QueryCtx | MutationCtx;

export async function getCurrentUserOrNull(
  ctx: AuthCtx,
): Promise<Doc<"users"> | null> {
  const identity = await ctx.auth.getUserIdentity();
  if (!identity) return null;

  return await ctx.db
    .query("users")
    .withIndex("by_token", (q) =>
      q.eq("tokenIdentifier", identity.tokenIdentifier),
    )
    .unique();
}

export async function requireCurrentUser(ctx: AuthCtx) {
  const user = await getCurrentUserOrNull(ctx);
  if (!user) throw new Error("Not authenticated");
  return user;
}
```

## Access control rules
- Never trust a client-supplied `userId` for permissions.
- Load the current user from auth, then compare against the resource.
- For team or workspace apps, check membership on every protected read and write.
- Use internal functions for system-only work.

## Ownership example
```ts
const task = await ctx.db.get("tasks", args.taskId);
if (!task) throw new Error("Task not found");

if (task.assigneeId !== user._id) {
  throw new Error("You do not have access to this task");
}
```

## When wrappers/custom functions help
If many functions repeat the same auth, tenant, or role checks:
- centralise the logic in helpers or wrapper factories
- keep the wrapper thin and visible
- avoid making the wrapper so magical that reviewers cannot see what a function requires

If the repo already uses `convex-helpers` or an equivalent pattern, extend it rather than fighting it.

## User creation and syncing
Common patterns:
- create or upsert a user document on first successful sign-in
- update profile data on a webhook or a dedicated sync mutation
- keep provider-specific identifiers out of business logic except for identity mapping

## Server-side auth
For authenticated server rendering or server actions:
- obtain a token via the provider's Next.js SDK
- pass that token into `convex/nextjs` helpers
- continue enforcing auth again inside Convex functions

Frontend checks are UX only. Convex functions are the real security boundary.
