# Convex components and `convex-helpers`

Use this reference when the backend is starting to sprawl or when repeated patterns deserve their own abstraction.

## When to use `convex-helpers`

Install `convex-helpers` when you want proven patterns for:

- auth wrappers,
- tenant wrappers,
- relationship helpers,
- sessions,
- and other common building blocks.

```bash
npm install convex-helpers
```

## Highest-value helper: custom function wrappers

This is the most useful pattern for Expo apps with authenticated user data.

### Why wrap functions?

Without wrappers, every query and mutation repeats:

- identity lookup,
- user lookup,
- membership checks,
- and role checks.

That repetition is noisy and easy to get wrong.

### Authenticated wrapper example

`convex/lib/authFunctions.ts`

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

Use it like this:

```ts
import { authedQuery, authedMutation } from "./lib/authFunctions";
import { v } from "convex/values";

export const listMine = authedQuery({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", ctx.user._id))
      .order("desc")
      .take(50);
  },
});

export const create = authedMutation({
  args: { title: v.string() },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      userId: ctx.user._id,
      title: args.title.trim(),
      createdAt: Date.now(),
    });
  },
});
```

## Tenant-scoped wrapper

When the product has organisations or teams, wrap membership checks too.

Benefits:

- less boilerplate,
- fewer authorization mistakes,
- cleaner function bodies,
- and better consistency across the backend.

## Relationship helpers

If the backend frequently loads related entities, relationship helpers can keep code readable.

Typical examples:

- load task + assignee,
- load project + members,
- load channel + unread counts,
- load file + owner.

Use them when they make the code clearer, but still design indexes properly first.

## When to use Convex components

Convex components are best when a feature area wants a strong internal boundary.

Good candidates:

- rate limiting,
- notifications,
- file handling,
- billing,
- analytics,
- reusable auth or organisation infrastructure.

### Use a component when the feature has:

- its own tables,
- its own functions,
- a reusable or swappable boundary,
- or enough complexity that it muddies the rest of the app.

### Do not reach for components too early

For a small Expo app, plain `convex/*.ts` modules are simpler. Introduce components when they actually reduce complexity.

## Practical decision rule

### Stay with plain modules when

- the feature is local to one app,
- it has only a few functions,
- and the boundary is still evolving quickly.

### Move toward components when

- the feature is reused across domains,
- multiple modules depend on it,
- you want clearer ownership and isolation,
- or a third-party official component already solves the problem well.

## Example: file handling boundary

A growing file feature often wants:

- upload metadata tables,
- processing actions,
- thumbnail logic,
- permissions,
- and serving helpers.

That is a good place to consider a component or at least a dedicated domain subtree.

## Review checklist

- [ ] Repeated auth logic has been centralised if it appears often.
- [ ] Wrappers still keep authorization decisions explicit and understandable.
- [ ] Relationships are backed by indexes before helper abstractions are added.
- [ ] Components are introduced to reduce complexity, not for novelty.
- [ ] The backend remains easy to navigate for someone new to the codebase.
