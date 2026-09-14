# Gesture Handler 3 contracts

Use hooks such as usePanGesture/useTapGesture and the v3 composition hooks for new
v3 code. Verify installed types; these names are not a v2 compatibility layer.

## Lifecycle and outcomes

The v3 renames include onStart -> onActivate and onEnd -> onDeactivate. The old
second `success` parameter is replaced by `event.canceled`, with inverted meaning.
Use `!event.canceled` before an application action. onFinalize cleanup must also
cover failure before activation; do not assume every begin leads to deactivate.

The old onChange callback moves to change* values on onUpdate. Do not add both
absolute translation and a delta in one frame. Preserve a start offset for each
new drag/pinch; otherwise each gesture jumps back to its local origin. Capture
an active gesture's bounds deliberately when the viewport changes.

For a destructive/remote action, separate the gesture decision, visual transition,
application request, and actual outcome. Gate repeated attempts while pending and
provide recoverable UI on failure. Animation completion is not commit evidence.

## Composition and hierarchy

Same-component relations use useCompetingGestures, useSimultaneousGestures, or
useExclusiveGestures. Cross-component relations use the documented requireToFail,
block, and simultaneousWith properties. Relations cannot cross between new hook
and old API generations; migrate a related group together. Do not reuse one gesture
instance across multiple detectors.

RNGH 3 GestureDetector changes view hierarchy. For hierarchy-dependent rendering
such as nested SVG interaction, use the documented InterceptingGestureDetector
and VirtualGestureDetector arrangement rather than inserting arbitrary native
views into the drawing tree. VirtualGestureDetector belongs below the intercepting
parent. Inspect current types/examples for the actual drawing library.

Keep the real GestureHandlerRootView boundary, modal handling, enabled state,
scroll competition, hit slop, and accessibility equivalent actions explicit.
Worklet callbacks can update shared values; cross to React Native only for a
necessary application action defined in that runtime.

Source reviewed 2026-09-13:
https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3/
