# Component patterns and review

Use these as decisions to implement with installed types, not a complete component
library. Keep application semantics and accessibility in the app's existing UI system.

## Local presence

A minimal visual presence pattern is:

```tsx
'use client';
import type { ReactNode } from 'react';
import { AnimatePresence, motion, useReducedMotion } from 'motion/react';

export function PresencePanel({ open, children }: { open: boolean; children: ReactNode }) {
  const reduce = useReducedMotion();
  return (
    <AnimatePresence initial={false}>
      {open && (
        <motion.div key="panel"
          initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          transition={{ duration: reduce ? 0 : 0.16 }}>
          {children}
        </motion.div>
      )}
    </AnimatePresence>
  );
}
```

This is visual-only. Interactive exiting content needs focus/inertness handling
through a presence-aware child or the UI library. A dialog also needs semantics,
labelling, dismissal, focus restoration, and background control. Do not present
the example as a complete modal, accordion, or production accessibility solution.

AnimatePresence needs stable unique direct-child keys and must outlive their
removal. `wait` supports one child at a time. Nested boundaries need deliberate
propagation. `popLayout` needs the documented ref/positioning contract for custom
children. Do not add an exit prop to a conditional element with no surviving
presence boundary and expect it to run.

## Layout and shared identity

Use layout for actual React-driven geometry changes; use layout="position" where
size interpolation would distort content. LayoutGroup scopes/co-ordinates related
layout work, and unique group IDs prevent separate tab rows sharing one underline.
A visual tab row still needs actual tab/list/panel semantics and keyboard behaviour.
For accordions, preserve expanded/controls state, content labelling, and focus when
collapsing. Dynamic content needs measured layout rather than guessed heights.

For Reorder, stable values must identify items uniquely. Duplicate visible labels
are not adequate IDs. Provide non-drag reorder controls and persist order through
the application's actual state/transaction logic.

## Scroll and sequences

Use whileInView for a modest reveal and the correct root for nested scrollers.
For progress/parallax, use motion values without React state updates per scroll
frame. Reduced motion should remove nonessential travel; essential progress must
remain readable. Confirm offscreen/hidden content is not trapping focus.

Use scoped useAnimate when imperative sequencing is justified. Cancel superseded
work and cleanup timers/listeners. Bound stagger delay for long/virtualised lists;
a hundred items should not wait through a decorative queue. Avoid selectors that
capture unrelated descendant controls.

## Bundle and wrappers

For LazyMotion use the matching lightweight m entry point. domAnimation covers
standard animation/presence/gestures; layout/drag needs the documented richer
feature set. Do not accidentally bundle full motion components inside a supposedly
minimal boundary. Measure the production bundle rather than quote a package-size
claim as the app's saving.

Use motion.create outside render and forward the correct DOM ref. Derive wrapper
props from Motion's actual element prop types when accepting arbitrary handlers;
React DOM drag/animation event types can collide with Motion gesture callbacks.
Preserve disabled state, button type, focus styling, refs, and layout instead of
adding arbitrary wrapper divs.

## Motion policy

Use the design system's durations, distances, and easing; fixed ranges are starting
heuristics, not universal correctness. Test interrupted animations, hover on touch,
keyboard activation, reduced-motion changes, and repeated interaction. Prefer
unchanged usable content to a broken effect. Do not put business logic exclusively
in onAnimationComplete.

Sources reviewed 2026-09-13:
- https://motion.dev/docs/react
- https://motion.dev/docs/react-animate-presence
- https://motion.dev/docs/react-accessibility
- https://motion.dev/docs/react-reduce-bundle-size
