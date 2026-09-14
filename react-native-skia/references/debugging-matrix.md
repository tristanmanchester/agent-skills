# Debugging matrix

Use this file when the repo already contains Skia code and something feels wrong.

## Install / build

### Symptom
Native build fails after installing Skia.

### Likely causes
- Required platform packages are absent or incompatible with the selected target.
- Lockfile, dependency resolution, or native build output belongs to a different stack.
- React / React Native / Skia versions do not match their compatibility requirements.

### Fixes
- Inspect the resolved versions, installed platform dependencies, target architecture,
  and first relevant native build error, not only declared package ranges.
- Current Skia binaries arrive through package dependencies. Do not add Bun trust
  entries or enable Yarn lifecycle scripts as a stock postinstall fix.
- Match React Native / React / Skia / Reanimated / Worklets using the installed
  Expo SDK and [current contracts](official-doc-notes.md).
- Repair the identified dependency or native build issue, then rebuild as authorised;
  do not reinstall or broaden script permissions without a concrete cause.

## Web blank screen

### Likely causes
- CanvasKit not loaded before Skia code runs.
- `setup-skia-web` not rerun after an upgrade.
- Skia components inside Expo Router are evaluated too early.

### Fixes
- Use `WithSkiaWeb` or `LoadSkiaWeb()`.
- For Expo web, rerun `setup-skia-web`.
- If needed, defer root registration or code-split the Skia route/component.

## Gestures do not work

### Likely causes
- `react-native-gesture-handler` missing or misconfigured.
- `GestureHandlerRootView` missing near the app root.
- Gesture transforms and canvas transforms are out of sync.

### Fixes
- Verify dependency installation.
- Ensure the app root is wrapped in `GestureHandlerRootView`.
- Keep transforms in shared values and apply the same model everywhere.

## Animation stutters

### Likely causes
- React state updates every frame.
- shared values read on the JS thread
- wrong render mode for the workload
- too many repeated shapes instead of `Atlas` or textures

### Fixes
- Move state to shared / derived values.
- Stop reading `.value` on the JS thread in normal render logic.
- Switch to `Atlas` or `Picture` when appropriate.
- Collapse repeated transforms into parent groups where possible.

## Visuals are blurry or soft

### Likely causes
- `RuntimeShader` image filter ignores pixel density.
- text or image is being blurred unintentionally
- low-resolution source image is scaled too far

### Fixes
- Supersample `RuntimeShader` image filters using layer scaling.
- Keep text crisp and in a foreground layer.
- Use better source assets or texture strategy.

## Text will not wrap or style correctly

### Likely causes
- wrong API for text layout
- fonts still loading
- paragraph layout never computed

### Fixes
- Prefer `Paragraph`.
- Guard until the font manager exists.
- Call `layout(width)` before measuring or drawing.

## Paragraph / Picture / Skottie effects do not apply

### Likely cause
Those components do not follow the same painting rules as normal shapes.

### Fix
Apply effects through a parent `Group` using `layer`.

## Snapshot crashes or returns the wrong view

### Likely cause
The root of the captured React Native subtree was optimised away.

### Fix
Set `collapsable={false}` on the captured root view.

## Theme or context values disappear inside Canvas

### Likely cause
Skia uses a separate React renderer.

### Fix
Prepare the values before entering the canvas tree, or explicitly re-inject context using a bridge.

## Rotation or transform math looks wrong

### Likely causes
- degrees were used instead of radians
- origin assumed to be centre instead of top-left

### Fixes
- convert to radians
- set `origin` explicitly when centring transforms
- prefer a single parent transform when possible

## Reduced motion is ignored

### Likely cause
Decorative loops were hard-coded with no fallback path.

### Fix
Use `useReducedMotion()` and provide a lighter or static path.
