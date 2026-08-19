---
name: write-good-docs
description: Use this skill when the requested output will be human-facing documentation, or when existing documentation must be written, rewritten, shortened, reorganized, or reviewed. Trigger for READMEs, guides, tutorials, how-tos, reference docs, API or CLI docs, runbooks, troubleshooting, onboarding, architecture or design docs, RFCs or ADRs, migration guides, release notes, and docstrings or comments; also trigger on vague requests such as "document this," "write the docs," "clean up this README," or "make this guide clearer." Do not trigger for ad hoc explanations, marketing copy, email, chat, social posts, fiction, or code-only work unless documentation is a material deliverable.
license: CC-BY-4.0; see ATTRIBUTION.md
metadata:
  version: "2.0.0"
  source: "Google developer documentation style guide"
  research-date: "2026-08-18"
---

# Write good documentation

Write for a specific human who needs to understand something, decide something, or complete a task. Produce the shortest document that lets that reader succeed without losing facts, caveats, safety information, or necessary context.

This skill governs documentation prose and structure. It is not a source of product facts. Derive facts from the user's material and authoritative project sources.

## Priorities

Resolve tradeoffs in this order:

1. **Technical truth and safety.** Do not invent, weaken, or silently change facts, requirements, uncertainty, warnings, code, commands, identifiers, or interface labels.
2. **The reader's outcome.** Include what the intended reader needs to act or understand. Exclude material that serves only the author, implementation history, or an appearance of completeness.
3. **Findability and sequence.** Make the answer easy to locate, scan, and follow from a search result or direct link.
4. **Clarity and concision.** Prefer direct, literal, natural language. Remove avoidable friction and repetition.
5. **Consistency and mechanics.** Follow the user's requirements and the project's established style before this skill's defaults.

Do not sacrifice a higher priority to satisfy a lower one.

## Before writing

Use the available context before asking the user for information.

1. Read the request and any supplied source material.
2. When working in a repository, inspect the relevant existing docs, templates, code, tests, configuration, issues, and pull requests. Use the smallest evidence set that establishes the facts and local conventions.
3. Identify:
   - the intended reader;
   - what the reader must understand, decide, or accomplish;
   - what the reader can already be expected to know;
   - the document's primary job;
   - the requested scope, format, length, dialect, and tone.
4. Record exact material that must not drift: product and feature names, UI labels, API names, identifiers, commands, code, paths, filenames, links, values, dates, limits, warnings, and contractual wording.
5. Separate established facts from inferences, proposals, and unknowns. Verify consequential claims. When evidence is unavailable, preserve the uncertainty or use an explicit placeholder instead of guessing.

Infer reasonable defaults from the project and request. Ask a question only when an unresolved ambiguity would materially change the document and cannot be resolved from available sources.

## Choose one primary job

A document becomes muddy when it tries to teach, direct, explain, and catalog everything at once. Choose the reader's main need:

| Reader need | Primary document job |
|---|---|
| Learn by doing in a controlled path | Tutorial |
| Complete a real task | How-to guide |
| Look up exact facts | Reference |
| Understand why or how something works | Explanation or concept guide |
| Evaluate or record a technical choice | Design document, RFC, or ADR |
| Diagnose, recover, or operate a system | Troubleshooting guide or runbook |
| Start using a project or team system | README or onboarding guide |
| Move between versions or behavior | Migration guide or release note |

A page can contain supporting material, but one job must control its structure. Link to a different document rather than burying a second document inside the first.

Read [Document shapes](references/document-shapes.md) before creating or substantially restructuring a full document.

## Workflow

### 1. Build a truth set

Collect only the facts needed for the requested scope. Note prerequisites, permissions, constraints, failure modes, compatibility, side effects, and unresolved questions. Treat implementation details as evidence, not automatically as reader-facing content.

For code, commands, APIs, UI, architecture, or operational material, read [Technical fidelity](references/technical-fidelity.md).

### 2. Plan the reader's path

Write a one-sentence private statement of the document's job:

> After reading this, **[reader]** can **[outcome]** under **[conditions]**.

Use it to decide what belongs. Order information by the reader's workflow or reasoning, not by the order in which the author discovered it or the product is implemented.

Usually:

1. Lead with the outcome, decision, or essential context.
2. State prerequisites and governing conditions before dependent material.
3. Present the recommended path before alternatives.
4. Put warnings immediately before the risky action.
5. Give verification, rollback, or next steps where the reader needs them.

### 3. Draft the minimum complete version

Write the smallest version that is accurate and usable.

- Address the reader as **you** in task-oriented content. Use imperatives for steps.
- Use active voice and name the actor when responsibility matters.
- Put conditions before the instruction or result they govern.
- Use one term for one concept. Do not rotate synonyms for variety.
- Define unfamiliar terms at the first useful mention.
- Prefer a clear default over an undifferentiated menu of options.
- Use examples only when they remove a real ambiguity or make an abstraction concrete.
- Make every heading, list, table, note, and code block earn its place.

For dense, awkward, inflated, or AI-sounding prose, read [Clear prose](references/clear-prose.md).

### 4. Compress without damaging meaning

Run a deletion pass after the content is correct.

Remove:

