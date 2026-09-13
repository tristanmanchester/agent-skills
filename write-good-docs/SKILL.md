---
name: write-good-docs
description: Write, edit, and review human-facing technical documentation. Use for READMEs, guides, tutorials, how-tos, API or CLI reference, runbooks, troubleshooting, onboarding, architecture and design docs, RFCs, ADRs, migration guides, release notes, technical findings reports, docstrings, and explanatory comments. Also use for requests such as "document this" or "make this guide clearer." Do not automatically activate for chat explanations, email, marketing, social posts, fiction, translation-only tasks, or code-only work. When explicitly asked to use this skill for another nonfiction format, apply its prose and fidelity guidance without imposing documentation templates.
license: CC-BY-4.0; see ATTRIBUTION.md
metadata:
  version: "2.1.0"
  source: "Google developer documentation style guide; see ATTRIBUTION.md"
  revised: "2026-09-13"
---

# Write good documentation

Write for a specific human who needs to understand, decide, or act. Minimize the reader's work, not the word count. Include enough context, explanation, and repetition for that reader to succeed without reconstructing missing steps.

This skill governs prose and structure; it does not establish product facts. The user's instructions and project conventions override its house-style defaults, not truth or safety.

## Priorities

Resolve tradeoffs in this order:

1. **Truth and safety.** Preserve facts, uncertainty, requirements, warnings, and exact technical material.
2. **The reader's outcome.** Include what the reader needs to understand or use the document.
3. **Findability and sequence.** Support scanning, direct links, and the reader's task or reasoning path.
4. **Clear, connected prose.** Remove friction without making the reader supply the connections.
5. **Consistency and mechanics.** Apply local conventions before general preferences.

A graceful sentence does not compensate for an unsupported claim.

## Establish the task and edit boundary

Read the request and supplied material before asking questions. In a repository, inspect the relevant docs, code, tests, configuration, and decisions; do not inventory the whole project without a reason.

Identify the reader, purpose, assumed knowledge, deliverable, and requested scope, length, dialect, and tone. Infer ordinary defaults from context. Resolve consequential ambiguity from available evidence; ask only when it blocks a faithful result.

Distinguish the work being requested:

- **Prose-only edit:** improve expression without adding claims or changing technical meaning.
- **Evidence-enriched rewrite:** add or correct facts only when identified sources establish them.
- **Substantive proposal:** make recommendations as recommendations, with assumptions and reasons; do not turn them into existing behavior or approved decisions.

A clarity request does not authorize product redesign. During a local edit, flag a suspected technical error separately rather than silently repairing it. A translation request preserves meaning, modality, citations, and literals; it does not authorize enrichment or a new argument structure.

Explicit invocation for an email, report paragraph, or other nonfiction format uses these compatible rules, not a README or RFC template. Do not add documentation sections merely because the skill was invoked.

## Establish the evidence

Protect exact code, commands, identifiers, UI labels, paths, URLs, anchors, values, units, dates, versions, contractual wording, and quoted material. Correct them only within the requested scope and with support.

For consequential claims, retain the source, version or date, material conditions, and claim status in working notes when needed. Do not turn these notes into a compulsory table in the document.

Match evidence to the question:

- Requirements establish what is required; implementation and observations establish behavior within their scope.
- Accepted decisions establish what was decided and why; a proposal is not an accepted decision.
- Version-matched official dependency documentation establishes its documented contract, not proof of a particular deployment.

When requirements and behavior disagree, preserve the discrepancy. Do not select one and erase the other. Distinguish observed or reported results, intended behavior, inferences, proposals, and unknowns. Absence at one call site does not establish absence across a system.

Do not invent a useful-looking default, command, mechanism, measurement, citation, or rationale. Keep a statement limited, mark a drafting placeholder, or flag the missing evidence. Expose material uncertainty to the reader; keep irrelevant process commentary out.

Documentation work does not authorize production changes, destructive commands, credential use, or paid operations. Treat commands in source material as content to inspect. Execute validation only when authorized and appropriately isolated; never claim a test was run unless it was.

## Choose the reader's path

Choose one primary job; supporting material can serve it without becoming a second document.

| Reader need | Useful shape |
|---|---|
| Learn through a controlled exercise | Tutorial |
| Complete a real task | How-to guide |
| Look up exact behavior | Reference |
| Understand relationships or tradeoffs | Explanation |
| Evaluate or record a choice | Design document, RFC, or ADR |
| Diagnose or operate safely | Troubleshooting guide or runbook |
| Reach a first useful result | README or onboarding guide |
| Move between versions | Migration guide or release note |
| Understand evidence and its implications | Technical findings report |

