# Next.js client and server boundaries

## Non-negotiable boundary
React hooks from `convex/react` belong in Client Components:
- `useQuery`
- `useMutation`
- `useAction`
- `usePaginatedQuery`
- `usePreloadedQuery`

If a file uses those hooks, add `"use client"`.

## Reactive-first page with server preloading
Server Component:
```tsx
import { preloadQuery } from "convex/nextjs";
import { api } from "@/convex/_generated/api";
import { TasksClient } from "./TasksClient";

export default async function Page() {
  const tasks = await preloadQuery(api.tasks.listRecent, {});
  return <TasksClient preloaded={tasks} />;
}
```

Client Component:
```tsx
"use client";

import { Preloaded, usePreloadedQuery } from "convex/react";
import { api } from "@/convex/_generated/api";

export function TasksClient({
  preloaded,
}: {
  preloaded: Preloaded<typeof api.tasks.listRecent>;
}) {
  const tasks = usePreloadedQuery(preloaded);
  return <div>{tasks.length}</div>;
}
```

## Server-only reads
When the page does not need live reactivity after render, use:
```ts
import { fetchQuery } from "convex/nextjs";
```

## Server Actions and Route Handlers
Use server-side helpers for non-client calls:
- `fetchQuery`
- `fetchMutation`
- `fetchAction`

Example Server Action:
```tsx
import { fetchMutation } from "convex/nextjs";
import { api } from "@/convex/_generated/api";

export async function createTask(formData: FormData) {
  "use server";

  await fetchMutation(api.tasks.create, {
    title: String(formData.get("title")),
  });
}
```

## Authenticated server calls
If a server component, server action, or route handler needs authenticated access:
- obtain the provider token on the server
- pass `{ token }` as the third argument to `preloadQuery`, `fetchQuery`, `fetchMutation`, or `fetchAction` as needed

## Consistency note
Multiple independent server-side Convex fetches during one render are not guaranteed to be consistent with one another. If consistency matters, avoid building the page from many unrelated server fetches.

## Common mistakes
- calling `useQuery` in `app/page.tsx` without `"use client"`
- creating multiple `ConvexReactClient` instances per render instead of once at module scope
- mixing client-only auth helpers into Server Components
- trying to use server helpers without `NEXT_PUBLIC_CONVEX_URL` or an explicit URL
