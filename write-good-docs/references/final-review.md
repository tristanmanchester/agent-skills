# Final review

Use this compact review for a substantial draft, rewrite, or formal documentation audit. Fix issues and repeat the review. Do not turn it into a report unless the user asked for a report.

## 1. Truth

- [ ] Every consequential fact is supported by the supplied material or an authoritative source.
- [ ] Facts, inferences, proposals, and unknowns are not blurred together.
- [ ] Exact code, commands, identifiers, values, paths, links, names, UI labels, versions, dates, and error text are preserved or authoritatively corrected.
- [ ] No prerequisite, permission, caveat, warning, side effect, compatibility limit, or failure condition was lost.
- [ ] The document does not invent defaults, support status, guarantees, measurements, reasons, or future plans.

## 2. Reader outcome

- [ ] The intended reader and the document's primary job are clear from context.
- [ ] The title and opening reveal the outcome, decision, or applicability without pre-announcement.
- [ ] Information follows the reader's task or reasoning path, not implementation or discovery order.
- [ ] The recommended path appears before alternatives.
- [ ] The reader can tell what to do, how to verify it, and what to do when it fails, where applicable.

## 3. Clarity and concision

- [ ] Each section, paragraph, sentence, list, table, and example adds distinct value.
- [ ] Repeated introductions, conclusions, transitions, benefits, and background are removed.
- [ ] Conditions precede dependent actions or outcomes.
- [ ] Actors, requirements, recommendations, expected states, and possibilities are explicit.
- [ ] Terminology is consistent and unfamiliar terms are defined only when needed.
- [ ] The prose is direct, natural, literal, and free of hype, reader blame, and generic AI padding.
- [ ] Lists and headings improve navigation rather than fragmenting ordinary prose.

## 4. Technical usability

- [ ] Procedures have safe prerequisites, one clear action path, and observable success criteria.
- [ ] Commands are runnable, scoped, and distinguish input, output, placeholders, and destructive effects.
- [ ] Code samples are valid or clearly marked as illustrative or incomplete.
- [ ] API and configuration reference entries expose defaults, constraints, errors, side effects, and versions that readers need.
- [ ] Design and architecture documents cover relevant tradeoffs, failure modes, migration, rollback, and unresolved questions rather than only the happy path.

## 5. Structure and access

- [ ] Headings create a useful scan path and remain understandable when reached directly.
- [ ] Important information is not hidden only in a note, table, image, link, or visual position.
- [ ] Links are descriptive and lead to the stated destination.
- [ ] Images, tables, controls, and instructions are accessible without relying on color, location, audio, or pointer use.
- [ ] Dates, units, examples, and wording are unambiguous for a global audience.
- [ ] Markup, dialect, anchors, and formatting match the project, with no unrelated restyling.

## 6. Deletion challenge

Read only the title, opening, headings, and first sentence of each paragraph. The document should still reveal its structure and main points.

Then ask of every remaining section:

> What would the reader lose if this disappeared?

If the answer is nothing material, remove it.
