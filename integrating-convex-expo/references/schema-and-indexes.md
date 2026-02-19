# Schema + indexes (production-friendly defaults)

## When to add a schema
- Add `convex/schema.ts` early if you want:
  - type-safe docs in TS
  - safer refactors/migrations
  - clearer index definitions and query performance expectations

Convex can run schemaless, but a schema is strongly recommended once your data model stabilises.

## Minimal schema pattern
```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
    ownerId: v.optional(v.id("users")),
  })
    // index examples:
    .index("by_owner", ["ownerId"])
    .index("by_owner_and_completed", ["ownerId", "isCompleted"]),
});
```

## Index rules of thumb
- If you might ever query over **1000+** documents, define an index that supports the lookup.
- Prefer `.withIndex(...)` conditions for large tables; avoid doing large `.collect()` calls and filtering in JS.
- Add indexes before you ship to production; retrofitting indexes is fine, but you’ll notice perf issues sooner.

## Querying with indexes
```ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listByOwner = query({
  args: { ownerId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_owner", (q) => q.eq("ownerId", args.ownerId))
      .order("desc")
      .take(50);
  },
});
```

## Best-practice reminders
- Await all promises in functions.
- Be cautious with `.collect()` on potentially unbounded result sets.
- Avoid putting `Date.now()` directly inside queries; it breaks caching.

(See upstream docs linked in `references/sources.md`.)