- pre-announcements such as “This document explains”;
- generic background that does not change a decision or action;
- repeated claims, conclusions, and transitions;
- sections added only because a template commonly contains them;
- headings that contain one short paragraph and add no navigation value;
- bullets that would read better as one or two sentences;
- obvious descriptions of code or UI that the reader can already see;
- adjectives and adverbs that do not add testable meaning;
- meta-commentary about the writing, research, or answer.

Do not remove prerequisites, distinctions, warnings, exceptions, rationale for a consequential decision, or repetition required for safe standalone use.

### 5. Validate as a first-time reader

Read [Final review](references/final-review.md) before finalizing a substantial draft, rewrite, or formal documentation review. Fix the document, then review it again.

## Load references only when needed

Progressive disclosure matters. Do not load every reference for every task.

| Situation | Read |
|---|---|
| Creating or reshaping a README, tutorial, how-to, reference page, concept guide, design doc, ADR, runbook, onboarding guide, migration guide, or release note | [Document shapes](references/document-shapes.md) |
| Rewriting for clarity, shortening prose, removing repetition, fixing tone, or avoiding common agent-writing patterns | [Clear prose](references/clear-prose.md) |
| Writing numbered steps, tutorials, operational procedures, troubleshooting, incident response, or destructive actions | [Procedures and troubleshooting](references/procedures-and-troubleshooting.md) |
| Documenting code, commands, output, APIs, UI, architecture, configuration, examples, or exact technical literals | [Technical fidelity](references/technical-fidelity.md) |
| Deciding headings, paragraphs, lists, tables, links, notices, images, Markdown, HTML, accessibility, localization, or inclusive wording | [Structure and accessibility](references/structure-and-accessibility.md) |
| Resolving spelling, capitalization, punctuation, numbers, dates, units, modality, or recurring word-choice questions | [Style reference](references/style-reference.md) |
| A concrete before-and-after pattern would help | [Examples](references/examples.md) |
| A condensed rule is insufficient or likely to have changed | [Official source map](references/source-map.md) |
| Finalizing a substantial document or formal audit | [Final review](references/final-review.md) |

Do not open [Style reference](references/style-reference.md) merely because the task contains prose. It is an edge-case and copyediting reference, not the writing workflow.

## Common agent failures

Actively prevent these patterns:

- **Generic openings:** “In today's fast-paced world,” “This comprehensive guide,” or a paragraph that repeats the title.
- **Documentation-shaped padding:** an unnecessary overview, benefits section, key takeaways, best practices list, FAQ, and conclusion added to make a short topic look complete.
- **Architecture dumps:** describing modules in implementation order when the reader needs a task or decision path.
- **Bullet soup:** converting every thought into a list, including items that are not parallel or easier to scan.
- **Heading inflation:** many tiny sections, repeated section names, or headings that do not help retrieval.
- **Synthetic certainty:** filling evidence gaps with plausible defaults, behavior, limits, reasons, or future plans.
- **Style overreach:** changing code, commands, identifiers, UI labels, established terminology, dialect, or unrelated formatting while “cleaning up” prose.
- **Option dumping:** listing every possible approach without choosing or explaining a default.
- **Repeated conclusions:** restating the same point in the opening, body, summary, and closing.
- **Marketing language:** “seamless,” “robust,” “powerful,” “revolutionary,” “best-in-class,” or unsupported claims about ease, speed, security, or reliability.
- **Reader blame:** “obviously,” “simply,” “just,” “easy,” or instructions that assume failure is the reader's fault.
- **Visual-only directions:** “click the button on the right,” “see above,” or relying on color, position, punctuation, or an image to carry essential meaning.

## Editing existing documentation

Match the requested scope.

- For a local edit, make a local edit. Do not restyle the whole file.
- Preserve supported facts, qualifications, warnings, anchors, links, terminology, and document history.
- Preserve exact literals unless the user asked to correct them and an authoritative source supports the correction.
- Match a coherent existing dialect, tone, heading system, and markup convention.
- Restructure only when requested or when the current structure materially blocks the reader's goal.
- Do not “improve” an historical ADR or release note by rewriting its decision in light of later events. Add a superseding record when appropriate.
- Do not remove intentional repetition from standalone procedures, warnings, generated reference sections, or content commonly entered from search.

## Review behavior

Follow the user's requested review format. Otherwise:

- When asked to edit, return the improved text or patch rather than an essay about style.
- When asked to review, report only material issues. For each issue, give the location, reader impact, and a concrete revision.
- Distinguish factual or usability problems from optional style preferences.
- Rank accuracy, safety, task completion, ambiguity, accessibility, and maintenance cost above cosmetic consistency.
- Do not cite this skill or mention that prose was “Google style” inside the document unless the user asks for that context.

## Default language choices

When the project does not establish a different convention:

- use American English;
- use sentence case for titles and headings;
- use a conversational, direct, respectful tone;
- use the serial comma;
- use **must** for requirements, **can** for capability or optional action, and **might** for possibility;
- avoid ambiguous **should** when a requirement, recommendation, expected state, or possibility can be stated precisely;
- use exact dates, versions, and lifecycle states instead of **current**, **new**, **latest**, or **soon**;
- use descriptive link text;
- put code-related literals in `code font` and exact UI labels in **bold**.
