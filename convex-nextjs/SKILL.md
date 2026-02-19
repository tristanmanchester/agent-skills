---
name: convex-nextjs
description: >-
  Builds and maintains Convex backends inside Next.js apps, including schema design,
  queries/mutations/actions, realtime React hooks, App Router server rendering, auth,
  file uploads, scheduling, testing, and deployment.
  Use when a project mentions Convex, Next.js, app router/pages router, convex/ folder,
  useQuery/useMutation, schema.ts, actions, or needs a type-safe realtime backend.
allowed-tools: Read,Write,Bash(npm:*),Bash(pnpm:*),Bash(yarn:*),Bash(npx:*),Bash(node:*),Bash(git:*)
---

# Convex + Next.js Agent Skill

## Why this exists

Convex is “batteries included” (database + backend functions + realtime subscriptions). Next.js (especially the App Router) adds constraints: **Client vs Server Components**, server rendering, env vars, and auth token plumbing. This skill standardises the *golden path* so you don’t accidentally:

- call Convex React hooks in Server Components
- put Node-only dependencies into the default Convex runtime
- expose internal functions to clients
- write unindexed queries that don’t scale
- leak private data via missing auth checks

## When to use this skill (triggers)

Use this skill whenever you need to:

- add Convex to a Next.js app (App Router or Pages Router)
- create/modify `convex/schema.ts` and Convex functions (`query`, `mutation`, `action`, `httpAction`)
- wire `ConvexProvider` / `ConvexReactClient` and use `useQuery`, `useMutation`, `useAction`
- do server rendering with `preloadQuery` / `fetchQuery` in Next.js
- implement auth and authorisation with `ctx.auth.getUserIdentity()`
- implement file uploads (Convex file storage) or scheduled jobs (scheduler / cron)
- deploy to production and set correct env vars for frontend + backend

---

## Default assumptions (override when project dictates)

- **Next.js App Router** (there is a Pages Router variant—see “Pages Router notes”)
- **TypeScript**
- Convex functions live in the default `convex/` folder
- “Public functions” = callable by any client (must have validators + access control)
- “Internal functions” = only callable from other Convex functions (preferred for `runQuery`, scheduling, etc.)

---

## Golden path checklist

Copy this into the task and tick it off:

- [ ] Identify Next.js router: App Router (`app/`) vs Pages Router (`pages/`)
- [ ] Install `convex` package
- [ ] Run `npx convex dev` (creates `convex/`, writes `.env.local`, generates `convex/_generated/*`)
- [ ] Create/confirm schema (`convex/schema.ts`) and required indexes
- [ ] Implement queries/mutations/actions with **argument validators** and **access control**
- [ ] Wire provider (`ConvexProvider` + `ConvexReactClient`) in a client boundary
- [ ] Call functions from UI using typed `api` references
- [ ] If using server rendering: use `preloadQuery` + `usePreloadedQuery` (reactive) or `fetchQuery` (non-reactive)
- [ ] Add file storage / scheduling / HTTP actions if needed
- [ ] Add error handling (client) and application errors (`ConvexError` or union returns)
- [ ] Add tests with `convex-test` for function logic
- [ ] Prep deployment: set `NEXT_PUBLIC_CONVEX_URL` (frontend) and dashboard env vars (backend)
- [ ] Validate with `npx convex run`, `npx convex logs`, and dashboard data/functions

---

# 1) Project setup

## Option A: scaffold quickly (recommended for greenfield)

```bash
npm create convex@latest
```

This scaffolds a Next.js + Convex app and wires defaults. Use this when there is no existing Next.js project.

## Option B: add Convex to an existing Next.js app (manual)

```bash
npm install convex
npx convex dev
```

`npx convex dev` will:
- prompt for GitHub login and create/link a Convex project
- create the `convex/` folder
- keep running to sync changes to your dev deployment
- generate types in `convex/_generated/*`

### Environment variables (frontend vs backend)

- **Frontend (Next.js):** `NEXT_PUBLIC_CONVEX_URL` must be set to the Convex deployment URL. `npx convex dev` typically writes this to `.env.local`.
- **Backend (Convex functions):** use env vars configured in the Convex Dashboard and read them via `process.env`. Do **not** rely on Next.js `.env*` files for backend secrets.

---

# 2) Next.js App Router integration (client side)

## 2.1 Create a provider boundary

Create `app/ConvexClientProvider.tsx`:

