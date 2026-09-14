---
name: nextjs-framer-motion-animations
description: >-
  Implement and debug Motion for React in Next.js: local interaction, presence,
  layout, shared elements, scroll, reduced motion, and router integration. Use for
  explicit Motion/Framer Motion work or interactions that need it; prefer CSS for
  simple effects and framework-native view transitions for supported route cases.
license: MIT. See LICENSE.txt
compatibility: Use the current motion package and the app's supported React/Next.js/runtime versions. Inspect locked versions and router type. No legacy import-rewriting wrapper or automatic project scaffolding is provided.
metadata:
  version: "5.0.0"
  reviewed: "2026-09-13"
---

# Purposeful Motion in Next.js

Choose motion to explain state or improve interaction, not to add a mandatory
layer to every page. Keep existing design tokens and semantic controls. For a
small colour/focus/hover transition, CSS may avoid unnecessary client JavaScript.

## Inspect before choosing the boundary

Read the actual component, router (App or Pages), package/lockfiles, installed
Motion API, and build configuration. Identify who owns mounting, state, focus,
scroll, and navigation. Distinguish a local reveal from a route transition.
A filename/token scanner cannot prove these relationships or build compatibility.

For modernised/new Motion code, use `motion/react`. In a Server Component, the
supported `motion/react-client` entry point exposes motion elements; it does not
turn hooks or arbitrary callbacks into server-safe code. Put interactive/hooks
in the smallest Client Component, keeping fetching and secrets server-side.
Server-rendered children can pass through a client wrapper without moving their
implementation into the client bundle. Props across that boundary must meet
React's actual serialisation contract.

For an existing framer-motion project, inspect its installed version and decide
whether migration is in scope. A deliberate migration updates package, imports,
lockfile, tests, and any changed APIs together. Do not mix runtimes or mechanically
rewrite namespace imports from motion/react-m into a different module. This skill
ships no compatibility branch or automatic import rewriting.

## Choose the mechanism

| Need | Start with | Essential condition |
| --- | --- | --- |
| Small local tween/gesture | motion element | Preserve semantic element and disabled/focus behaviour |
| Several coordinated children | variants and stagger | Stable identity and a bounded delay budget |
| Local removal | AnimatePresence | It survives and observes the removed keyed child |
| Layout change | layout / layout="position" | Correct measurement and retained identity |
| Shared element within a live tree | layoutId / LayoutGroup | Unique, intentionally scoped IDs |
| Visibility reveal | whileInView | Correct scroll root and progressive visibility |
| Scroll-linked value | useScroll plus motion values | Correct target/container and reduced-motion policy |
| Imperative sequence | useAnimate | Scoped targets and cancellation/cleanup |
| Bundle-sensitive region | LazyMotion with m | Feature set covers the used layout/drag APIs |
| Route/shared-view transition | Framework-supported ViewTransition | Actual Next/React/browser contract, not a pathname wrapper |

Read [component patterns](references/COMPONENTS.md) for implementation decisions
and [router integration](references/ROUTING.md) for route changes. Do not assume
one package-wide provider or one animation duration fits every interaction.

## Presence and application state

A persistent AnimatePresence is necessary for its own exits but is not sufficient
to control a router-owned subtree. Keying a wrapper by pathname does not establish
that outgoing route content is retained unchanged. Do not freeze private router
context, intercept every click, or delay all navigation to make an exit demo work.
Use the supported framework route mechanism or an honest enter-only enhancement.

An animation callback is not a transaction boundary. Do not make a payment,
delete, navigation confirmation, or other application outcome depend on whether
an animation happened to finish. Cancellation, interruption, remount, and reduced
motion must preserve the same logical outcome.

## Accessibility and rendering

Use MotionConfig reducedMotion="user" where it fits the existing tree, plus local
useReducedMotion decisions for scroll, autoplay, and bespoke effects. Opacity-only
animations and independent CSS/view-transition paths need their own policy; one
Motion provider is not a universal motion switch.

Use real buttons/links/dialogs. Preserve keyboard paths, visible focus, logical
reading order, and an equivalent to drag-only interaction. Exiting invisible
controls must not remain focusable or intercept input. A visual modal shell is
not focus management, Escape behaviour, a label, or background inertness.

Do not server-render critical text permanently invisible and depend on successful
hydration/intersection observation to reveal it. Keep layout boxes stable and
handle font/image loading, viewport changes, and no-JavaScript/failure behaviour
where required. Use transform/opacity where suitable, but measure actual paint,
layout, compositing, and bundle costs before claiming a speed improvement.

## Validate the actual change

Run the project's existing typecheck/lint/build as authorised; do not assume its
scripts are named npm run lint/build. Test in the browser with rapid interactions,
back/forward navigation, slow data, interruptions, reduced motion, keyboard use,
and multiple copies of shared-layout components. Check console/hydration errors,
scroll restoration, focus, and usable nonanimated fallback. Unit mocks are not a
browser performance or router-lifetime test.

Deliver the patch, chosen boundary/mechanism, actual verification, and remaining
browser checks. The old generic scanners, generated plans, all-assets scaffolder,
and their golden-output pack are removed; real integration evidence is the goal,
not reproducing a heuristic's preferred output.

## Sources and maintenance

Reviewed 2026-09-13: [Motion installation](https://motion.dev/docs/react-installation),
[AnimatePresence](https://motion.dev/docs/react-animate-presence),
[Next templates](https://nextjs.org/docs/app/api-reference/file-conventions/template),
and [Next view transitions](https://nextjs.org/docs/app/guides/view-transitions).
[Evaluation cases](evals/scenarios.json) describe required checks, not tests run.
