---
name: convex-react-native-expo
description: >-
  Integrates the Convex reactive backend into React Native apps built with Expo (including expo-router).
  Covers Convex CLI setup, Expo/EAS environment variables, server functions (queries/mutations/actions),
  schema + indexes, generated types, and React hooks (useQuery/useMutation/useAction).
  Use when adding, fixing, or deploying Convex in an Expo project or when working with EXPO_PUBLIC_CONVEX_URL,
  ConvexProvider/ConvexReactClient, or realtime data flows.
---

# Convex in React Native (Expo) — Agent Skill

## Why this exists
Expo + React Native has a couple of “gotchas” compared to web React when integrating Convex:

- You **must** configure the deployment URL as `EXPO_PUBLIC_CONVEX_URL` and make it available both locally and in EAS builds. (Expo reads `EXPO_PUBLIC_*` variables at runtime/build time.)  
- You should initialise `ConvexReactClient` with `unsavedChangesWarning: false` in Expo/React Native projects.  
- `npx convex dev` does more than start “a server”: it creates/configures the project, creates the `convex/` backend folder, and keeps **generated types** up to date in `convex/_generated`.  

This skill is a repeatable, “copy/paste safe” workflow to add Convex to an Expo project and keep the frontend and backend in sync.

---

## When to use this skill (triggers)
Use this skill when the user asks for any of:

- “Add Convex to my Expo / React Native app”
- “Set up `npx convex dev` / Convex CLI”
- “How do I set `EXPO_PUBLIC_CONVEX_URL` / EAS env vars for Convex?”
- “Write a Convex query/mutation/action for my Expo app”
- “Type-safe `api` generation / `convex/_generated` issues”
- “Realtime subscriptions with `useQuery` in React Native”
- “Deploy Convex + build the Expo app”

---

## Core mental model (Convex basics)
Convex is a reactive database + hosted server functions:

- **Queries**: read data; cached + subscribable (realtime/reactive).  
- **Mutations**: write data; run as a transaction.  
- **Actions**: call external APIs/services; can’t access the DB directly—use `ctx.runQuery`/`ctx.runMutation` (or schedule work via `ctx.scheduler`).  

> Convex functions are written in TypeScript/JavaScript inside the `convex/` directory and become API endpoints automatically.

---

# Quick start workflow (new Expo app)

> Goal: a running Expo app displaying data from Convex in <10 minutes.

### 1) Create the Expo app
```bash
npx create-expo-app my-app
cd my-app
```

### 2) Install Convex (Expo-friendly)
Expo’s integration guide recommends:
```bash
npx expo install convex
```

(Using `npm install convex` also works; Expo just prefers `expo install` to match SDK versions.)

### 3) Create a Convex dev deployment and generate backend scaffolding
```bash
npx convex dev
```

This prompts you to log in, creates a Convex project, saves your URLs, and creates `convex/` for backend functions. Leave it running to sync changes. It also updates generated types in `convex/_generated` as you edit functions/schema.

### 4) Ensure `EXPO_PUBLIC_CONVEX_URL` exists locally
After `npx convex dev`, you should have a `.env.local` containing `EXPO_PUBLIC_CONVEX_URL=...` for the client, and `CONVEX_DEPLOYMENT=...` for the CLI.

### 5) (Optional) Seed sample data
Create `sampleData.jsonl`:
```jsonl
{"text": "Buy groceries", "isCompleted": true}
{"text": "Go for a swim", "isCompleted": true}
{"text": "Integrate Convex", "isCompleted": false}
```

Import to a `tasks` table:
```bash
npx convex import --table tasks sampleData.jsonl
```

### 6) Add a query function (backend)
`convex/tasks.ts`
```ts
import { query } from "./_generated/server";

export const get = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("tasks").collect();
  },
});
```

### 7) Wire the app to Convex (Expo Router)
In your root layout (path depends on your template, commonly `app/_layout.tsx` or `src/app/_layout.tsx`):

```tsx
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Stack } from "expo-router";

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!, {
  unsavedChangesWarning: false,
});

export default function RootLayout() {
  return (
    <ConvexProvider client={convex}>
      <Stack>
        <Stack.Screen name="index" />
      </Stack>
    </ConvexProvider>
  );
}
```

