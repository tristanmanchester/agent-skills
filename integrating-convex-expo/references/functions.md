# Convex function patterns for Expo projects

Use this reference when deciding how to implement backend logic and where that logic should live.

## Choose the right function type

### `query`

Use for deterministic reads.

Good for:

- loading lists,
- loading detail views,
- computing derived read-only values from Convex data.

Rules:

- no writes,
- no external network access,
- no `Date.now()`-driven behaviour inside the query,
- and keep it fast.

### `mutation`

Use for writes.

Good for:

- create, update, delete,
- toggles,
- transactional state changes,
- bookkeeping fields such as `createdAt` and `updatedAt`.

Rules:

- do not call third-party APIs from mutations,
- keep business rules server-side,
- and validate all client inputs.

### `action`

Use when you need things outside the normal deterministic runtime.

Good for:

- calling external APIs,
- using Node-only packages,
- AI SDKs,
- Stripe,
- sending email,
- filesystem or crypto APIs that require the Node runtime,
- post-processing uploads.

Rules:

- if the file starts with `"use node"`, keep that file action-only,
- call writes via `ctx.runMutation(...)`,
- call reads via `ctx.runQuery(...)`,
- and avoid mixing runtime modes in the same file.

### Internal functions

Use `internalQuery`, `internalMutation`, and `internalAction` when logic should never be callable from a client.

Good for:

- backfills,
- privileged state transitions,
- action helpers,
- scheduled jobs,
- expensive maintenance logic,
- and refactoring public wrappers into smaller internal operations.

## Minimum standard for public functions

Every public `query`, `mutation`, and `action` should have:

- `args`,
- clear backend authorization if the data is not public,
- and preferably `returns`.

For mutations that do not return useful data, explicitly return `null`.

## Starter template

```ts
import { mutation, query, internalMutation } from "./_generated/server";
import { v } from "convex/values";

const taskDoc = v.object({
  _id: v.id("tasks"),
  _creationTime: v.number(),
  userId: v.id("users"),
  title: v.string(),
  status: v.union(
    v.literal("todo"),
    v.literal("doing"),
    v.literal("done"),
  ),
  createdAt: v.number(),
});

export const listMine = query({
  args: {
    userId: v.id("users"),
  },
  returns: v.array(taskDoc),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("userId", args.userId))
      .order("desc")
      .take(50);
  },
});

export const create = mutation({
  args: {
    userId: v.id("users"),
    title: v.string(),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    const title = args.title.trim();
    if (!title) throw new Error("Task title cannot be empty");

    return await ctx.db.insert("tasks", {
      userId: args.userId,
      title,
      status: "todo",
      createdAt: Date.now(),
    });
  },
});

export const markDone = internalMutation({
  args: {
    taskId: v.id("tasks"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.taskId, { status: "done" });
    return null;
  },
});
```

## Thin wrappers, shared helpers

Keep wrappers small. Put repeated logic in plain TypeScript helpers.

### Good structure

- `convex/tasks.ts` for public wrappers
- `convex/lib/auth.ts` for identity lookup helpers
- `convex/lib/tasks.ts` for business rules or validation helpers
- `convex/tasksActions.ts` for external API or Node-runtime work

### Why this matters

- easier to test,
- less duplicated auth and ownership logic,
- easier to reuse from actions or background jobs,
- safer refactors.

## Auth pattern

If data is user-scoped, do not trust a client-supplied `userId` unless the function verifies it.

Safer patterns:

- read the current identity with `ctx.auth.getUserIdentity()`,
- resolve the corresponding user document,
- and then scope queries or writes with the verified user.

When many functions need the same protection, create custom wrappers with `convex-helpers`. See `references/auth.md` and `references/components-and-helpers.md`.

## Expected failures vs exceptional failures

For expected product-level failures:

- return `null` or a discriminated result shape when that fits the API,
- or throw a `ConvexError` with a structured payload when the caller should handle it as an expected failure.

Examples:

- unauthenticated access,
- trying to edit a resource the user does not own,
- validation that depends on current database state,
- or “not found” for a user-selected record.

Use plain `Error` for unexpected failures when structure is not needed.

## Avoid these anti-patterns

### 1. Unvalidated public functions

Bad:

```ts
export const create = mutation({
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", args);
  },
});
```

Why it is bad:

- no input validation,
- no output contract,
- easy to accidentally expose fields you did not intend.

### 2. Query logic that depends on wall-clock time

Bad:

```ts
export const listReleased = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db
      .query("posts")
      .withIndex("by_released_at", (q) => q.lte("releasedAt", Date.now()))
      .take(50);
  },
});
```

Safer options:

- pass `now` from the client as an argument when needed,
- or precompute a field such as `isReleased` with scheduled updates.

### 3. Full-table scans with `.filter()`

Bad:

```ts
const project = await ctx.db
  .query("projects")
  .filter((q) => q.eq(q.field("slug"), args.slug))
  .unique();
```

Better:

- add `.index("by_slug", ["slug"])`,
- use `.withIndex("by_slug", ...)`.

### 4. Unbounded `.collect()` on feeds

Bad:

```ts
return await ctx.db.query("notifications").collect();
```

Better:

- use `.take(50)` for small bounded lists,
- or paginated queries for inboxes, feeds, and chat.

### 5. Mixing `"use node"` with queries or mutations

Bad:

```ts
"use node";

import { mutation } from "./_generated/server";

export const createTask = mutation({
  // invalid in a Node-runtime-only file
});
```

Correct pattern:

- keep regular `query` and `mutation` functions in normal runtime files,
- create a sibling `somethingActions.ts` file for `"use node"` actions.

## Action pattern for external services

`convex/aiActions.ts`

```ts
"use node";

import { action } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

export const generateAndStoreSummary = action({
  args: {
    noteId: v.id("notes"),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    const note = await ctx.runQuery(internal.notes.getForSummariser, {
      noteId: args.noteId,
    });

    if (!note) {
      throw new Error("Note not found");
    }

    const summary = `Summary for ${note.title}`;

    await ctx.runMutation(internal.notes.storeSummary, {
      noteId: args.noteId,
      summary,
    });

    return null;
  },
});
```

## Pagination backend pattern

```ts
import { paginationOptsValidator } from "convex/server";
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listByProject = query({
  args: {
    projectId: v.id("projects"),
    paginationOpts: paginationOptsValidator,
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_project", (q) => q.eq("projectId", args.projectId))
      .order("desc")
      .paginate(args.paginationOpts);
  },
});
```

## Review checklist

- [ ] Correct function type chosen.
- [ ] Public functions validate `args`.
- [ ] Public functions expose deliberate `returns`.
- [ ] Protected data is authorised on the backend.
- [ ] Shared logic lives in helpers or wrappers.
- [ ] External APIs and Node-only SDKs live in actions.
- [ ] No unbounded `.collect()` on growing data.
- [ ] No `Date.now()` inside query logic.
- [ ] All promises are awaited.
- [ ] Internal functions are used to reduce public surface area where appropriate.
