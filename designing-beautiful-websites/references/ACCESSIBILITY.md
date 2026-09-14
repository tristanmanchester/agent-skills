# Accessibility in the actual interface

Define the applicable standard, level, pages, states, and assistive-technology
scope before making a conformance claim. The checks below are selected design
and implementation checks, not all of WCAG 2.2 or a legal opinion. Automated tools,
source inspection, and screenshots cannot replace testing the rendered interaction.

## Text and visual information

WCAG contrast minimums are 4.5:1 for ordinary text and 3:1 for text meeting the
criterion's large-text definition, with specified exceptions. Compare unrounded
ratios, not rounded display values. Inspect actual foreground/background colours
in every relevant state; transparency, gradients, images, and theme changes need
the effective background. Do not rely on colour alone for meaning. Non-text UI
and meaningful graphic contrast require their own assessment.

The bundled helper accepts only opaque #RGB/#RRGGBB sRGB pairs. Resolve SKILL_DIR
to this installed directory and run, for example:

```bash
python "$SKILL_DIR/scripts/contrast_check.py" '#0f172a' '#ffffff'
```

Its exit 0 means the supplied pair meets the normal-text threshold; exit 1 means
it does not, even when it meets the large-text threshold. Exit 2 is a usage/input
error. The helper does not inspect a website, font size, alpha compositing, semantic
contrast, or full conformance. Keep it as a small calculation tool, not a page audit.

Source: https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html

## Keyboard, focus, and semantics

Use native controls with accurate names, roles, and states. Preserve a logical
reading/focus sequence supporting meaning and operation; do not repair arbitrary
CSS rearrangement with positive tabindex values. Include keyboard routes and no
unintended traps. Use meaningful headings, landmarks, labels, and image alternatives.

Focused controls need a visible indicator. WCAG 2.2 AA's Focus Not Obscured minimum
also requires the focused component not be entirely hidden by author-created
content. Test sticky headers, cookie banners, drawers, and onscreen keyboards.
A visible ring on an offscreen/covered control is not useful. The separate enhanced
focus criteria have different levels; don't label every AAA prescription as AA.

For dialogs, use a suitable implemented dialog pattern, accessible labelling,
appropriate initial focus, dismissal, focus containment for a modal, background
inertness, and restoration to a sensible location. A decorative overlay or an
aria-modal attribute alone does not provide that behaviour.

Source: https://www.w3.org/WAI/WCAG22/Understanding/focus-not-obscured-minimum.html

## Pointer input and alternatives

WCAG 2.2 AA's target-size minimum is 24 by 24 CSS pixels, subject to defined spacing,
equivalent-control, inline, user-agent, and essential exceptions. Check the actual
hit area and neighbours; a 24-pixel bounding box around a round target does not
necessarily contain a 24-pixel square. Larger comfortable targets can be a design
goal without misrepresenting the minimum or exceptions.

Provide a single-pointer non-drag alternative for functionality using dragging,
except where the criterion allows an essential or user-agent exception. Keyboard
support is separately important and is not by itself the single-pointer alternative.
Examples include move-up/down buttons alongside drag reordering. Test touch,
pointer cancellation, disabled states, and accidental repeated activation.

Sources:
- https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- https://www.w3.org/WAI/WCAG22/Understanding/dragging-movements.html

## Forms and status changes

Give fields persistent programmatic labels, understandable instructions, and
specific associated error messages. Preserve entered data. After submission,
choose an appropriate error summary/focus or first-invalid-field pattern for the
form; don't prescribe one focus target universally. Dynamic error/status changes
need an appropriate announcement strategy. aria-describedby associates descriptive
text but is not a blanket guarantee that every later change is announced.

Avoid duplicate or excessively chatty live announcements. Test actual focus,
validation, successful submission, and server-error behaviour with the intended
screen reader/browser. Don't make a transient toast the only place to learn how
to recover, and don't call a pending request a completed action.

Source: https://www.w3.org/WAI/tutorials/forms/notifications/

## Responsive content and motion

Test zoom, reflow, increased text spacing, long/localised strings, meaningful images,
and tables without losing actions or information. Use appropriate captions and
text alternatives for media. Honour reduced-motion preferences and provide control
or a static alternative for nonessential movement; inspect CSS and JavaScript paths,
not just one library setting. Avoid flashing and motion-dependent completion logic.

Record the pages/states, tools, actual manual tests, findings, and untested cases.
A colour calculation, linter score, or five-second expert glance is not a complete
accessibility or usability test. Sources reviewed 2026-09-13; consult the complete
current standard for a formal assessment: https://www.w3.org/TR/WCAG22/.
