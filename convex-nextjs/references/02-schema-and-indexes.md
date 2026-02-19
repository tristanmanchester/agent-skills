# Schema & indexes (data modelling)

## Golden rules
- Define tables and field types in `convex/schema.ts` with `defineSchema`, `defineTable`, and validators `v`.
- Index for your access patterns, then query with `.withIndex(...)` (usually faster and avoids unbounded scans).
- Use `v.optional(...)` for optional fields and `v.union(...)` for tagged unions.
- Convex automatically adds `_id` and `_creationTime` to documents.

## Minimal schema example
```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
    ownerId: v.optional(v.string()),
  })
    .index("by_owner", ["ownerId"])
    .index("by_completed", ["isCompleted"]),
});
```

## Index design notes
- Index names are per-table and must be unique per table.
- Compound indexes (multiple fields) are for common multi-field filters/sorts.
- If you need text search, define a search index in the schema (separate from standard DB indexes).

## Data modelling tips
- Prefer referencing other docs via `v.id("otherTable")` to keep relationships explicit.
- Keep documents small and queryable; put large blobs in File Storage and store IDs.

## When a schema change fails
- Ensure `npx convex dev` is running so schema/index updates sync.
- Confirm any new index is compatible with query code you’re writing.
