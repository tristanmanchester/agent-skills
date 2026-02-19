# Frontend patterns (Expo / React Native)

## Where to put the provider
### expo-router
Wrap the entire tree in `app/_layout.tsx` (or `src/app/_layout.tsx`):

```tsx
<ConvexProvider client={convex}>
  <Stack />
</ConvexProvider>
```

### Non-router
Wrap the top-level navigation root in `App.tsx`.

## `useQuery` lifecycle
- `useQuery(...)` returns:
  - `undefined` while loading (initially)
  - a value once loaded (often an array)
  - re-renders automatically on relevant backend changes

Always handle `undefined` explicitly:

```tsx
const tasks = useQuery(api.tasks.get);
if (tasks === undefined) return <ActivityIndicator />;
```

## `useMutation` lifecycle
Mutations return a function you call:

```tsx
const addTask = useMutation(api.tasks.add);
await addTask({ text: "Hello" });
```

Use optimistic UI on the client only if needed; often the real-time re-query is enough.

## Navigation + auth loading states
If your app has auth, route based on:
- Auth loading (show splash)
- Signed in vs signed out

Convex’s React helpers include components like `Authenticated`, `Unauthenticated`, and `AuthLoading` (see upstream docs in `references/sources.md`).

## Keeping the DX smooth
- Run `npx convex dev` in one terminal.
- Run `npx expo start` (or `npm start`) in another.
- If `convex/_generated` looks stale, confirm `npx convex dev` is running and has no TS errors.

