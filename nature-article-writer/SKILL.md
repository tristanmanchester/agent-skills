---
name: nature-article-writer
description: Drafts, rewrites, diagnostically critiques, and style-calibrates primary research manuscripts for Nature and Nature Portfolio journals. Use when the user wants a Nature-style title, summary paragraph or abstract, introduction, results, discussion, methods, figure legends, presubmission enquiry, cover letter, reviewer response, or when a scientific draft sounds generic, jargon-heavy, structurally weak, or AI-ish and needs precise, broad-reader-friendly prose without inventing data, analyses, or references. Best for primary research articles and letters rather than reviews or press releases unless explicitly adapting one.
compatibility: Best in skills-compatible agents with file read/write access. Optional Python 3 enables scripts/nature_preflight.py and scripts/prose_fingerprint.py. If web access is available, verify the live guide and inspect recent papers when a specific journal is named.
metadata:
  author: OpenAI
  version: "2.0.0"
  updated: "2026-04-19"
  target: Nature and Nature Portfolio primary research
---

# Nature Article Writer

Write and revise primary research manuscripts so they feel editorially mature: precise, proportionate, detailed where detail matters, and genuinely pleasurable for a scientist to read. Beautiful Nature-style prose is not ornate prose. It is clear, load-bearing prose with strong logic, good sentence movement, and no wasted claims.

This skill optimises for editorial quality, reader trust, and human-sounding scientific prose. It does **not** optimise for AI-detector evasion.

Do not imitate a named living author. Emulate journal expectations, the user's own prior writing if supplied, and the specific paper's evidence profile.

## When to activate this skill

Use this skill when the user:
- names Nature or a Nature Portfolio journal
- asks for "Nature-style", "Nature journal", or "high-impact journal" scientific writing
- wants a title, summary paragraph, abstract, introduction, results, discussion, methods, figure legend, presubmission package, cover letter, or reviewer response
- wants a scientific draft to sound more natural, less generic, less formulaic, or less obviously machine-written
- wants to convert notes, figures, bullet points, or a rough draft into a submission-ready manuscript
- wants a diagnostic pass on manuscript structure, claim calibration, prose quality, or compliance

## Success standard

A strong output from this skill should feel like it was written by a careful scientist-editor who understands both the data and the journal:
- the central claim is evident early and never overstated
- adjacent-field readers can follow the logic without drowning in jargon
- each paragraph has a job
- each sentence earns its place
- results progress by question and answer, not lab chronology
- the prose is varied but restrained
- limitations are surfaced before reviewers must drag them out
- end matter and policy-sensitive statements are present or explicitly marked as missing

## Non-negotiables

- Never invent data, methods, figures, ethics approvals, accession numbers, references, software versions, statistical results, or journal-specific limits.
- Never strengthen a claim beyond the evidence actually supplied.
- Never hide uncertainty. Mark missing facts explicitly with `[confirm]`, `[insert ref]`, `[insert accession]`, or a short `Issues to confirm` list.
- Never use AI-generated figures or image content for publication.
- Never copy distinctive phrasing from published papers. Use exemplars for structure, rhythm, and level-setting, not sentence theft.
- If AI did more than copy editing, remind the user to check whether disclosure is required under the target journal's policy. Human authors remain accountable for the final text.

## Default workflow

### 1. Build the manuscript brief

Infer or assemble the minimum brief:
- target journal and content type
- one-sentence central claim
- why it matters outside the immediate subfield
- evidence ladder: 3-6 concrete results, figures, or analyses that support the claim
- strongest prior work and the precise gap
- strongest limitation or boundary condition
- data, code, and materials availability
- ethics or compliance facts if humans, animals, clinical samples, or sensitive data are involved

If the user has scattered notes, use [assets/manuscript-brief-template.md](assets/manuscript-brief-template.md).

### 2. Calibrate before you draft

Use both of these calibration layers when possible.

#### A. Journal calibration
Consult [references/modes.md](references/modes.md) and [references/journal-calibration.md](references/journal-calibration.md).

- Choose the closest bundled mode:
  - `nature-article`
  - `nature-letter`
  - `portfolio-article`
  - `portfolio-letter`
- If the user names a specific journal and web access is available, verify the live guide and inspect 2-4 recent primary research papers from that journal.
- Build a short internal style card: title texture, opening-paragraph shape, heading policy, legend density, end-matter order, and how aggressively claims are hedged.