### 8) Display data with `useQuery`
`app/index.tsx` (or `src/app/index.tsx`):
```tsx
import { api } from "@/convex/_generated/api";
import { useQuery } from "convex/react";
import { Text, View } from "react-native";

export default function Index() {
  const tasks = useQuery(api.tasks.get);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      {tasks?.map(({ _id, text }) => (
        <Text key={_id}>{text}</Text>
      ))}
    </View>
  );
}
```

### 9) Start the Expo app
```bash
npm start
```

---

# Expo + EAS environment variable workflow (production/preview/dev builds)

`npx convex dev` writes `EXPO_PUBLIC_CONVEX_URL` into `.env.local`. That works for local development, but **EAS builds don’t automatically read your local `.env.local`**.

Expo’s guide recommends creating an EAS environment variable:

```bash
eas env:create   --name EXPO_PUBLIC_CONVEX_URL   --value https://YOUR_DEPLOYMENT_URL.convex.cloud   --visibility plaintext   --environment production   --environment preview   --environment development
```

Replace the URL with the value of `EXPO_PUBLIC_CONVEX_URL` from `.env.local`.

---

# Building features: server functions + client hooks

## A) Queries (read)
Queries live in `convex/` and are called from React/React Native using `useQuery`.

### Query rules
- Keep queries **deterministic** (given the same args, return the same result).
- Queries are cached + realtime; they rerun when underlying data changes.

### Typical query with validators + an index
`convex/tasks.ts`
```ts
import { query } from "./_generated/server";
import { v } from "convex/values";

export const listByListId = query({
  args: { taskListId: v.id("taskLists") },
  handler: async (ctx, { taskListId }) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_task_list_id", (q) => q.eq("taskListId", taskListId))
      .order("desc")
      .take(100);
  },
});
```

### On the client: loading state
`useQuery` returns `undefined` while loading:
```tsx
const tasks = useQuery(api.tasks.listByListId, { taskListId });
// tasks === undefined initially
```

### Conditionally skipping a query
If you don’t yet have args (e.g. route param), pass `"skip"` instead of args:
```tsx
const tasks = useQuery(api.tasks.listByListId, taskListId ? { taskListId } : "skip");
```

---

## B) Mutations (write)
Mutations are transactional writes. They are called from React Native with `useMutation`, which returns an async function.

### Example mutation
`convex/tasks.ts`
```ts
import { mutation } from "./_generated/server";
import { v } from "convex/values";

export const create = mutation({
  args: { text: v.string() },
  handler: async (ctx, { text }) => {
    const id = await ctx.db.insert("tasks", { text });
    return id;
  },
});
```

### Client usage
```tsx
import { useMutation } from "convex/react";
import { api } from "@/convex/_generated/api";

const createTask = useMutation(api.tasks.create);

await createTask({ text: "New task" });
```

### Error handling
- Query errors are thrown from `useQuery` call sites; handle with a React **error boundary**.
- Mutation errors reject the promise; handle with `try/catch` or `.catch(...)`.

---

## C) Actions (external APIs / side effects)
Convex queries and mutations **cannot** call `fetch` to the outside world. Use **actions** for external calls, and then write results via mutations.

### Action basics
- Actions can call `fetch` and third-party services.
- To access data, call queries/mutations via `ctx.runQuery` / `ctx.runMutation`, or schedule work with `ctx.scheduler`.
- Actions from a single client are parallelised; await previous calls if ordering matters.
- Actions do **not** have automatic retries or optimistic updates.

### Recommended pattern
In most apps, **don’t call actions directly from the client**. Prefer:
1) Client calls a mutation capturing user intent (write a record, enforce invariants).
2) That mutation schedules an internal action.
3) The action calls the external API and writes results via a mutation.

---

# Data modelling essentials (schema, tables, IDs, indexes)

## Tables
Tables are created automatically the first time you insert into them:
```ts
await ctx.db.insert("friends", { name: "Jamie" });
// creates `friends` table if it didn’t exist
```

