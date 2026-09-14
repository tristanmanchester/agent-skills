---
name: animating-react-native-expo
description: >-
  Implement and debug React Native or Expo motion with Reanimated 4 and Gesture
  Handler 3: state transitions, layout, gestures, scroll, worklets, cancellation,
  and accessible alternatives. Use for native UI motion, not web Motion or a
  reason to add canvas graphics to ordinary views.
compatibility: Requires a compatible React Native New Architecture, Reanimated 4, Worklets, and Gesture Handler 3 stack. Resolve versions through the app's Expo SDK or upstream compatibility tables; native verification needs a device or simulator build.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# React Native motion

Choose by the driver: state changes use CSS transitions, mount/reflow uses layout
animations, and gestures/scroll/physics use shared values and worklets. Keep
business state in React/application state and per-frame values out of React renders.
Do not impose animation on an interaction that works better without it.

## Inspect the actual stack

Read package and lockfiles, native architecture/configuration, and relevant
components before installing anything. Use the package manager's dependency-tree
command and the current [compatibility guide](https://docs.swmansion.com/react-native-reanimated/docs/guides/compatibility/).
A declared package is not proof that its native binary or Babel plugin matches.

This skill targets Reanimated 4 and RNGH 3. If the app is not on that stack, choose
a deliberate supported upgrade or stay within its installed API; do not mix API
generations or add compatibility wrappers. For Expo, use its SDK-specific install
resolution rather than independently upgrading every native package to latest.
See [setup](references/setup-and-compat.md). The old string-matching setup checker
is removed; use actual dependency/build evidence instead of an 'OK' printout.

## Implement one complete interaction

Define initial, active, completed, cancelled, interrupted, disabled, and reduced-
motion states. Include layout bounds, orientation/size changes, multiple touches,
and navigation/unmount. Choose a clear target state rather than toggling by whether
an in-flight animation value happens to be nonzero.

Gesture Handler 3's `onDeactivate` receives an event with **`canceled`**, not the
old second success argument. Perform committed actions only after a successful
gesture, and handle cleanup even if activation never happened. A completed animation
is not proof of a successful backend mutation. Prevent duplicate submissions while
an action is pending and reflect actual failure/recovery in application state.

Keep worklet closures small. Use `scheduleOnRN` only for a function defined in the
React Native runtime, such as navigation or an application callback. Do not pass a
function created inside a worklet and assume it belongs to JS. A UI worklet still
uses the UI thread: expensive computation can block rendering.

Use [gesture contracts](references/gestures.md) for composition and current v3
semantics, and [recipes](references/recipes.md) for deliberate starting patterns.
Paths under scripts/references/assets belong to the installed skill directory,
not the app's own similarly named directories.

## Accessible motion and lifecycle

Respect the system reduced-motion policy in timing, spring, layout, and CSS paths.
Reanimated's `useReducedMotion()` reports the startup setting; it is not a live
subscription. Where changes must apply while running, use the app's reactive
AccessibilityInfo subscription and remove the listener on cleanup. Provide a
non-gesture action for drag/swipe operations and preserve labels, focus, disabled
state, and hit targets. A visually translated view still needs correct interaction
and accessibility geometry.

Stop decorative loops/frame callbacks when unmounted, off-screen, backgrounded,
or reduced motion disables them. Reset to a meaningful static state. Do not make
accessibility depend on a particular frame rate or the completion of an exit effect.

## Verify

Type-check the actual component against the locked stack. Exercise success,
cancellation, interruption, repeat activation, pending/error outcomes, reduced
motion, screen-reader alternatives, and supported platforms. Profile a release-
like build on representative hardware; UI-thread execution is not a 60/120 fps
guarantee. Use Hermes-compatible debugging, not JSC Remote JS Debugging.

Report the patch, chosen driver/API, tests actually run, and remaining device
checks. Do not use dependency strings or mocked animations as native-runtime proof.

## Targeted references

- [Setup](references/setup-and-compat.md): dependency or native build mismatch.
- [Gestures](references/gestures.md): v3 lifecycle, composition, or hierarchy.
- [Worklets](references/worklets-and-threading.md): cross-runtime callbacks.
- [CSS](references/css-transitions-and-animations.md): style transitions/loops.
- [Layout](references/layout-animations.md): entering/exiting/reflow.
- [Recipes](references/recipes.md): adapting an interaction.
- [Performance](references/debugging-and-performance.md): measured frame problems.

Sources reviewed 2026-09-13: upstream Reanimated compatibility and
[reduced motion](https://docs.swmansion.com/react-native-reanimated/docs/device/useReducedMotion/),
[RNGH 3 migration](https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3/),
and [Expo integration](https://docs.expo.dev/versions/latest/sdk/reanimated/).