```tsx
"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import { ReactNode } from "react";

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClientProvider({ children }: { children: ReactNode }) {
  return <ConvexProvider client={convex}>{children}</ConvexProvider>;
}
```

Wire it in `app/layout.tsx`:

```tsx
import { ConvexClientProvider } from "./ConvexClientProvider";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ConvexClientProvider>{children}</ConvexClientProvider>
      </body>
    </html>
  );
}
```

## 2.2 Use Convex hooks in Client Components only

Any component that calls `useQuery`, `useMutation`, or `useAction` must be a Client Component:

```tsx
"use client";

import { useQuery, useMutation } from "convex/react";
import { api } from "../convex/_generated/api";

export function Tasks() {
  const tasks = useQuery(api.tasks.get); // undefined while loading
  const createTask = useMutation(api.tasks.create);

  if (tasks === undefined) return <div>Loading...</div>;

  return (
    <div>
      {tasks.map((t) => (
        <div key={t._id}>{t.text}</div>
      ))}
      <button onClick={() => void createTask({ text: "New task" })}>
        Add
      </button>
    </div>
  );
}
```

**Loading semantics:**
- `useQuery(...)` returns `undefined` while loading.
- If the query returns `undefined` on the server, the client receives `null`.

---

# 3) Schema design (`convex/schema.ts`)

## 3.1 Define tables with validators

Use `defineSchema`, `defineTable`, and `v` validators:

```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  })
    .index("by_isCompleted", ["isCompleted"]),
});
```

Notes:
- Convex automatically adds `_id` and `_creationTime`.
- Prefer `Id<"table">` for foreign keys and references.

## 3.2 Index strategy

Rules of thumb:
- If a query can touch **1000+** docs or is **unbounded**, design an index and use `.withIndex(...)`.
- Avoid redundant indexes where one is a prefix of another unless you need the implicit `_creationTime` ordering behaviour.

---

# 4) Writing Convex functions

Convex functions live in `convex/*.ts` and are deployed by `npx convex dev` / `npx convex deploy`.

## 4.1 Choose the right function type

| Need | Use | Can access DB directly? | Network calls? | Deterministic? |
|---|---|---:|---:|---:|
| Read data | `query` | ✅ | ❌ | ✅ |
| Write data (transaction) | `mutation` | ✅ | ❌ | ✅ |
| Side effects / third-party APIs | `action` | ❌ (use `ctx.runQuery/runMutation`) | ✅ | ❌ |
| Public HTTP endpoint/webhook | `httpAction` | ❌ (use `ctx.runQuery/runMutation`) | ✅ | ❌ |

## 4.2 Queries

Example `convex/tasks.ts`:

```ts
import { query } from "./_generated/server";

export const get = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("tasks").collect();
  },
});
```

## 4.3 Mutations (atomic writes)

```ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: { text: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", { text: args.text, isCompleted: false });
  },
});
```

Important:
- Writes inside a mutation are atomic; avoid partial-state bugs by keeping related writes in one mutation.
- **Prefer explicit table name** when calling `ctx.db.get/patch/replace/delete`:

```ts
await ctx.db.patch("tasks", taskId, { isCompleted: true });
```

## 4.4 Actions (side effects, runtimes, and best practice patterns)

Actions can call third-party APIs via `fetch` and interact with the database by calling queries/mutations via `ctx.runQuery` / `ctx.runMutation`.

```ts
import { action, internalQuery } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

export const doSomething = action({
  args: { a: v.number() },
  handler: async (ctx, args) => {
    const data = await ctx.runQuery(internal.myFunctions.readData, { a: args.a });
    // ... call external API, then write results ...
    await ctx.runMutation(internal.myFunctions.writeData, { a: args.a, data });
  },
});

export const readData = internalQuery({
  args: { a: v.number() },
  handler: async (ctx, args) => {
    // read from ctx.db here
    return null;
  },
});
```

### Picking the runtime (“use node”)

- Default: actions run in Convex’s fast runtime (browser-like APIs; no cold starts).
- If you need Node-only APIs or unsupported npm deps, put `"use node";` at the top of the file.

Constraints:
- A `"use node"` file may contain **actions only** (no queries/mutations).
- Non-node files must not import node files.

### Recommended pattern: mutation schedules action

Calling actions directly from clients is often an anti-pattern. Prefer:

1) client calls a mutation to write “intent” into DB  
2) mutation schedules an internal action (`runAfter(0, ...)`) to do side effects