#### B. Exemplar anchoring
If the user supplies their own accepted papers, lab style guides, or a high-quality draft they want to sound like, use [references/exemplar-anchoring.md](references/exemplar-anchoring.md) and optionally run:

```bash
python3 scripts/prose_fingerprint.py --candidate draft.md --reference exemplar1.md exemplar2.md --format text
```

Imitate **broad habits** such as sentence length range, paragraph density, degree of overt signposting, and tolerance for technical detail. Do not imitate distinctive turns of phrase.

### 3. Build the editorial architecture

Before line-level drafting, create:
- a one-sentence paper promise
- a figure-claim matrix
- a paragraph map for the major sections

Use:
- [assets/editorial-blueprint-template.md](assets/editorial-blueprint-template.md)
- [assets/figure-claim-matrix-template.md](assets/figure-claim-matrix-template.md)
- [assets/paragraph-map-template.md](assets/paragraph-map-template.md)
- [references/editorial-architecture.md](references/editorial-architecture.md)

This is the main upgrade over a generic "write the paper" prompt. The prose improves when the structure is load-bearing before wording starts.

### 4. Draft in evidence order, not display order

Default drafting order:
1. figure plan and one-sentence take-home message for each figure
2. Results
3. Methods
4. Discussion or concluding synthesis
5. opening context paragraph or Introduction
6. summary paragraph or abstract
7. title
8. figure legends
9. availability statements and other end matter
10. cover letter or presubmission material if requested

Starting from figures and claims produces more grounded prose than starting from the title or abstract.

### 5. Shape paragraphs deliberately

Every paragraph needs:
- a topic sentence that names the paragraph's job
- evidence or reasoning that advances the job
- a final stress position that lands the important point or hands the reader to the next paragraph

Use [references/sentence-craft.md](references/sentence-craft.md) and [assets/paragraph-map-template.md](assets/paragraph-map-template.md). Prefer old-to-new information flow, concrete verbs, and sentences that end on the point that matters.

### 6. Run a human-voice pass tuned for scientific prose

Consult [references/voice-and-variation.md](references/voice-and-variation.md).

Target common instruction-tuned LLM artefacts without turning the paper chatty:
- overuse of present-participial clause chains
- noun-heavy nominalized phrasing
- conveyor-belt transitions (`Additionally`, `Moreover`, `Importantly`, `Taken together`)
- inflated significance language
- generic concluding sentences that claim importance without stating the implication
- repeated weak sentence openings (`This`, `These`, `It`, `We`)
- flat sentence rhythm and uniform paragraph shape

Do **not** blindly ban passive voice, repetition, or technical compounds. Scientific prose needs all three sometimes. The aim is selective repair.

### 7. Run integrity and compliance checks

Use [references/integrity-and-compliance.md](references/integrity-and-compliance.md) and, if Python 3 is available:

```bash
python3 scripts/nature_preflight.py --input draft.md --mode nature-article --format text
```

or the relevant mode:

```bash
python3 scripts/nature_preflight.py --input draft.md --mode portfolio-article --format text
```

Use the report to fix:
- title length and title texture
- missing required or expected sections
- opening paragraph length or structure
- missing Data Availability or Code Availability sections
- bracket citations that need conversion
- figure legends missing title sentences or statistical detail
- hype words, generic AI-ish phrases, rhythm flatness, or repeated weak openers
- obvious overclaim or unsupported forward-looking claims

If scripting is unavailable, do the same checks manually.

## Section guidance

Use [references/section-rubric.md](references/section-rubric.md) for detailed section-by-section repair rules. High-level rules:

### Title
- clear, searchable, and readable outside the narrow subfield
- avoid hype, puns, slogans, rhetorical questions, and vague grandeur
- for main Nature, aim for roughly 75 characters and avoid numbers, acronyms, abbreviations, and punctuation unless essential

### Summary paragraph or abstract
- broad context first, then the specific gap
- state the main finding once, cleanly
- end on the most defensible implication
- use references in main Nature-style summary paragraphs when appropriate
- avoid stuffing it with data scraps, acronyms, or methodological clutter

### Introduction or opening
- move quickly from field context to unresolved problem
- do not write a mini-review
- finish with what the paper does, why the approach is appropriate, and what kind of answer the paper delivers

