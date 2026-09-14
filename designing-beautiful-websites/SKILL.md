---
name: designing-beautiful-websites
description: >-
  Design, implement, or critique website and web-app UX/UI: information structure,
  user flows, responsive layouts, visual systems, content, and interaction states.
  Use for a requested interface or visual-design change; do not expand a small
  component edit into an unrequested product redesign.
compatibility: Design reasoning works from supplied content and screenshots. Implementation and browser checks depend on the project's tools. The optional opaque-sRGB contrast helper requires Python 3.9+.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# Clear, distinctive web interfaces

Make the purpose and next action legible, with a visual language that fits the
product and audience. Build from real content and behaviour, then use typography,
spacing, colour, imagery, and motion deliberately. Beauty is not one universal
palette, a grid of rounded cards, or an obligation to remove all decoration.

## Establish the actual design task

Read the request, existing implementation, design system, assets, and relevant
content. Identify the user, page purpose, important journey, brand signals, target
platforms, and constraints. Use supplied answers; infer ordinary defaults and
state consequential assumptions without repeating a questionnaire.

For a local polish request, stay local unless a structural problem prevents the
requested result. For a new site, choose a coherent direction and implement the
requested deliverable rather than only returning a planning packet. For an audit,
show the material issues, their locations and impact, and specific fixes. Do not
claim to have interacted with a page when only a screenshot was available.

## Structure before ornament

Trace the user's key task from entry through completion and recovery. Make labels,
content order, navigation, and feedback understandable without internal terminology.
Retain the context needed to make a decision; fewer words or clicks are not always
better. Distinguish required steps from accidental friction, including permissions,
confirmation, cancellation, and access to help.

Start layout from the content and priorities rather than a generic app shell.
Use meaningful grouping, alignment, and whitespace. Define how real long text,
translations, missing images, tables, errors, loading, empty results, and success
states fit. Design information order and controls for narrow screens, zoom, and
keyboard use, not merely a scaled-down desktop screenshot.

## Give the interface a visual point of view

Use the project's established visual system first. For a new direction, choose a
small set of intentional characteristics: for example, editorial typography and
asymmetric composition for a publication, precise compact controls for a technical
tool, or generous photography and warm materials for a hospitality site. These
are possible directions, not templates to apply regardless of the brief.

Create hierarchy through type size, weight, line length, spacing, contrast, and
position before adding more decoration. Use a consistent spacing/type scale as a
starting discipline, then allow a justified optical or content-specific adjustment.
Use borders, shadows, backgrounds, and illustration according to the composition;
a blanket preference for shadows over borders is not a quality rule.

Make dominant content and actions visible, with quieter supporting information.
Use intentional imagery and crop/focal choices rather than arbitrary stock assets.
Only use assets with suitable rights; do not invent client logos, reviews, awards,
statistics, or product capabilities to fill a layout. Mark synthetic content as a
placeholder. Avoid fake scarcity, hidden refusal, or misleading price presentation.

Use restrained, purposeful motion where it helps orientation or feedback, with
reduced-motion and usable static states. Do not add a heavy library, animation
system, or client boundary for an effect already served by simple CSS.

## Implement complete states and semantics

Keep buttons as actions and links as navigation. Use the existing component system
and framework conventions; preserve refs, focus, form submission, validation, and
loading/error semantics when restyling. A disabled-looking control must have the
correct interaction behaviour. Define what happens after network failure, duplicate
activation, cancellation, or stale data; visual feedback is not proof a write succeeded.

For forms, preserve entered data and make errors specific and recoverable. For
menus/dialogs/tabs, use the appropriate semantic pattern and keyboard/focus behaviour,
not just a styled container with role attributes. Do not hide important content
until a fragile JavaScript reveal succeeds. Keep layout stable as fonts/media load.

Read [accessibility](references/ACCESSIBILITY.md) for targeted checks. A contrast
ratio or automated scan is one piece of evidence, not an accessibility certificate.

## Inspect, test, and iterate

A quick first-impression or heuristic walkthrough is useful expert inspection;
it is not a measured user test and cannot establish conversion or task-success
rates. Where testing is requested, use actual participants or observed interaction
and record scope, conditions, and results. Do not invent a successful glance test.

For implementation, run the relevant project typecheck/build/tests as authorised,
then inspect rendered output at meaningful widths, zoom/text sizes, interaction
states, and input methods. Check focus, accessible names, scrolling, clipping,
content wrapping, and browser/console failures. Record what was actually tested.
A static screenshot cannot establish keyboard or screen-reader behaviour; a test
plan is not a completed test. Avoid unsupported performance or conversion claims.

For handoff, give the actual patch or requested design artefact, changed tokens
and component/state rules where useful, and unresolved verification. A small edit
does not need a new sitemap, complete design system, or seven-section report.
Stop when the work serves the task; don't keep redesigning coherent choices for novelty.

## Load only the relevant reference

- [Visual design](references/VISUAL-DESIGN.md): typography, hierarchy, composition.
- [Information architecture](references/INFORMATION-ARCHITECTURE.md): navigation and structure.
- [Interaction](references/INTERACTION-DESIGN.md): states, controls, and forms.
- [Content](references/CONTENT-COPY.md): useful labels and microcopy.
- [Responsive design](references/RESPONSIVE.md): content-led layouts and edge cases.
- [Accessibility](references/ACCESSIBILITY.md): semantic and input checks.
- [Design audit](references/DESIGN-AUDIT.md): finding/impact/fix format.
- [Page patterns](references/PAGE-PATTERNS.md), [usability](references/USABILITY.md),
  [workflow](references/WORKFLOW.md), and [checklists](references/CHECKLISTS.md):
  optional deeper methods, not a mandatory output format.

Reference/script paths belong to the installed skill directory, not the target
project. Older numeric design ranges are heuristics to adapt, not universal standards.
No usability, accessibility, conversion, or performance improvement is claimed
without evidence from the actual interface.

Authoring baseline reviewed 2026-09-13: https://agentskills.io/specification.
Current accessibility sources are listed in the accessibility reference.