This prevents duplicate execution and lets the mutation enforce invariants.

---

# 5) Access control and authentication

## 5.1 Minimum bar for public functions

Every public `query`, `mutation`, `action`, and `httpAction` should have:
- **argument validators**
- **some form of access control**

Typical access control uses:

```ts
const identity = await ctx.auth.getUserIdentity();
if (identity === null) throw new Error("Unauthorised");
```

Do not use spoofable inputs (like email) as the only access control check.

## 5.2 Store users in your Convex database (common pattern)

Many apps store a `users` table keyed by identity and then reference user IDs from other docs.

Pattern:
- create a helper `getCurrentUserOrThrow(ctx)` that loads/creates the user doc
- reference `user._id` in other tables (`messages.userId`, etc.)

Also consider a client helper that combines auth state with “user doc exists” checks.

## 5.3 Next.js server rendering with auth tokens

When using `preloadQuery` / `fetchQuery` from server-side Next.js code, pass `{ token }` in the third options argument.

Token retrieval depends on your auth provider (Clerk/Auth0/etc.). Keep token handling server-side.

---

# 6) Next.js server rendering (App Router)

Use these when you need SSR or want to call Convex from Server Components / Server Actions.

## 6.1 Preload data for Client Components (reactive after hydration)

Server Component:

```ts
import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { Tasks } from "./Tasks";

export async function TasksWrapper() {
  const preloaded = await preloadQuery(api.tasks.list, { list: "default" });
  return <Tasks preloadedTasks={preloaded} />;
}
```

Client Component:

```tsx
"use client";

import { Preloaded, usePreloadedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function Tasks(props: { preloadedTasks: Preloaded<typeof api.tasks.list> }) {
  const tasks = usePreloadedQuery(props.preloadedTasks);
  return <div>{/* render tasks */}</div>;
}
```

Notes:
- `preloadQuery` uses `cache: "no-store"` and will prevent static rendering for that Server Component.
- Avoid multiple `preloadQuery` calls in one render tree; the underlying HTTP client is stateless and data may be inconsistent. Prefer “one query that returns all needed data”.

## 6.2 Render pure Server Components (non-reactive)

Use `fetchQuery` in Server Components when reactivity is not needed.

## 6.3 Server Actions and Route Handlers

Use `fetchMutation` / `fetchAction` / `fetchQuery` from `convex/nextjs` inside:
- Server Actions (`"use server"`)
- Route Handlers (`app/api/.../route.ts`)

After server-side mutations, call `revalidatePath(...)` (or related cache invalidation) so Next.js updates the page.

## 6.4 Deployment URL for server-side Convex calls

`preloadQuery`, `fetchQuery`, `fetchMutation`, `fetchAction` require either:
- `NEXT_PUBLIC_CONVEX_URL` set, or
- passing `{ url }` explicitly in the third options argument

---

# 7) File Storage (uploads and serving)

## 7.1 Upload via short-lived upload URL (scales to large files)

3-step client flow:
1) call a mutation to generate an upload URL (`ctx.storage.generateUploadUrl()`)
2) `POST` the file to the returned URL → receive `storageId`
3) call another mutation to save `storageId` into a document

Example mutation:

```ts
import { mutation } from "./_generated/server";

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    return await ctx.storage.generateUploadUrl();
  },
});
```

Upload URLs expire (fetch shortly before upload). Use the generating mutation to enforce “who can upload”.

## 7.2 Serve via `ctx.storage.getUrl` (simple)

In a query/mutation/action, turn `Id<"_storage">` into a URL:

```ts
const url = await ctx.storage.getUrl(storageId);
```

Return the URL alongside your data and render it in `<img src={url} />`.

## 7.3 Serve via HTTP action (access control at request time)

If you need access control at serve-time, implement an `httpAction` that loads the blob via `ctx.storage.get(...)` and returns a `Response`.

Note: HTTP action responses have a size limit (use URLs for larger files).

---

# 8) Scheduling (durable background work)

Use `ctx.scheduler.runAfter(delayMs, fn, args)` or `ctx.scheduler.runAt(timestampMs, fn, args)` from mutations or actions.

Example: schedule self-destruct in 5 seconds:

```ts
import { mutation, internalMutation } from "./_generated/server";
import { internal } from "./_generated/api";
import { v } from "convex/values";

export const sendExpiringMessage = mutation({
  args: { body: v.string(), author: v.string() },
  handler: async (ctx, args) => {
    const id = await ctx.db.insert("messages", args);
    await ctx.scheduler.runAfter(5000, internal.messages.destruct, { messageId: id });
  },
});

export const destruct = internalMutation({
  args: { messageId: v.id("messages") },
  handler: async (ctx, args) => {
    await ctx.db.delete("messages", args.messageId);
  },
});
```

Key constraints:
- A single function can schedule up to **1000** functions, total arg size **8MB**
- Auth is **not propagated** to scheduled functions; pass required user info explicitly
- Prefer scheduling **internal** functions (`internal.*`) rather than public `api.*`

---

# 9) Error handling

## 9.1 Client-side: Error boundaries

Wrap your React app (or subtrees) in an Error Boundary so query errors don’t white-screen the whole app.

## 9.2 Expected failures: return unions or throw `ConvexError`

For expected error conditions you can:
- return a union type (TypeScript-enforced handling)
- or throw `ConvexError` so clients can handle it like other errors

Notes:
- Throwing an error in a mutation prevents the transaction from committing.
- `runQuery`, `runMutation`, and `runAction` calls in actions will propagate thrown errors.

---

# 10) Testing Convex functions (fast unit tests)

Use `convex-test` to run functions against a mock backend.

Typical stack:
- `vitest`
- `convex-test`
- `@edge-runtime/vm`

Example pattern:
- import your schema
- import all modules via `import.meta.glob("./**/*.ts")`
- call `t.query(api.foo.bar)` / `t.mutation(...)`

Always still do a manual end-to-end smoke test; the mock runtime differs from the real Convex runtime.

---

# 11) CLI workflows (debugging + ops)

Common commands:

```bash
npx convex dev              # sync functions + generate types
npx convex dashboard        # open dashboard
npx convex run <fn> <args>  # run a function with JSON args
npx convex logs             # tail logs
npx convex deploy           # deploy to prod
npx convex env list         # view backend env vars
npx convex env set KEY val  # set backend env var
npx convex import --table <t> file.jsonl  # import data
```

Tips:
- Use `npx convex run ... --watch` for live-updating query output during debugging.
- If auth seems broken, log `await ctx.auth.getUserIdentity()` in a function and check dashboard logs.

---

# 12) Best practices (the “don’t regret it later” list)

- Always `await` promises (`ctx.db.*`, `ctx.scheduler.*`, etc.)
- Prefer `.withIndex` / `.withSearchIndex` over `.filter` on database queries
- Only call `.collect()` when the result set is guaranteed small; otherwise use indexes, `.take`, or `.paginate`
- Don’t use `Date.now()` inside queries (it can produce stale results); model time as data or pass time as a coarse query arg
- Use argument validators for all public functions (optionally enforce with ESLint rules)
- Apply access control to every public function (`ctx.auth.getUserIdentity()` or unguessable IDs)
- Only schedule and `ctx.run*` **internal** functions
- In actions, batch DB access; avoid sequential `ctx.runQuery` / `ctx.runMutation` calls unless intentional
- In actions, use `ctx.runAction` only when crossing runtimes; prefer plain TS helpers otherwise
- Prefer granular mutations (e.g. `setTeamName`) over “god” updates (e.g. `updateTeam`) to simplify access control

---

# 13) Pages Router notes (when the repo uses `pages/`)

If the project uses Pages Router (has `pages/` and no `app/`), use the Pages Router quickstart and Next.js Pages Router docs.

Key difference:
- Provider wiring happens in `pages/_app.tsx` rather than `app/layout.tsx`.
- Server-side rendering patterns differ; use the Pages Router guide for SSR/auth specifics.

---

## THE EXACT PROMPT — “Convex + Next.js Implementation Plan”

Use this prompt when you want the agent to plan before coding:

```text
You are implementing Convex in a Next.js project.

1) Identify whether this repo uses App Router or Pages Router.
2) Propose the data model and schema (tables + indexes).
3) List the Convex functions you will create (queries, mutations, actions, HTTP actions),
   including which are public vs internal, with validators and access control.
4) Show how the Next.js app will call these functions (client hooks and/or server rendering).
5) Identify any auth/token requirements and where they are enforced.
6) Call out performance risks (indexes, .collect usage, pagination) and how you’ll mitigate them.
7) Provide a step-by-step implementation checklist and then implement the code.
```

