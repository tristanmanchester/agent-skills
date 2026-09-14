# Current contracts and source map

Reviewed 2026-09-13. These are selected API checks, not a native runtime certification
or a claim that every bundled template was built. Inspect installed types and
version-matched documentation before applying a recipe.

## Native installation

The reviewed stable line needs RN 0.79+, React 19+, iOS 14+, and Android API21+;
video needs Android26+. Skia2.10+ native animation uses Reanimated4. The installation
page gives Worklets0.7+ as a floor, but Reanimated's exact minor/patch compatibility
still controls which Worklets release fits. Expo's supported combination can lag
upstream: do not independently upgrade every native dependency to latest.

Native binaries are package dependencies (react-native-skia-android and platform
Apple packages), resolved through Gradle/CocoaPods. The old postinstall/Bun
trustedDependencies/Yarn enableScripts advice does not apply to this delivery
model. Inspect missing platform packages and native build errors instead of
broadening script execution globally.

Graphite remains an experimental @next backend, not the stable default. Choosing
it changes platform/build requirements. Its internal Dawn implementation does
not make Skia a public WebGPU API; any WebGPU interop needs the documented matching
Dawn build and explicit project scope.

Source: https://shopify.github.io/react-native-skia/docs/getting-started/installation/

## Animated values

Pass shared/derived values directly to Skia props. Use Skia interpolateColors rather
than assuming Reanimated's colour representation is interchangeable. Current select
binds fields from one shared object; nested animation objects are not supported.
Animate individual values and derive an object, or update plain values in a bounded
frame callback. Stop that callback when it is not needed.

Source: https://shopify.github.io/react-native-skia/docs/animations/animations/

## Canvas, context, and assets

Skia's drawing tree has a separate renderer: read application/theme context outside
and pass the needed values, or bridge deliberately. Do not require an extra context
library when simple props suffice.

Source: https://shopify.github.io/react-native-skia/docs/canvas/contexts/

Wait for images/fonts/video and layout readiness before snapshots. Texture-backed
snapshots need the async rendering-context path; a successful allocation alone is
not evidence of correct pixels. Capturing a native subtree with makeImageFromView
requires attention to the non-collapsed capture root.

androidWarmup is only for static opaque drawings. highBitDepth is greater precision,
not HDR; support depends on platform/backend. Check the actual rendered output and
fall back deliberately when unavailable. Accessible native overlay views remain
necessary for individually interactive drawing objects.

Source: https://shopify.github.io/react-native-skia/docs/canvas/overview/
Source: https://shopify.github.io/react-native-skia/docs/snapshotviews/

## Web and resource costs

Load the version-matched CanvasKit bundle before Skia-dependent imports/rendering.
Use the installed release's web setup; do not mix a latest CDN WASM with older JS.
Handle loading and failure states and repeated mount/unmount. Private-looking
optimisation props need current documentation and a workload-specific reason,
not cargo-cult use. Bundle-size figures are library estimates, not measurements
of the app's download, startup, GPU memory, or rendering cost.

Sources:
- https://shopify.github.io/react-native-skia/docs/getting-started/web/
- https://shopify.github.io/react-native-skia/docs/getting-started/bundle-size/

## Maintainer regression scenarios

Check a Bun/Yarn project without lifecycle-script permission; Skia2.10 with an
incompatible Reanimated/Worklets pair; nested timing values in grouped state;
texture snapshots before image readiness; a context-consuming drawing component;
an off-screen infinite effect; an interactive canvas with no accessible controls;
and a request for ordinary native polish that should not force Skia.

Inspect the actual result, not whether a particular helper was invoked. Existing
evaluation fixtures are prompts, not measurements of current model behaviour.
