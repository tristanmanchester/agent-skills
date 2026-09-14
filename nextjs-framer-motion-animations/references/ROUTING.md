# Router integration

## App Router

Layouts persist; templates remount at their own segment boundary, including changed
dynamic parameters. A deeper navigation need not remount a higher template, and
search-parameter changes do not automatically remount it. Use a template only when
its state-reset/effect-restart behaviour is desired, not as a free animation wrapper.

For enter-only motion, render a small animated leaf from the relevant template.
For local toggles, keep AnimatePresence around a child whose visibility and key
the application actually controls. Neither proves complete route exit choreography.

A generic `AnimatePresence` around `<motion.main key={pathname}>{children}</motion.main>`
in a persistent layout lacks a demonstrated contract for retaining an unchanged
outgoing router subtree. Verify that contract before making exit guarantees. Do
not solve it through private router-context snapshots, frozen stale data, nested
main landmarks, or indiscriminate navigation interception.

Source: https://nextjs.org/docs/app/api-reference/file-conventions/template
Source: https://motion.dev/docs/react-animate-presence

## Current framework view transitions

The current Next.js guide (updated 2026-08-25) documents React ViewTransition in
the App Router without configuration, using the React build supplied by Next.
Check the app's actual version; do not copy an old experimental flag or separately
install React canary merely because an old article required it.

Choose unique shared-element names on the participating pages. A shared-element
pair needs appropriate old/new content in the same commit: a suspended destination
can instead follow its loading/enter path. Default animations and explicit share
settings must match; test unrelated updates to avoid accidental crossfades.
Navigation direction tags are intentional application metadata, not automatic
proof of browser back/forward intent. Preserve interaction and reduced-motion
fallbacks, and check browser support.

Motion AnimateView is separately labelled alpha in the reviewed docs. Its existence
does not require adopting it when Next's documented view-transition surface or a
simple local animation suffices. Keep experimental adoption explicit.

Sources:
- https://nextjs.org/docs/app/guides/view-transitions
- https://motion.dev/docs/react-animate-view

## Pages Router

Pages Router has a different ownership model. A persistent presence boundary in
_app can observe keyed page replacement; check what the page actually renders
and whether the exiting component remains stable. Keys should reflect the intended
route identity, not an array index. Avoid hydration differences from asPath before
the router is ready, and decide whether query-only changes should replay motion.
Do not move a one-off animation into _app merely for convenience.

## Server and client rendering

Use motion/react-client for a supported declarative motion element from a server
file, and a Client Component for hooks/presence/scroll/interactive logic. Do not
pass ordinary server closures as event handlers. Keep server children, their data,
and route/loading/error boundaries intact. Do not add a root client boundary just
to satisfy one import.

## Browser acceptance matrix

Verify: direct load; hydrated navigation; dynamic segment change; query change;
back/forward; rapid double navigation; cancelled or superseded navigation; suspended
and failed data; focus/scroll restoration; reduced motion; unsupported browser;
and no unexpected duplicated landmarks/content. Record expected versus observed
behaviour rather than treating a persistent wrapper as proof.
