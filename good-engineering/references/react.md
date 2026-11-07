# React and React Native

Everything in [typescript](typescript.md) applies. These are the mistakes specific to
components, hooks and mobile.

## State has one home

| Kind of state | Lives in |
| --- | --- |
| Server or remote data | TanStack Query (or the project's data layer), keyed by its inputs. Not `useState` + `useEffect` |
| Derivable from props or other state | Computed during render. Not stored |
| URL-addressable (tab, filter, selected id) | The router's params or search params |
| Form input | The form library or local state, parsed on submit |
| Shared client state | A small store (Zustand, context plus reducer) with typed actions |
| Persisted on device | MMKV, SQLite or AsyncStorage behind one module with a schema version |

- **Never mirror props into state** to "keep them in sync". Compute the value, or key
  the component (`key={id}`) to reset it.
- **Async UI state is a discriminated union** (`idle | loading | ready | failed`), or
  the query library's status, never three booleans.
- Reducers own transitions. Components dispatch events (`"saveClicked"`) rather than
  setting fields directly.

## Effects are for syncing with external systems

`useEffect` is for subscriptions, timers, imperative APIs, analytics and native
modules: things outside React. It is not for deriving data, handling a click, or
chaining state updates.

- Every effect that subscribes returns a cleanup that unsubscribes. StrictMode runs
  effects twice in development to prove the cleanup works. Don't disable it.
- Effects that fetch must ignore stale results:

  ```ts
  useEffect(() => {
    const controller = new AbortController();
    const live = () => !controller.signal.aborted;
    setState({ kind: "loading" });
    load(id, controller.signal).then(
      (data) => { if (live()) setState({ kind: "ready", data }); },
      (error) => { if (live()) setState({ kind: "failed", error }); },
    );
    return () => controller.abort();
  }, [id]);
  ```

  Use a query library for this instead whenever one is available.
- Dependency arrays are complete. Satisfy `react-hooks/exhaustive-deps` by restructuring;
  never silence it. A stale closure is a real bug.
- Event handlers do the work caused by an event. Effects do the work caused by
  being on screen.

## Rendering

- With React Compiler on, don't add `useMemo`, `useCallback` or `memo` by hand.
  Without it, add them only where a profile shows a cost or a referentially stable
  value is part of a contract (an effect dependency, a memoised child).
- List keys are stable ids from the data, never the array index for lists that
  reorder, insert or delete.
- Move data fetching and decisions out of a component into hooks or plain functions
  when that makes them reusable or testable without rendering. A small, cohesive
  component can keep all three.

## React Native

- **The JS thread is the bottleneck.** Keep parsing, sorting and image work off it.
  Run animations and gestures on the UI thread with Reanimated worklets and shared
  values, not `setState` per frame.
- Lists: `FlashList` or `FlatList` with a stable `keyExtractor`, memoised row
  components and no inline heavy work in `renderItem`. Never `ScrollView` over an
  unbounded array.
- Navigation params are serialisable ids, not objects or functions. Load the object by
  id on the destination screen.
- Screens stay mounted in stacks. Subscriptions and timers tied to visibility belong in
  `useFocusEffect`, not `useEffect`.
- Platform differences go in `.ios.tsx` / `.android.tsx` files or behind one module, not
  `Platform.OS` checks scattered through components.
- Persisted data carries a schema version and a migration path; app updates load old
  data.
- Handle app state: background, kill and cold start mid-operation. Pending writes
  survive in a persisted queue (the outbox in [state](state.md)).
- Permissions, network and keyboard are states the UI models, not edge cases.
- Test logic with Jest or Vitest and components with React Native Testing Library,
  queried by role and text. Verify flows on a real simulator or emulator; a passing
  unit test doesn't show the screen works.

## Testing components

- Query by role, label and text as a user would (`getByRole("button", { name: "Save" })`),
  never by test ids for things users can see, and never by component internals.
- Assert what the user sees and what was persisted or sent. Don't assert on hooks,
  state variables or that a callback was called with the props you just passed.
- Stub the network with `msw`. Render with the real providers (query client, router,
  store) through one `renderWithProviders` helper.