## Schemas (recommended for production)
Schemas are optional, but strongly recommended to ensure data consistency and type safety.

`convex/schema.ts`
```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  }),
});
```

## Indexes (use early on hot paths)
Define indexes in the schema via `.index(...)` and query with `.withIndex(...)`.

`convex/schema.ts`
```ts
export default defineSchema({
  messages: defineTable({
    channel: v.id("channels"),
    body: v.string(),
    user: v.id("users"),
  })
    .index("by_channel", ["channel"])
    .index("by_channel_user", ["channel", "user"]),
});
```

Key rules:
- Indexes are created during `npx convex dev` and `npx convex deploy`.
- `withIndex` ranges must step through index fields in order.
- If you use `withIndex` without a range expression, avoid full scans by pairing it with `.first()`, `.unique()`, `.take(n)`, or `.paginate(...)`.

---

# Generated code + type safety

## What gets generated
Convex generates app-specific code in `convex/_generated/` (e.g. `api.js/api.d.ts`, `dataModel.d.ts`, `server.js/server.d.ts`).

## How it’s generated
- `npx convex dev` generates/updates it automatically (and keeps it in sync while running).
- `npx convex codegen` regenerates it (useful in CI).

## Important repo rule
Commit `convex/_generated` to your repository. TypeScript builds won’t typecheck without it.

---

# Deployment workflow (backend + Expo builds)

## Deploy Convex functions
```bash
npx convex deploy
```

This typechecks functions, regenerates `convex/_generated`, bundles dependencies, and pushes functions/indexes/schema to production.

## Expo builds
- Ensure `EXPO_PUBLIC_CONVEX_URL` is set in EAS env vars for the relevant environments.
- When you cut a new backend release, **deploy Convex first**, then build your app so the frontend matches the deployed API.

---

# Debugging & common failure modes

## Symptom: app can’t connect / `EXPO_PUBLIC_CONVEX_URL` undefined
Checklist:
- `.env.local` contains `EXPO_PUBLIC_CONVEX_URL=...`
- Your code reads `process.env.EXPO_PUBLIC_CONVEX_URL` (spelling matters)
- For EAS builds, you created the EAS env var (not just local)

## Symptom: `api` import missing / stale types
Checklist:
- `npx convex dev` is running (it updates `convex/_generated`)
- Run `npx convex codegen` if needed
- Ensure `convex/_generated` is committed and not ignored

## Symptom: query throws in render
- Handle query errors with an error boundary.
- Remember: retrying a query with the same args won’t fix deterministic errors; you must fix the server function.

## Symptom: “write conflict” / OCC errors
- This often happens when many concurrent mutations update the same doc or scan large ranges.
- Reduce conflicts by narrowing reads/writes (use indexes, avoid reading huge tables in a mutation).

---

# Agent checklists (copy/paste)

## Integration checklist
- [ ] Install `convex` (`npx expo install convex`)
- [ ] Run `npx convex dev` and keep it running
- [ ] Confirm `.env.local` has `EXPO_PUBLIC_CONVEX_URL`
- [ ] Wrap app with `ConvexProvider` + `ConvexReactClient(..., { unsavedChangesWarning: false })`
- [ ] Write queries/mutations in `convex/` and import `api` from `convex/_generated/api`
- [ ] Commit `convex/_generated` to git
- [ ] For EAS: create `EXPO_PUBLIC_CONVEX_URL` environment variable for build environments
- [ ] Deploy with `npx convex deploy`

## Safe defaults for new features
- [ ] Add `v` validators (`args: { ... }`) for every public query/mutation/action
- [ ] Prefer queries for reads, mutations for writes, actions only for external calls
- [ ] Put hot-path lookups behind indexes early
- [ ] Use error boundaries for query errors; try/catch for mutations/actions

---

# References (primary docs)
- Convex docs home: https://docs.convex.dev/home
- Convex + React Native quickstart: https://docs.convex.dev/quickstart/react-native
- Expo guide: Using Convex: https://docs.expo.dev/guides/using-convex/
- Convex React client docs: https://docs.convex.dev/client/react
- Convex CLI: https://docs.convex.dev/cli
