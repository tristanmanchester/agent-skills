# Interaction recipes

These patterns target Reanimated 4/RNGH 3. Adapt them to actual app types and test
them on the target build; they are not a generic production-ready component kit.

## Successful swipe requests an action

Inside a component with `x`, `startX`, and `committing` shared values, a finite
positive row width, an appropriate gesture root, and an RN-runtime
`onRequestDelete` callback:

```tsx
const pan = usePanGesture({
  onActivate: () => {
    cancelAnimation(x);
    startX.value = x.value;
  },
  onUpdate: (event) => {
    if (!committing.value) {
      x.value = Math.max(-width, Math.min(0, startX.value + event.translationX));
    }
  },
  onDeactivate: (event) => {
    if (committing.value) return;
    const threshold = Math.min(120, width * 0.4);
    if (!event.canceled && x.value < -threshold) {
      committing.value = true;
      scheduleOnRN(onRequestDelete);
    } else {
      x.value = withSpring(0, { reduceMotion: ReduceMotion.System });
    }
  },
});
```

Import cancelAnimation/withSpring/ReduceMotion from react-native-reanimated,
usePanGesture from react-native-gesture-handler, and scheduleOnRN from
react-native-worklets. `onRequestDelete` handles confirmation/undo/backend state
as required by the product; only remove the row according to that actual outcome.
On failure or cancelled confirmation, clear committing and restore its position
through the application's state/effect flow. Gate non-gesture actions too. Provide
an accessible Delete button/menu; swiping must not be the only route.

Use onFinalize for any begin-state cleanup, including a gesture that fails before
activation. Test cancellation beyond the threshold, repeated swipes while pending,
backend failure, resize, and unmount. Do not keep the old (_, success) callback.

## Persistent pinch and pan

Maintain committed scale/translation separately from each gesture's starting
values. At activation capture the current transform; update from that start and
the event's scale/translation, then clamp to meaningful content bounds. On a
successful end retain the result; on cancellation apply the product's defined
rollback policy. Compose with useSimultaneousGestures only when simultaneous
interaction is intended. Preserve focal-point behaviour and test successive
pinches, not only the first one. Add zoom/reset controls for accessibility.

## Double tap and state transitions

Use useTapGesture with numberOfTaps: 2 and a successful onDeactivate event.
Store a target zoom state rather than comparing an interpolated scale to 1.
Apply a reduced-motion-aware timing/spring to that target and provide a single-
action button equivalent. Do not mix builder and hook APIs in the same related
subtree.

For a simple state-driven CSS transition, name only the changing properties and
set a finite duration. Apply the app's reduced-motion setting to that CSS path as
well; disabling a spring elsewhere is not a global accessibility solution.

## Layout accordion

Use React state for open/closed, an accessible labelled toggle with expanded
state, and layout/entering/exiting presets for the visual change. Preserve focus
when content is removed. Ensure exit animation does not leave invisible controls
interactive. Skip nonessential animation under reduced motion and verify dynamic
content measurement on both platforms.

The templates illustrate application decisions; official lifecycle source:
https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3/
