---
name: react-native-skia
description: >-
  Build, debug, or profile React Native Skia canvases, paths, rich text, shaders,
  images, snapshots, video, and animated graphics. Use when Skia is selected or
  custom drawing is needed. Do not introduce a canvas merely because ordinary
  native UI should look polished or animate smoothly.
compatibility: Current native Skia requires React Native 0.79+ and React 19+. Skia 2.10+ animation integration requires Reanimated 4; resolve the exact Worklets/native combination through the app's Expo SDK and upstream compatibility tables.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# React Native Skia

Use Skia when the task needs custom drawing. Keep accessible native controls and
ordinary layout as native views. For an existing app, inspect the actual locked
Skia/React Native/React/Reanimated/Worklets versions, target platforms, rendering
backend, and relevant component before changing dependencies or architecture.

## Choose by workload

Use retained drawing for stable scenes with animated props, Picture when recording
a changing command list is justified, and Atlas for repeated sprites sharing a
texture. Reuse textures for repeated expensive motifs only when profiling or the
workload supports that tradeoff. A shader is not automatically faster than shapes;
blur, overdraw, texture uploads, resolution, and live resource count matter.

Define the intended visual hierarchy, interaction, assets, bounds, and reduced-
motion state. For broad creative requests, choose a coherent direction and proceed;
do not require a design workshop for a small effect. Preserve useful design and
primitive-selection methods in the references below.

## Current integration rules

Read [current contracts](references/official-doc-notes.md) for version-sensitive
setup. Native binaries now arrive through package dependencies, not a Skia
postinstall downloader. Do not enable arbitrary lifecycle scripts or add Bun trust
entries as a stock fix. Confirm the build actually resolves the platform packages.

Pass shared/derived values directly to drawing props. Do not wrap Skia drawing
nodes in createAnimatedComponent/useAnimatedProps merely for animation; native
overlay views are a different case. Use Skia's interpolateColors for Skia colours.
Keep React state and context decisions outside the separate drawing renderer,
or deliberately bridge required context. Worklets still consume frame time.

For grouped state, the current select API can bind object fields. Do not nest
withTiming/withSpring objects inside that state and assume Reanimated animates
each field; use individually animated values or calculated plain values instead.

Guard asynchronous images/fonts/video and shader-compilation failures. Prefer
Paragraph for wrapped or multi-style text. Check drawing origins, radians, clipping,
and paint/layer semantics before treating a visual defect as a performance issue.
For texture-containing snapshots, use the documented async path in the correct
rendering context and wait for real asset readiness, not a fixed arbitrary delay.

## Lifecycle and accessibility

Cancel or deactivate decorative loops/frame callbacks on unmount and when they
are unnecessary off-screen/backgrounded. Provide a meaningful static reduced-motion
state. Reanimated's useReducedMotion reads the startup preference; use an actual
reactive setting subscription if the app must respond while running.

Mirror relevant hit regions and transforms with accessible native controls, with
labels, focus, keyboard/screen-reader actions, and adequate hit targets. A Canvas
accessibility label does not expose its individual interactive shapes. Verify
successive gestures, cancellation, bounds changes, and multi-touch, not only a
single ideal drag. Use one compatible Gesture Handler generation for related
interactions; adapt a template's gesture API to the chosen stack.

## Inspect and verify

The former regex audit is removed: it inferred installed versions from dependency
ranges and prescribed obsolete postinstall fixes. Instead inspect lockfiles,
dependency resolution, native build logs, actual component state, and targeted
source searches. A token in a comment or neighbouring component is only a lead.

Type-check the adapted component in the actual project. Verify assets, loading/error
states, density, orientation, fonts, touch/accessibility, and web CanvasKit loading
where applicable. Profile a release-like build on representative devices, including
GPU cost and memory. Mocks and CanvasKit tests are not native rendering proof;
UI-thread execution, a warmup flag, or an Atlas node is not a frame-rate guarantee.

Report the patch, intended effect, why the chosen primitives fit, observed results,
and remaining device/browser checks. Do not label unmeasured work GPU-friendly or
near-zero-cost. Treat Graphite/@next as an explicitly chosen experiment, not the
normal upgrade path.

## Load references for the task

- [Current contracts](references/official-doc-notes.md): setup, assets, versions.
- [Decision tree](references/decision-tree.md): rendering primitives.
- [Motion design](references/motion-design-playbook.md): composition and visual intent.
- [Performance](references/performance-playbook.md): measured bottlenecks.
- [Debugging](references/debugging-matrix.md): symptom-driven investigation.
- [Recipes](references/animated-element-recipes.md): implementation approaches.
- [Template index](assets/templates/template-index.md): starting examples to adapt.
- [Evaluation](references/eval-strategy.md): maintainer output/trigger checks.

References and templates are skill-relative, not files in the target app. Templates
are starting points, not certified against every current native stack. Preserve
their useful design while checking actual imports, lifecycle, and semantics.
