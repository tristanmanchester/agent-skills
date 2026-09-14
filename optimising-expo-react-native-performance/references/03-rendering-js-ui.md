# JS work, React rendering, and the UI thread

Reviewed 2026-09-13. Attribute the stall before choosing a fix: a blocked JS thread, an expensive React commit, and native rendering pressure need different interventions.

## Non-urgent computation

React Native 0.87 removed InteractionManager. Use the supported global `requestIdleCallback` and `cancelIdleCallback` for bounded, interruptible non-urgent work. It still runs on the JS thread. Neither an idle callback, a promise/microtask, a transition, nor `requestAnimationFrame` makes an expensive synchronous calculation cheap or parallel.

A scheduling pattern for small independent items:

```ts
function processInIdleTime<T>(items: readonly T[], processOne: (item: T) => void) {
  let index = 0;
  let cancelled = false;
  let handle: ReturnType<typeof requestIdleCallback>;

  const schedule = () => {
    handle = requestIdleCallback((deadline) => {
      const started = performance.now();
      let processed = 0;
      while (!cancelled && index < items.length && processed < 64 &&
             performance.now() - started < 4 &&
             (deadline.timeRemaining() > 1 || (deadline.didTimeout && processed === 0))) {
        processOne(items[index++]);
        processed++;
      }
      if (!cancelled && index < items.length) schedule();
    }, { timeout: 250 });
  };
  schedule();
  return () => { cancelled = true; cancelIdleCallback(handle); };
}
```

Return the cancellation function from the owning effect. Keep the input stable for a run, and do not publish stale results after route/account/input changes. The example cannot interrupt one expensive item: subdivide that work or use an explicitly supported native/worker execution path. Test cancellation, input replacement, empty input, timeout progress, and the actual worst-case item duration. The 4 ms/64-item limits are example budgets to measure, not platform guarantees.

Use animation-frame callbacks for frame-related updates, not bulk parsing. Use transitions for non-urgent React updates, not to offload arbitrary CPU-bound work.

## Rendering

Find which state change causes the expensive commits. Narrow context subscriptions, colocate state, avoid unnecessary derived state, and stabilise genuinely hot prop boundaries. Do not add `memo`, `useMemo`, or `useCallback` to every component by reflex.

React Compiler is stable. Check generated configuration and compiler coverage before adding it; Expo configuration depends on the installed SDK. Do not automatically install a beta because an old snippet did. Follow the matching Expo guide, run the Rules of React lint checks, inspect compiler diagnostics, and compare release results. Keep manual memoisation needed for semantic identity rather than deleting it blindly.

Remove or sample high-volume debug logging on hot paths while retaining actionable errors and the application's observability pipeline. Blanket removal of every `console.*` is not a security or reliability strategy.

## UI-thread work and animation

Use system traces to distinguish native layout/drawing, decoding, compositing, and navigation work. Prefer native-stack transitions or the animation system appropriate to the app. Animate transforms/opacity when they express the design; layout animation is valid when layout actually needs to change.

For `Animated`, use `useNativeDriver: true` only for supported non-layout properties. For Reanimated, keep worklets small, avoid repeated JS/UI synchronisation, and follow the installed Reanimated/Worklets compatibility matrix. Moving a heavy computation to the UI runtime can simply move the jank.

Measure shadows, blur, translucent layers, overdraw, and texture allocation. Rasterisation and hardware-texture flags trade memory and invalidation cost for rendering work; do not enable them globally or assume they are enabled by default.

## Primary sources

- [React Native 0.87 release and removals](https://reactnative.dev/blog/2026/08/11/react-native-0.87)
- [requestIdleCallback](https://reactnative.dev/docs/global-requestIdleCallback)
- [React Compiler stable release](https://react.dev/blog/2025/10/07/react-compiler-1)
- [Expo React Compiler integration](https://docs.expo.dev/guides/react-compiler/)
- [React Native performance](https://reactnative.dev/docs/performance)
