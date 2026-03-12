# Schema and index design for Expo + Convex

Convex works schemaless, but an Expo app benefits from adding `convex/schema.ts` early once the data model stops changing every few minutes.

## Design principles

### 1. Model documents as flat, relational records

Prefer:

- `tasks.userId`
- `comments.taskId`
- `memberships.organizationId`

over deeply nested arrays of objects inside a single document.

### 2. Add indexes for real query shapes

Index the fields you actually query on:

- ownership: `userId`
- membership: `organizationId`, `teamId`
- status tabs: `userId + status`
- time or ordering: `userId + createdAt`, `channelId + createdAt`
- lookup keys: `tokenIdentifier`, `email`, `slug`

### 3. Keep arrays bounded

Arrays are fine for small, naturally limited collections such as:

- user roles,
- a few tags,
- feature flags,
- recent device IDs.

Do not store large, growing sets such as comments, messages, or child records inside arrays.

### 4. Design around access rules

If every query is user-scoped, put `userId` directly on the table and index it.

If data is multi-tenant, include the org or team ID directly on every tenant-owned table rather than inferring tenancy indirectly.

## Schema template

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

  projects: defineTable({
    ownerId: v.id("users"),
    organizationId: v.optional(v.id("organizations")),
    name: v.string(),
    status: v.union(
      v.literal("active"),
      v.literal("archived"),
      v.literal("draft"),
    ),
    createdAt: v.number(),
  })
    .index("by_owner", ["ownerId"])
    .index("by_org", ["organizationId"])
    .index("by_owner_and_status", ["ownerId", "status"]),

  tasks: defineTable({
    projectId: v.id("projects"),
    assigneeId: v.optional(v.id("users")),
    title: v.string(),
    status: v.union(
      v.literal("todo"),
      v.literal("doing"),
      v.literal("done"),
    ),
    createdAt: v.number(),
  })
    .index("by_project", ["projectId"])
    .index("by_assignee", ["assigneeId"])
    .index("by_project_and_status", ["projectId", "status"]),
});
```

## Query shape mapping

Before adding an index, write the query in plain English.

- “List my active projects” → `by_owner_and_status`
- “Find a user by token identifier” → `by_token`
- “Show tasks for a project in todo state” → `by_project_and_status`
- “Load messages in a channel newest first” → `by_channel` plus `.order("desc")`

If you cannot describe the query shape clearly, the schema is usually not ready yet.

## Prefer indexes over `.filter()`

For large or growing tables:

- use `.withIndex(...)`,
- then use `.order(...)`, `.take(...)`, `.first()`, or `.paginate(...)`.

Use `.filter()` only when:

- the result set is already small and bounded, or
- the logic truly cannot be expressed via indexes.

If you do filter in TypeScript, start from a deliberately small result set rather than the whole table.

## Pagination rule of thumb

Switch from `take(...)` to pagination when any of the following are true:

- the list is user-generated and unbounded,
- the screen is a feed, inbox, notification list, or message list,
- the product expects hundreds of rows,
- or the UI naturally wants infinite scroll or “load more”.

See `references/frontend-patterns.md` for the frontend hook and `references/functions.md` for the backend query pattern.

## Time-based data

### Safe pattern

Store timestamps on writes:

- `createdAt`
- `updatedAt`
- `scheduledFor`
- `releasedAt`

and query them deterministically.

### Unsafe pattern

Do not call `Date.now()` inside a query to decide what should be returned right now.

Instead:

- pass time as an argument from the client, or
- maintain a coarser state field such as `isReleased`, `isExpired`, or `dueToday`, updated by a scheduled function.

## Example: messages with pagination

```ts
import { paginationOptsValidator } from "convex/server";
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listByChannel = query({
  args: {
    channelId: v.id("channels"),
    paginationOpts: paginationOptsValidator,
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channelId", args.channelId))
      .order("desc")
      .paginate(args.paginationOpts);
  },
});
```

## Common mistakes

### Missing index on a foreign key

If a feature constantly looks up `projectId`, `userId`, or `organizationId`, index it from the start.

### Nested objects growing without bound

If comments or checklist items can grow, they deserve their own table.

### Too many redundant indexes

Do not create every possible index “just in case”. Add indexes around observed access patterns.

### Migrating directly to a breaking schema

For live data, add optional fields first, backfill, and only then make them required. See `references/migrations.md`.

## Review checklist

- [ ] Each protected resource stores the ownership or tenancy field it needs.
- [ ] Each common lookup has a matching index.
- [ ] Bounded arrays stay bounded.
- [ ] Large lists use pagination rather than unbounded collection.
- [ ] Query code does not rely on `Date.now()` for live filtering.
- [ ] The schema is easy to explain in terms of product features rather than implementation accidents.
