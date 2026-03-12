# Schema and indexes

## Design for read patterns
Model tables around the queries you expect to run repeatedly, not around the exact shape of a screen.

### Ask first
- What is the ownership boundary: user, team, workspace, org?
- Which lists are filtered by owner, status, parent, or time?
- Which reads must be unique?
- Which lists can grow forever and therefore need pagination?

## Baseline example
```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  users: defineTable({
    tokenIdentifier: v.string(),
    name: v.string(),
    email: v.optional(v.string()),
  }).index("by_token", ["tokenIdentifier"]),

  projects: defineTable({
    ownerId: v.id("users"),
    name: v.string(),
    archived: v.boolean(),
    createdAt: v.number(),
  })
    .index("by_owner", ["ownerId"])
    .index("by_owner_and_archived", ["ownerId", "archived"]),

  tasks: defineTable({
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
  })
    .index("by_project", ["projectId"])
    .index("by_project_and_status", ["projectId", "status"])
    .index("by_assignee", ["assigneeId"]),
});
```

## Query from indexes, not scans
Prefer:
```ts
return await ctx.db
  .query("tasks")
  .withIndex("by_project_and_status", (q) =>
    q.eq("projectId", args.projectId).eq("status", "todo"),
  )
  .take(50);
```

Avoid reaching first for:
```ts
return await ctx.db
  .query("tasks")
  .filter((q) => q.eq(q.field("projectId"), args.projectId))
  .collect();
```

## Modelling guidance
- Prefer flat relational documents over deep nested arrays or maps.
- Use `v.id("otherTable")` for document relationships.
- Keep large blobs in File Storage and store references in tables.
- Add `searchIndex` or `vectorIndex` only when the feature actually needs search or embeddings.
- Be deliberate about timestamps and status fields. Persist what you need for sorting and filtering instead of recomputing everything ad hoc.

## Migration mindset
When adding a field or index:
1. update `schema.ts`
2. update the write path
3. update the reads to use the new index
4. consider whether existing documents need backfill logic

If the repo is mid-migration, prefer additive changes first and only remove old fields after code has switched over.
