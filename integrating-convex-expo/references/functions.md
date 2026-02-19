# Convex functions (query / mutation / action)

## Picking the right function type
- **query**: read data; must be deterministic; should be fast; returns data to clients.
- **mutation**: write data; can check auth; returns ids/results.
- **action**: for non-deterministic work (long fetches, Node APIs, heavier compute). Actions can call queries/mutations via `ctx.runQuery` / `ctx.runMutation` but avoid long sequential chains.

## Standard file organisation
- Put functions under `convex/` and name files by domain:
  - `convex/tasks.ts`
  - `convex/users.ts`
  - `convex/files.ts`

The exported symbol name becomes part of the API name:
- `convex/tasks.ts` + `export const get = ...` → `api.tasks.get`

## Always validate args
Use `v` validators on all functions called from the client:

```ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const byId = query({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id);
  },
});
```

## Access control pattern
Treat all client-callable functions as untrusted input:
- check auth (`ctx.auth`) if required
- enforce row-level access in the function, not in the client

## Frontend calling patterns
- `useQuery(api.tasks.get, { ...args })`
- `useMutation(api.tasks.add)` then call it: `await add({ ...args })`

## Error handling (what to throw)
- Throw `Error("message")` for client-visible errors.
- Keep errors actionable (“Not authorised”, “Task not found”, etc).

