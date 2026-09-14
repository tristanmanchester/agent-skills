---
name: optimising-expo-react-native-performance
description: Diagnose and fix measured startup, rendering, scrolling, memory, media, or network regressions in Expo React Native apps. Use for a reproducible performance problem or an explicit performance audit, not speculative library swaps or blanket memoisation.
license: MIT
compatibility: An Expo React Native repository. Device benchmarks require an appropriate Android or iOS build environment; source inspection alone cannot establish a performance improvement.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Improve Expo React Native performance

Start with the user's slow flow, not a list of fashionable optimisations. Preserve behaviour, accessibility, error reporting, and data correctness while improving a measured bottleneck.

## Establish the experiment

Inspect the package manager and lockfile, Expo SDK, React Native and React versions, Hermes/runtime, New Architecture, router, updates configuration, and performance-sensitive dependencies. Expo's supported React Native version is the app's constraint; do not install the newest React Native independently to match an example.

Define a repeatable scenario and one primary metric: cold-start time, input latency, dropped frames, retained memory after a navigation loop, or end-to-end request latency. Add a few guardrail metrics. Agree numerical budgets from the product and target device, not invented universal thresholds.

Record commit, build configuration, device/OS, thermal state, cache state, dataset, network conditions, repetitions, and measurement method. Separate cold from warm runs. Interleave baseline and candidate runs when drift is plausible; report the distribution and sample count, not a best run or an unsupported p95.

## Diagnose, change, verify

1. Reproduce and capture a release-build baseline on representative hardware. Simulators and development builds are useful for diagnosis, not substitutes for shipping-device measurements.
2. Use React Native DevTools for React/JS attribution in a compatible diagnostic build; native system traces and Instruments reveal main-thread, rendering, I/O, and allocation costs. Keep these evidence types distinct. See `references/01-profiling-toolchain.md`.
3. Form a specific hypothesis supported by a trace or counter. Change one coherent cause, not several unrelated knobs.
4. Repeat the same scenario and correctness checks. Keep the change only when its benefit exceeds run-to-run variation without breaking a guardrail.
5. Add a regression check proportionate to the problem. Bundle size is not a proxy for input latency; do not claim a size gate prevents all performance regressions.

## Route to the bottleneck

| Evidence | Investigate | Reference |
|---|---|---|
| Long pre-interactive work or JS evaluation | Critical startup path, eager imports, asset loading, update payloads | `references/02-startup-bundle-ota.md` |
| Long JS tasks or repeated expensive commits | State ownership, derivations, bounded scheduling, compiler coverage | `references/03-rendering-js-ui.md` |
| UI stalls while JS is quiet | Layout, compositing, image decoding, native animations | `references/03-rendering-js-ui.md` |
| Scroll/recycling or media pressure | Row identity, list API, image size/cache, video lifecycle | `references/04-lists-images-media.md` |
| Retained JS heap or growing native footprint | Repeated navigation, listeners, closures, media release | `references/01-profiling-toolchain.md` |
| Refetch storms or blocking requests | Deduplication, cache semantics, pagination, cancellation | `references/05-network-background.md` |

Current API rules: use bounded `requestIdleCallback` work rather than removed InteractionManager APIs. Scheduling does not move CPU work off the JS thread. FlashList v2 requires the New Architecture and automatic sizing; do not add size-estimate props. Inspect whether React Compiler already runs before installing or duplicating its configuration.

Resolve `SKILL_DIR` to this skill's installation directory before running bundled scripts or loading templates. Pass the target project separately; its `scripts/` directory is not the skill's directory.

## Deliver

Use `assets/templates/perf-audit-report-template.md` when a report is useful. Include the observed symptom, baseline, causal evidence, exact changes, comparable before/after results, correctness checks, trade-offs, and remaining unknowns. For source-only work, deliver hypotheses and a runnable measurement plan, not fabricated timings or a claim that the app is now faster.

Use `references/00-principles-and-kpis.md` for metric definitions and `references/06-ci-regression.md` for regression-control ideas. Treat package installation and build flags in older project configurations as things to verify against the installed SDK, not universal defaults.
