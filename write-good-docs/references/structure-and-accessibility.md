# Structure and accessibility

Read this reference for headings, paragraphs, lists, tables, notices, links, images, Markdown, HTML, accessibility, localization, and inclusive wording.

## Titles and headings

- Use one level-1 title for a standalone page unless the project's format supplies it elsewhere.
- Use sentence case unless the project requires another convention.
- Make titles and headings descriptive, unique, and useful in search results or a table of contents.
- Use task verbs for task sections: “Configure authentication.”
- Use noun phrases or clear questions for concepts and reference: “Authentication flow” or “Why tokens expire.”
- Preserve a logical hierarchy. Do not skip levels or leave empty headings.
- Avoid many tiny sections. A heading should create a useful navigation boundary.
- Preserve stable anchors when editing published or linked documentation.
- Do not use **Introduction**, **Overview**, **Background**, or **Conclusion** when a more specific heading says what the section contains.

## Openings

Lead with the outcome, decision, applicability, or essential context. Do not pre-announce the document.

A useful opening often answers one or two of these questions:

- What can the reader do or understand here?
- When does this guidance apply?
- What decision was made?
- What risk or change requires attention?

Do not front-load product history, a glossary, or broad motivation unless the reader needs it before the main content.

## Paragraphs

- Keep one main idea per paragraph.
- Put the critical point first.
- Use short paragraphs, but do not fragment one coherent idea into artificial one-sentence blocks.
- Left-align prose. Do not rely on manual line breaks inside paragraphs.
- Use a list, table, or code block only when its structure makes information easier to retrieve or follow.

## Lists

Choose the semantic list type:

- numbered list for a required sequence or ranked order;
- bulleted list for parallel nonsequential items;
- description list for term-description pairs when the format supports it.

Write lists well:

- use parallel grammar;
- make the lead-in a complete sentence when it ends with a colon;
- keep capitalization and punctuation consistent;
- keep each item focused;
- state whether choices are exclusive, cumulative, or conditional;
- avoid deep nesting;
- do not use a list for one item;
- do not turn a paragraph into bullets merely to make it look scannable.

When each item needs several paragraphs, use subsections instead of oversized bullets.

## Tables

Use a table for compact comparison or predictable lookup across the same attributes.

- Introduce the table in text.
- Use descriptive row and column headers.
- Keep cell content concise.
- Avoid merged cells, visual-only grouping, and long narrative prose.
- Do not use a table when readers must read every row in order.
- Ensure the same meaning is available without color or spatial styling.
- Consider a list or repeated subheadings for narrow screens and accessibility.

## Notices

Use notices sparingly and choose severity by consequence:

- **Note:** information that prevents confusion but is not part of the main path.
- **Tip:** optional guidance that improves the experience.
- **Caution:** risk of data loss, cost, degraded behavior, or difficult recovery.
- **Warning:** risk of serious harm, security compromise, or major irreversible impact.

Put essential prerequisites and ordinary instructions in the main flow, not in notes. Place a caution or warning immediately before the protected action.

## Links and cross-references

- Use descriptive link text that works out of context.
- Name the destination or task: “See [Configure workload identity]” rather than “click here.”
- Do not use raw URLs in prose unless the literal URL is the subject.
- Avoid **above**, **below**, **previous**, and **next** when a heading or page name is clearer.
- Link only the meaningful words, not surrounding punctuation.
- Do not force links to open in a new tab without a specific reason.
- Preserve inbound links and anchors when restructuring.
- Avoid link chains that make readers traverse several pages to reach a required step.

## Code and UI formatting

Unless project style differs:

- put commands, identifiers, filenames, paths, configuration keys, and literal values in `code font`;
- put exact visible UI labels in **bold**;
- do not use code font for ordinary technical concepts;
- keep punctuation outside inline formatting unless it is part of the literal;
- introduce code blocks and explain why the reader needs them.

## Images and diagrams

Use an image only when it communicates structure, state, or visual interaction more efficiently than prose.

- Provide concise alt text for informative images.
- Use empty alt treatment for decorative images.
- Give complex diagrams a nearby text description that conveys the relationships and conclusions.
- Do not repeat a caption verbatim in alt text.
- Name entities and flows consistently with the prose.
- Do not rely on color alone; add labels, patterns, shapes, or text.
- Use sufficiently high-resolution or vector assets when practical.
- Keep essential instructions and data in text, not only in an image.

## Accessibility

The document must remain usable when the reader:

- uses a screen reader;
- navigates by keyboard;
- enlarges text or reads on a narrow screen;
- cannot distinguish colors;
- cannot see an image, hear audio, or use a pointer;
- enters through search at a subsection rather than the top.

Use semantic headings, lists, tables, links, labels, and notices. Do not encode meaning only in punctuation, font style, capitalization, position, color, or visual shape.

For forms and interactive instructions:

- name fields and controls by their labels;
- state what an error means and how to correct it;
- do not use placeholder text as the only label;
- make keyboard paths possible when documenting a supported interface.

## Global audience and localization

- Prefer literal wording over idioms, puns, metaphors, and culture-specific references.
- Use unambiguous dates and times.
- State units and currencies clearly.
- Avoid examples that require knowledge of one country's institutions, addresses, holidays, or sports unless relevant.
- Keep sentence structure straightforward for readers using English as an additional language.
- Avoid splitting a sentence with formatting or placeholders in ways that make translation difficult.
- Preserve variables and code literals so translators do not mistake them for prose.

## Inclusive language

Use terms that describe the technical role or behavior precisely.

- Avoid unnecessary gender, age, disability, race, nationality, family, or cultural assumptions.
- Use neutral plural constructions when a singular pronoun would be awkward.
- Replace harmful or exclusionary metaphors with domain-specific terms when technically equivalent.
- Preserve an official standard or literal identifier when changing it would be inaccurate; explain it when useful.
- Do not perform blind search-and-replace in code, APIs, database values, historical quotations, or compatibility documentation.
- Use fictional examples without stereotypes or real personal data.

Common alternatives include:

- **allowlist/blocklist** or a precise access rule instead of **whitelist/blacklist**;
- **primary/replica**, **leader/follower**, **controller/worker**, or the real relationship instead of **master/slave**;
- **preliminary check**, **validation**, or the exact check instead of **sanity check**;
- **stop responding** instead of **hang** as a metaphor when that wording is accurate;
- **person-hours** instead of **man-hours**;
- **everyone**, **people**, **team**, or the named audience instead of **guys**.

## Footnotes and mathematical notation

Avoid footnotes. They separate information from its context and can create accessibility and localization problems. Prefer a sentence in the main flow, a short parenthetical, a note, or a cross-reference. When a footnote is unavoidable, use the publication's standard semantic markup and never put essential information only in the footnote.

For mathematical notation:

- use conventional symbols and define every variable;
- distinguish variables from operators, function names, numerals, and units;
- explain what the equation calculates and what the result means;
- use true mathematical characters when the format supports them;
- provide a text equivalent when an equation or diagram would otherwise be inaccessible;
- add a concrete implication or example when the abstract result is difficult to interpret.

## Markdown and HTML

- Follow repository conventions first.
- Prefer Markdown for ordinary prose when the platform supports it.
- Use HTML only when Markdown cannot express the required semantics or the project standard requires it.
- Keep source readable and avoid unrelated reformatting.
- Use semantic HTML elements rather than presentational markup.
- Do not use tables, headings, blockquotes, or code blocks merely for visual styling.
- Use relative links only when the hosting and repository conventions make them stable.
- Keep heading IDs and link targets valid after edits.
