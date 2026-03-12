# Frontend patterns for Expo + Convex

Use this reference when wiring the Convex client into an Expo app and when connecting screens to backend functions.

## Root provider placement

### Expo Router

Mount the provider in `app/_layout.tsx` or `src/app/_layout.tsx`.

```tsx
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Stack } from "expo-router";

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!, {
  unsavedChangesWarning: false,
});

export default function RootLayout() {
  return (
    <ConvexProvider client={convex}>
      <Stack />
    </ConvexProvider>
  );
}
```

### Classic `App.tsx`

Wrap the navigation container or root screen tree in the same provider.

## One client only

Create the client once at module scope.

Bad:

```tsx
export default function App() {
  const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!);
  return <ConvexProvider client={convex}>{/* ... */}</ConvexProvider>;
}
```

Why it is bad:

- recreates the client on render,
- breaks subscriptions,
- makes debugging confusing.

## `useQuery` lifecycle

`useQuery(...)` behaves like this:

- `undefined` during the initial load,
- a real value once the query returns,
- reactive updates afterwards.

Always handle the loading phase explicitly.

```tsx
const project = useQuery(api.projects.byId, { projectId });

if (project === undefined) {
  return <ActivityIndicator />;
}
```

## `useMutation`

Mutations return a callable function.

```tsx
const createTask = useMutation(api.tasks.create);

await createTask({
  projectId,
  title: "Draft landing page",
});
```

Tips:

- trim user input before sending,
- disable repeated taps while a mutation is in flight when needed,
- rely on reactivity instead of manually refetching whenever possible.

## `useAction`

Use when the backend function is an action.

Typical cases:

- AI or summarisation,
- export or import jobs,
- external service calls,
- Stripe, email, or webhook tooling.

```tsx
const runSummary = useAction(api.aiActions.generateAndStoreSummary);
await runSummary({ noteId });
```

## Paginated lists

For feeds, inboxes, chat history, or large tables, pair a paginated query with `usePaginatedQuery`.

```tsx
import { usePaginatedQuery } from "convex/react";

const { results, status, loadMore } = usePaginatedQuery(
  api.notifications.listMine,
  {},
  { initialNumItems: 20 },
);
```

### Expo / React Native list pattern

```tsx
import { ActivityIndicator, FlatList, Pressable, Text, View } from "react-native";

export function NotificationsScreen() {
  const { results, status, loadMore } = usePaginatedQuery(
    api.notifications.listMine,
    {},
    { initialNumItems: 20 },
  );

  const isInitialLoading = results.length === 0 && status === "LoadingFirstPage";

  if (isInitialLoading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }

  return (
    <FlatList
      data={results}
      keyExtractor={(item) => item._id}
      renderItem={({ item }) => <Text>{item.title}</Text>}
      onEndReached={() => {
        if (status === "CanLoadMore") {
          loadMore(20);
        }
      }}
      onEndReachedThreshold={0.6}
      ListFooterComponent={
        status === "LoadingMore" ? <ActivityIndicator /> : null
      }
    />
  );
}
```

## Auth-aware rendering

If the auth integration provides Convex auth helpers, use them for UI gating:

- `Authenticated`
- `Unauthenticated`
- `AuthLoading`

These improve UX, but they are not security controls. The backend still decides access.

## Error handling in screens

Prefer three explicit states:

1. loading,
2. empty,
3. loaded with data.

Then add an error strategy appropriate for the app:

- inline message for expected issues,
- toast or banner for mutation failures,
- error boundary for render-time query failures.

A useful mental model is that Convex gives you the data transport and reactivity, but you still own product-grade UX.

## Path alias and import pitfalls

Common generated API imports:

- `../convex/_generated/api`
- `../../convex/_generated/api`
- `@/convex/_generated/api` if the project already defines that alias

Do not assume `@/` exists. Verify the project config first.

## Screen checklist

Before finishing a screen that talks to Convex:

- [ ] `useQuery` handles `undefined`.
- [ ] Mutations are awaited.
- [ ] The screen imports from generated API references.
- [ ] Empty states exist for zero-data cases.
- [ ] The list is paginated if it can grow without bound.
- [ ] Protected data is backed by server-side authorization.
- [ ] No extra Convex client is created inside the component tree.
