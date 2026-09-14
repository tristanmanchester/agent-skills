# Pan/zoom image template

Copy both `assets/templates/pan-zoom-image-stage.tsx` and
`assets/templates/pan-zoom-math.ts` into the same directory in the application.
The template targets Skia 2.10+, Reanimated 4, and Gesture Handler 3 with a working
Worklets setup and the application's GestureHandlerRootView. It is a bounded,
non-rotating image viewer, not a general affine editor or a drop-in migration shim.

The image fits the viewport at scale 1 while preserving its aspect ratio. Scale
and translation share one pose; the Group receives one derived transform of
plain numbers. A moving pinch focal point owns two-finger translation, so pan
does not add that motion a second time. Each update uses the actual clamped scale
ratio. Overscroll is clamped, and an axis with content smaller than the viewport
stays centred. Clamping can intentionally move the focal image point at an edge.

A cancelled view gesture retains its last bounded pose. It does not initiate a
business mutation. A new source or new dimensions resets the pose by remounting
the view. Native buttons provide zoom, translation, and reset without requiring
gestures. Button changes are immediate, with no decorative motion to suppress.
Loading and image errors are visible. Add retry, progress feedback, localisation,
and application-specific image descriptions as required.

## Offline geometry checks

From the skill directory, with TypeScript already installed:

```sh
BUILD_DIR="$(mktemp -d)"
tsc --strict --target ES2022 --module commonjs --outDir "$BUILD_DIR" \
  assets/templates/pan-zoom-math.ts
SKIA_GEOMETRY_BUILD="$BUILD_DIR" node --test tests/pan-zoom.test.cjs
# BUILD_DIR contains disposable compiled test output; retain or remove it deliberately.
```

These tests exercise fitting, repeated zooms, focal-point invariance, clamped
ratios, translation, invalid values, and a deterministic sequence of 500 updates.
They do not execute Reanimated worklet transformation, gesture arbitration,
React Native accessibility, or Skia drawing. A TypeScript syntax transpilation
likewise does not type-check the component against installed native packages.

## Required app checks

Type-check in the actual app, build both native targets, and exercise successive
pinches, one-to-two-to-one pointer changes, cancellations, competing parent scroll,
edge clamping, source changes, resize, loading failure, and each native control.
Verify image geometry and pixel density on real renders, along with screen-reader
focus and labelling. Adapt gesture relations when embedding in another scroll or
zoom surface; the pure geometry tests cannot prove that arbitration is correct.

## Sources checked September 14, 2026

- https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pan-gesture/
- https://docs.swmansion.com/react-native-gesture-handler/docs/gestures/use-pinch-gesture/
- https://docs.swmansion.com/react-native-gesture-handler/docs/composition/use-simultaneous-gestures/
- https://shopify.github.io/react-native-skia/docs/animations/animations/
- https://shopify.github.io/react-native-skia/docs/group/
- https://shopify.github.io/react-native-skia/docs/images/
- https://docs.swmansion.com/react-native-worklets/docs/threading/scheduleOnUI/