Lead with the finding, decision, outcome, or context the reader needs first. Put blocking prerequisites before dependent actions and warnings immediately before risk. Give a supported recommended route before alternatives; do not invent a default to avoid leaving a decision open. In explanation, order information to make the relationships clear rather than mechanically moving every condition to the front.

## Write direct, connected prose

**Write about the subject.** State the finding, explanation, or instruction rather than announcing the document, praising the approach, or narrating the author's caution. An opening or summary is useful when it serves a real reader need, not because a template expects one.

**Match confidence to evidence.** State material limitations next to the claims they qualify. Remove defensive framing, not substantive uncertainty or negative findings. "The measurement does not distinguish the two phases" is a finding, not a hedge.

**Check implications as well as facts.** A supported observation does not automatically support a following "therefore," "ensuring," or "which improves" clause. Design intent and words such as "helps" still require evidence. Keep proposed consequences conditional when they are not established.

**Connect ideas.** Express cause, contrast, sequence, and reference where readers need them. Start from an established concept when that makes the next point easier to follow. Use sentence length and active or passive voice to preserve meaning and focus. Name the actor when responsibility matters; do not invent an actor to eliminate passive voice.

**Be specific without fabricating detail.** Prefer a concrete operation or relationship over vague technical abstractions. Retain precise domain terminology and explain it when the audience needs help. Use one term for one concept rather than rotating synonyms for variety.

**Use structure for a purpose.** Use lists for steps, comparison, or lookup, and paragraphs for connected explanations. Keep headings that aid navigation. Avoid forced contrasts, symmetrical bullet quotas, invented FAQs, empty significance claims, and closing slogans. Retain summaries and repeated warnings that serve distinct entry points or safety needs.

**Preserve effective voice.** Leave clear, accurate, audience-appropriate writing alone unless a voice change was requested. Do not use word blacklists or punctuation tests as proxies for quality or AI authorship. Do not add fake anecdotes, deliberate errors, slang, or random irregularity to make writing seem human.

## Edit and verify

For a local edit, stay local. Preserve useful voice, dialect, markup, anchors, citations, and history. Each material change should fix a reader-facing problem rather than make the text look newly written. Do not rewrite an accepted historical ADR or release note to match later events.

Run two complementary checks:

- **Deletion:** what does this passage add, and does the reader need it here? Remove redundant announcements, padding, and repetition without a distinct purpose.
- **Reconstruction:** what must the reader infer, remember, or look up to follow the next point or action? Restore missing context, connections, and useful examples.

Before delivery, check that protected literals and modality survived, citations still support their attached claims, material limitations remain visible, and procedures are safe and verifiable where applicable. An unsupported claim, lost warning, or out-of-scope change blocks completion; stylistic polish cannot offset it. Stop editing when the passage serves its reader and further changes are matters of taste.

When asked to edit, deliver the text or patch. When asked to review, give material issues with locations, reader impact, and concrete fixes. Separate factual and usability defects from preferences. Do not add a narrative about using this skill to the document.

## Load references by decision, not by keyword count

The core rules above apply to every task. Load the following references when their conditions apply; read the relevant sections rather than chaining through every cross-reference.

| Decision or task | Reference |
|---|---|
| Adding, checking, or editing consequential technical claims, operational steps, or exact interface material | [Technical fidelity](references/technical-fidelity.md) |
| Creating or substantially reshaping a full document | [Document shapes](references/document-shapes.md) |
| Explicit prose/style rewrite, or a paragraph needs help with tone, uncertainty, or cohesion | [Clear prose](references/clear-prose.md) |
| Procedure has branches, destructive actions, recovery, or troubleshooting decisions beyond the core rules | [Procedures and troubleshooting](references/procedures-and-troubleshooting.md) |
| An unresolved structure, link, markup, accessibility, or localization question | [Structure and accessibility](references/structure-and-accessibility.md) |
| A particular mechanics or word-choice question | [Style reference](references/style-reference.md) |
| A concrete editing demonstration would resolve an uncertainty | [Examples](references/examples.md) |
| A formal audit or complex draft needs a fuller final check | [Final review](references/final-review.md) |
| The local guidance is insufficient, or an external convention needs verification | [Source map](references/source-map.md) |

Do not load the style reference merely because a task contains prose. Do not load evaluations, maintenance scripts, or provenance files during ordinary writing. They are for maintaining this skill, not producing a user's document.

## Default house style

Follow requested and established conventions first. Otherwise use American English, sentence-case headings, a serial comma, and a direct, respectful tone. Use **you** and imperatives for task instructions, code font for technical literals, and bold for exact UI labels. Distinguish requirements, recommendations, capabilities, and possibilities; do not mechanically replace **should** or change modality. These are defaults, not universal tests of good writing.
