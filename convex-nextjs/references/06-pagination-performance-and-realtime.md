# Pagination, performance, and realtime

## Default rule
If a list can grow indefinitely, make it paginated before you build the UI.

Typical examples:
- activity feeds
- notifications
- messages
- search results
- audit logs
- comments on popular objects

## Backend paginated query
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

## React client
```tsx
"use client";

import type { Id } from "@/convex/_generated/dataModel";
import { usePaginatedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function Tasks({ projectId }: { projectId: Id<"projects"> }) {
  const { results, status, loadMore } = usePaginatedQuery(
    api.tasks.listByProject,
    { projectId },
    { initialNumItems: 20 },
  );

  return (
    <>
      <ul>{results.map((task) => <li key={task._id}>{task.title}</li>)}</ul>
      {status === "CanLoadMore" && (
        <button onClick={() => loadMore(20)}>Load more</button>
      )}
    </>
  );
}
```

## Realtime fit check
Convex is especially attractive when the user is building:
- live collaborative features
- chat and messaging
- presence or activity indicators
- notifications
- dashboards that should stay fresh without custom polling

## Performance checklist
- every hot read path has an index
- the UI uses paginated queries for unbounded data
- mutations write stored sort and filter fields intentionally
- helpers are extracted so business logic is readable
- no accidental full-table scans in core flows

## Smells to fix
- `.collect()` on user-facing feeds
- `.filter(...)` where an index should exist
- fetching many unrelated server-side queries for one page when a smaller number of coherent calls would do
- a query returning far more fields than the UI needs

## Realtime UX note
Use `useQuery` or `usePaginatedQuery` when the page should stay live after render.
Use `fetchQuery` only for server-only snapshots.
