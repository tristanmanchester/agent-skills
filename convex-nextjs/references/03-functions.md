# Convex functions (queries, mutations, actions)

## Decide which function type to use
- **Query**: read-only, deterministic.
- **Mutation**: read/write transaction, deterministic (no network calls).
- **Action**: can call third-party services / non-deterministic; must call queries/mutations to access the DB.

## Naming (how functions appear to the client)
- File path + export name become the API path.
  - `convex/tasks.ts` exporting `get` → `api.tasks.get`
  - `convex/admin/reports.ts` exporting `daily` → `api.admin.reports.daily`

## Always validate args
- For any function callable from the client, define `args` with `v.*` validators.

### Query example (indexed)
```ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listByOwner = query({
  args: { ownerId: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_owner", (q) => q.eq("ownerId", args.ownerId))
      .order("desc")
      .take(100);
  },
});
```

### Mutation example (insert)
```ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: { text: v.string() },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("tasks", { text: args.text, isCompleted: false });
    return id;
  },
});
```

## Access control patterns (minimal)
- If auth is enabled, check `ctx.auth.getUserIdentity()` at the start of every public function.
- Enforce ownership in reads and writes (e.g., by filtering on `ownerId`).

## Best practices that prevent common footguns
- Await all promises.
- Avoid `.filter` on DB queries when an index-based query is appropriate.
- Avoid `.collect()` for large/unbounded result sets; use `.take(n)` or pagination.

## Actions & runtimes
- Actions default to Convex’s runtime (supports `fetch`).
- If you need Node.js APIs or unsupported packages, put `"use node";` at the top of the file.
  - Note: other Convex functions cannot be defined in files with `"use node";`.

## Pagination
- Use cursor-based pagination via `.paginate(paginationOpts)` and `usePaginatedQuery` in React.
