# Next.js SSR, Server Components, Server Actions (App Router)

## Use cases
- **Faster first paint** without giving up reactivity: `preloadQuery` → `usePreloadedQuery`.
- **Server-only reads** (non-reactive): `fetchQuery`.
- **Server Actions / Route Handlers** to mutate from the server: `fetchMutation` / `fetchAction`.

## Preloading data for a reactive Client Component
Server component:
```tsx
import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { TasksClient } from "./TasksClient";

export default async function Page() {
  const preloaded = await preloadQuery(api.tasks.list, { list: "default" });
  return <TasksClient preloaded={preloaded} />;
}
```

Client component:
```tsx
"use client";
import { Preloaded, usePreloadedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function TasksClient(props: { preloaded: Preloaded<typeof api.tasks.list> }) {
  const tasks = usePreloadedQuery(props.preloaded);
  return <div>{tasks.length}</div>;
}
```

## Server Actions and Route Handlers
Server Action:
```tsx
import { fetchMutation, fetchQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";

async function createTask(formData: FormData) {
  "use server";
  await fetchMutation(api.tasks.create, { text: String(formData.get("text")) });
}
```

Route Handler:
```ts
import { fetchMutation } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const { text } = await req.json();
  await fetchMutation(api.tasks.create, { text });
  return NextResponse.json({ ok: true });
}
```

## Authentication on the server
- To make authenticated `preloadQuery` / `fetchQuery` calls, pass `{ token }` in the third argument.
- How you acquire the token depends on the auth provider (e.g., Clerk/Auth0 Next.js SDKs).

## Deployment URL
- `convex/nextjs` helpers assume `NEXT_PUBLIC_CONVEX_URL` is set OR you pass an explicit `url` option.

## Consistency caveat
- `preloadQuery`/`fetchQuery` use a stateless HTTP client; multiple calls in one render aren’t guaranteed consistent.
- If consistency matters, avoid multiple independent `preloadQuery` calls on a single page.
