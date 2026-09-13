# Profiling without confusing diagnosis and measurement

## Two different jobs

**Diagnosis:** React Native DevTools in a compatible Hermes diagnostic build can locate long JS tasks, expensive React commits, retained JS objects, and supported network events. Use it to form and falsify hypotheses. A profiler, development checks, debugger attachment, and network inspection add overhead.

**Performance acceptance:** measure the shipping configuration on representative physical devices, with developer tools disconnected. Use native profilers or an explicitly configured release/profileable build when a trace is required, and record the instrumentation. Do not compare an instrumented development baseline with an uninstrumented release candidate.

`debugOptimized` can be useful for debugging with more native optimisation; it is not a store-equivalent release build. Simulator results do not establish performance on a low-end phone.

## Choose evidence for the suspected cost

| Suspected cost | Evidence |
|---|---|
| JS work or React commits | RN DevTools Performance/Profiler panels; supported runtime traces |
| Retained JS objects | Before/after heap snapshots after the same stress loop |
| Main thread, RenderThread, scheduling, I/O | Android system trace / Perfetto on a suitable profileable build |
| Native CPU/layout/allocations | Xcode Instruments Time Profiler, Allocations, and appropriate platform instruments |
| Native media/image memory | Native allocations and footprint, not only JS heap |
| Network waiting | Application spans plus provider/server timings; account for gaps in DevTools network coverage |

Availability depends on the installed RN version. The modern Performance and Network panels arrived in RN 0.83; older runtime documentation or a web-browser DevTools screenshot does not establish support. Expo-specific networking can have a different inspection path. A quiet network panel does not prove that no requests occurred.

## Repeatable protocol

Record the exact commit, lockfile, device/OS, native and JS build flags, profiler version, thermal/battery conditions, cache state, dataset, and scenario. Define start/end events before measuring startup or navigation. Repeat enough times to see variability; interleave baseline and candidate runs and report sample count. Use the same warm-up policy for both.

For memory, repeat navigation or scrolling, allow a consistent settling interval, and inspect retained objects or resource ownership. A cache growing then plateauing is different from a leak; garbage collection timing can distort single snapshots.

Save raw traces and a small before/after table. Redact private URLs, request bodies, tokens, and user data before sharing. When instrumentation is unavailable, report that limitation and supply reproduction steps instead of inventing a trace or benchmark.

## Primary sources

Reviewed 2026-09-13:

- [React Native DevTools](https://reactnative.dev/docs/react-native-devtools)
- [React Native performance](https://reactnative.dev/docs/performance)
- [Expo debugging tools](https://docs.expo.dev/debugging/tools/)