### Results
- organise by conceptual question or figure logic, not by when experiments happened
- make every subsection claim-bearing
- distinguish observation from interpretation
- mention only the numbers that advance the story

### Discussion
- say what the work establishes, what it suggests, and where it stops
- surface the main limitation before the reviewer does
- end with the most defensible field-level implication, not a cinematic future vision

### Methods
- concise but genuinely informative
- include the details that govern interpretability and reproducibility
- use short subsection headings and concrete labels

### Figure legends
- begin with a brief title sentence
- describe panels in sequence
- define statistics, sample sizes, centre values, and error bars where relevant
- stand on their own as far as reasonable

## Working modes

### A. Full manuscript from notes
Deliver:
- a short manuscript brief
- a figure-led blueprint
- the full draft in the chosen template
- an unresolved-gap list
- optional preflight and fingerprint reports

### B. Rewrite an existing draft
Process:
1. identify the actual claim
2. preserve data and meaning
3. repair structure
4. line-edit for Nature-style clarity and reader movement
5. flag claims that need verification

### C. Abstract or summary paragraph only
Where useful, provide 2-3 versions:
- conservative
- balanced or default
- slightly bolder but still defensible

Label the trade-off in claim strength.

### D. Reviewer response or rebuttal
Use [assets/reviewer-response-template.md](assets/reviewer-response-template.md).

Rules:
- answer every point directly
- quote the reviewer briefly, then answer
- specify exactly what changed and where
- concede valid points plainly
- when declining a request, explain why and offer the nearest rigorous alternative

### E. Presubmission enquiry or cover letter
Use:
- [assets/presubmission-enquiry-template.md](assets/presubmission-enquiry-template.md)
- [assets/cover-letter-template.md](assets/cover-letter-template.md)

Write for editors, not reviewers. Explain:
- the central advance
- why broad readers should care
- why the evidence is strong enough
- why the paper fits this journal
- what the paper is **not** claiming

## Output style

When returning a draft or rewrite:
- state the chosen journal mode and key assumptions
- give the manuscript in clean, journal-ready prose
- include a brief `Issues to confirm` list only when necessary
- do not pad the answer with generic writing advice unless the user asked for it

When returning diagnostics:
- prioritise the 5-10 issues that will most improve reader trust and editorial fit
- separate structural issues from line-edit issues
- suggest concrete rewrites, not vague criticism

## Fast heuristics for excellent Nature-style prose

- A clear limitation usually makes the paper sound stronger.
- If a phrase could appear in almost any paper, cut or replace it.
- The sentence ending matters. Land on the point that earns emphasis.
- Replace abstract importance language with the exact implication.
- Good scientific prose can be vivid without being promotional.
- Detail is welcome when it is the detail that lets the reader trust the claim.
- "Human sounding" here means precise, calm, varied, and specific, not casual.

## Bundled references

- [references/modes.md](references/modes.md)
- [references/section-rubric.md](references/section-rubric.md)
- [references/editorial-architecture.md](references/editorial-architecture.md)
- [references/sentence-craft.md](references/sentence-craft.md)
- [references/voice-and-variation.md](references/voice-and-variation.md)
- [references/journal-calibration.md](references/journal-calibration.md)
- [references/exemplar-anchoring.md](references/exemplar-anchoring.md)
- [references/integrity-and-compliance.md](references/integrity-and-compliance.md)
- [references/research-notes.md](references/research-notes.md)

## Bundled assets

- [assets/manuscript-brief-template.md](assets/manuscript-brief-template.md)
- [assets/editorial-blueprint-template.md](assets/editorial-blueprint-template.md)
- [assets/figure-claim-matrix-template.md](assets/figure-claim-matrix-template.md)
- [assets/paragraph-map-template.md](assets/paragraph-map-template.md)
- [assets/nature-article-template.md](assets/nature-article-template.md)
- [assets/nature-letter-template.md](assets/nature-letter-template.md)
- [assets/portfolio-article-template.md](assets/portfolio-article-template.md)
- [assets/portfolio-letter-template.md](assets/portfolio-letter-template.md)
- [assets/presubmission-enquiry-template.md](assets/presubmission-enquiry-template.md)
- [assets/cover-letter-template.md](assets/cover-letter-template.md)
- [assets/reviewer-response-template.md](assets/reviewer-response-template.md)
