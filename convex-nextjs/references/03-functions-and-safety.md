# Functions and safety

## Choose the smallest correct function type
- **Query**: read-only data access.
- **Mutation**: transactional writes.
- **Action**: external API calls, long-running orchestration, or non-transactional work.
- **Internal** variants: for functions that should not be client-callable.

## Public functions: baseline requirements
For any public query, mutation, or action:
- define `args`
- usually define `returns`
- validate access
- await all promises
- keep database access index-driven

## Query example
```ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const getById = query({
  args: { taskId: v.id("tasks") },
  returns: v.union(
    v.object({
      _id: v.id("tasks"),
      _creationTime: v.number(),
      projectId: v.id("projects"),
      assigneeId: v.optional(v.id("users")),
      title: v.string(),
      status: v.union(
        v.literal("todo"),
        v.literal("doing"),
        v.literal("done"),
      ),
      dueAt: v.optional(v.number()),
      createdAt: v.number(),
    }),
    v.null(),
  ),
  handler: async (ctx, args) => {
    return await ctx.db.get("tasks", args.taskId);
  },
});
```

## Mutation example
```ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";
import { requireCurrentUser } from "./lib/auth";

export const create = mutation({
  args: {
    projectId: v.id("projects"),
    title: v.string(),
  },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    const user = await requireCurrentUser(ctx);

    // Optional ownership check on the parent resource goes here.
    return await ctx.db.insert("tasks", {
      projectId: args.projectId,
      assigneeId: user._id,
      title: args.title,
      status: "todo",
      createdAt: Date.now(),
    });
  },
});
```

## Action example
Use the default Convex runtime unless you need Node-only APIs or unsupported packages.

```ts
import { action } from "./_generated/server";
import { api } from "./_generated/api";
import { v } from "convex/values";

export const enrichTask = action({
  args: { taskId: v.id("tasks") },
  returns: v.null(),
  handler: async (ctx, args) => {
    const response = await fetch("https://example.com/enrich", {
      method: "POST",
      body: JSON.stringify({ taskId: args.taskId }),
      headers: { "content-type": "application/json" },
    });

    const data = await response.json();

    await ctx.runMutation(api.tasks.applyEnrichment, {
      taskId: args.taskId,
      summary: data.summary,
    });

    return null;
  },
});
```

## `"use node"`: when it is actually justified
Only add `"use node"` when the action needs:
- Node-only APIs such as filesystem access, certain crypto APIs, or process-level libraries
- third-party SDKs that do not run in the default Convex runtime

If a file uses `"use node"`, keep **only actions** in that file.

## Scheduler safety
When scheduling work from functions, prefer internal function references rather than public `api.*` references.

Good shape:
```ts
await ctx.scheduler.runAfter(0, internal.jobs.sendDigest, {
  userId: args.userId,
});
```

## Helper functions and wrappers
Keep registered functions thin. Push reusable logic into plain TypeScript helpers:
- `getCurrentUser`
- `requireMembership`
- `loadProjectOrThrow`
- `assertCanEditTask`

If many functions repeat the same access checks, consider custom wrappers or helper constructors so the protection is centralised.

## Query-performance rules of thumb
- Prefer `.withIndex(...)` over `.filter(...)` whenever possible.
- Prefer `.take(n)` or pagination over unbounded `.collect()`.
- Treat `.collect()` as a smell unless the result set is truly bounded.
- If a list is user-facing and can grow indefinitely, paginate it.

## Time-based logic
Do not hide core business logic behind ambient state if you can store or pass what you need explicitly.
Prefer:
- persisted timestamps for sorting
- stored status fields for common filters
- explicit arguments when evaluating a date-sensitive view

If you do use current time helpers inside queries, keep the logic intentional and easy to test.

## Error shape
Use direct, user-meaningful errors:
- `"Not authenticated"`
- `"Task not found"`
- `"You do not have access to this project"`

Do not leak secrets or provider internals through error strings.
