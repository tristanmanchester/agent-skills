# Template index

These templates are starting points, not one-size-fits-all answers. Check the
selected template's actual imports and lifecycle against the application's
installed stack; the whole collection has not been certified on a native build.

## Visual surfaces

- `ambient-gradient-card.tsx` — ambient card with blurred orbs
- `shimmer-cta-button.tsx` — clipped shimmer button with paragraph label
- `shader-noise-background.tsx` — procedural shader background
- `morphing-blob.tsx` — path interpolation for organic motion
- `tilt-spotlight-card.tsx` — gesture-led spotlight / card depth
- `video-frame-surface.tsx` — video-backed hero / media surface
- `skottie-loader.tsx` — Lottie/Skottie playback with runtime tinting

## Data / status / text

- `progress-ring.tsx` — animated ring / HUD pattern
- `custom-font-paragraph-badge.tsx` — wrapped rich text with explicit font loading

## Interaction / high-instance patterns

- `pan-zoom-image-stage.tsx` **and** `pan-zoom-math.ts` — RNGH 3 pan/pinch,
  bounded viewport-centred geometry, and native zoom/move/reset controls. Copy
  both files. Read the [integration and test notes](../../references/pan-zoom-template.md).
- `sprite-atlas-field.tsx` — repeated textured sprites via `Atlas`
- `snapshot-composite.tsx` — capture React Native content into Skia

## Adaptation advice

Preserve the architecture when it still suits the workload. Rename dimensions,
colours, and copy to match the product. Remove secondary motion before rewriting
a component solely to make it lighter; strengthen hierarchy before adding more
moving parts. Check loading/error paths, cancellation, cleanup, and accessibility
in the selected template rather than assuming the entry-point guidance has
already been implemented in every example.
