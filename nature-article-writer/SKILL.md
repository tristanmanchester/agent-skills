---
name: nature-article-writer
description: Drafts, rewrites, and critiques primary research manuscripts in the style expected by Nature and Nature Portfolio journals while keeping the prose natural, precise, and human-sounding. Use when the user wants a Nature-style title, summary paragraph or abstract, introduction, results, discussion, methods, figure legends, presubmission enquiry, cover letter, reviewer response, or line edit for a scientific manuscript, or when converting notes or an existing draft into submission-ready journal prose without inventing data or references.
compatibility: Best in skills-compatible agents with file read/write access. Optional Python 3 enables scripts/nature_preflight.py. If web access is available, verify the live author guide for the named journal before finalising limits or section order.
metadata:
  author: OpenAI
  version: "1.0.0"
  updated: "2026-04-19"
  target: Nature and Nature Portfolio primary research
---

# Nature Article Writer

Write and revise primary research manuscripts so they read like careful, expert scientific prose rather than templated AI output. Aim for clarity, intellectual honesty, strong logical flow, and accessibility to scientists outside the narrow subfield.

Do not imitate a named author. Emulate journal expectations, not a person.

## When to activate this skill

Use this skill when the user:
- names Nature or a Nature Portfolio journal
- asks for "Nature-style" or "Nature journal" writing
- wants a title, summary paragraph, abstract, introduction, results, discussion, methods, figure legend, presubmission package, cover letter, or reviewer response
- wants scientific prose to sound more natural, less generic, or less obviously AI-written
- wants to convert notes, figures, or a rough draft into a submission-ready research manuscript

## Non-negotiables

- Never invent data, methods, figures, ethics approvals, accession numbers, references, software versions, or statistical results.
- Never promote a weak result with stronger language than the evidence supports.
- Never hide uncertainty. If key facts are missing, mark them explicitly with `[confirm]`, `[insert ref]`, `[insert accession]`, or a short `Issues to confirm` list.
- Never use AI-generated figures or image content for publication.
- Do not copy wording from published papers unless the user explicitly asks for quoted comparison and attribution is clear.
- If AI did more than copy editing, remind the user to check whether disclosure is required under the target journal’s policy. AI-assisted copy editing for readability and style does not currently need declaration under Nature’s policy, but human authors remain accountable for the final text.

## Default workflow

### 1. Establish the manuscript brief

Before drafting, infer or collect the following:
- target journal and content type
- one-sentence central claim
- why it matters outside the immediate subfield
- the evidence ladder: 3-6 concrete results or figures that support the central claim
- strongest prior work and the precise gap
- strongest limitation or boundary condition
- data, code, and materials availability
- ethics or compliance facts if humans, animals, clinical samples, or sensitive data are involved

If information is missing, proceed with stated assumptions and place unknowns in a short `Manuscript brief` or `Issues to confirm` block rather than stalling.

Use [assets/manuscript-brief-template.md](assets/manuscript-brief-template.md) if the user provides scattered notes rather than a manuscript-ready brief.

### 2. Choose the closest mode

Use [references/modes.md](references/modes.md) and the templates in [assets](assets/nature-article-template.md) to select the closest mode:

- `nature-article` — main Nature Article with a referenced summary paragraph
- `nature-letter` — Nature or Nature-style Letter with a referenced introductory paragraph and no main-text headings
- `portfolio-article` — common Nature Portfolio research article with an unreferenced abstract plus Introduction, Results, Discussion and Methods
- `portfolio-letter` — common Nature Portfolio Letter with a referenced introductory paragraph and concise main text

If the user names a specific journal and web access is available, check the live author guide before finalising word counts or mandatory sections. If web access is unavailable, use the closest bundled mode and say that the exact limits should be checked against the current journal guide.

### 3. Build the claim ladder before writing

Create, even if only mentally, this hierarchy:

1. title claim
2. summary paragraph or abstract claim
3. section claims
4. figure-level claims
5. sentence-level evidence

Nothing lower in the ladder may contradict or exceed the level above it. Discussion may extend meaning, but not the core evidence.

### 4. Outline by question and answer, not chronology

Results sections should usually follow this pattern:
- question or obstacle
- experiment or analysis used to address it
- direct finding
- what that finding permits you to claim next

Organise by figures or conceptual steps, not by the order experiments happened in the lab.

### 5. Draft sections in this order

1. figure plan and one-sentence take-home message for each figure
2. Results
3. Methods
4. Discussion or concluding synthesis
5. opening context paragraph or Introduction
6. summary paragraph or abstract
7. title
8. figure legends
9. data or code availability and end matter
10. cover letter or presubmission paragraph if requested

This order produces more grounded prose than starting with the title or abstract.

## Section guidance

For detailed rubrics, consult [references/section-rubric.md](references/section-rubric.md).

### Title

- precise, searchable, readable outside the subfield
- avoid hype, puns, slogans, rhetorical questions, and vague claims
- for main Nature, aim for about 75 characters and avoid numbers, acronyms, abbreviations or punctuation unless essential
- include the key entity, process, or system when discoverability depends on it

### Summary paragraph or abstract

- open with 1-3 sentences of broad context
- define the precise gap
- introduce the principal conclusion with `Here we show` or an equivalent phrase only once
- close with the immediate implication, not a grand future vision
- for main Nature Article: referenced, ideally 200 words or fewer, aimed at non-specialists, and avoid abbreviations and numbers unless essential
- for many Nature Portfolio journals: unreferenced 100-150 or 200 words depending on the journal, with context, rationale, main conclusion, and implication

### Introduction or opening

- do not write a mini-review
- make the reader care quickly
- move from big picture to specific unresolved problem
- finish with what the paper does, in present tense if summarising the paper’s findings
- for portfolio articles, the final Introduction paragraph can summarise the major results and conclusion
- for main Nature Article, the summary paragraph already carries much of the broad framing, so the main text should move briskly into the gap and study logic

### Results

- every subsection needs a claim, not just a topic
- start with the cleanest, most load-bearing result
- use subheadings that are informative but restrained
- distinguish observation from interpretation
- tell the reader why each figure exists
- do not repeat every number from the figure in prose; mention only what advances the argument

### Discussion

- separate what the data establish from what they suggest
- include the main limitation or competing explanation before the reviewer does
- explain scope: where the result should generalise and where it may not
- end with the most defensible field-level implication, not the broadest imaginable one

### Methods

- concise but complete enough for interpretation and replication
- use short bold subsection headings
- include statistics, sample definitions, preprocessing, inclusion or exclusion rules, randomisation or blinding if relevant, and software versions when material
- do not park essential interpretation details only in the supplement if the main claim depends on them

### Figure legends

- begin with a brief title sentence
- describe panels in sequence
- define symbols, centre values, error bars, sample size `n`, statistical tests, and P values where relevant
- keep methodological detail to a minimum if there is a Methods section
- each legend should stand on its own as far as reasonably possible

### End matter

Include, when relevant:
- Data Availability
- Code Availability
- Acknowledgements
- Funding Statement
- Author Contributions
- Competing Interests
- Additional Information or Correspondence
- Extended Data legends

Use placeholders rather than fabricating missing facts.

## Human-sounding scientific prose rules

Use [references/human-voice.md](references/human-voice.md) for detailed patterns.

Core rules:
- Prefer active voice when it makes agency clearer.
- Use concrete verbs: `measured`, `trained`, `compared`, `found`, `estimated`, `tested`.
- Keep sentences simply built; unpack dense noun clusters.
- Minimise acronyms. Define the unavoidable ones once.
- Cut filler transitions: `Additionally`, `Moreover`, `Importantly`, `Taken together`, `Overall`, `It is worth noting that`.
- Avoid inflated claims: `novel`, `groundbreaking`, `paradigm-shifting`, `unprecedented`, `remarkable`, `game-changing`.
- Avoid generic AI abstractions: `landscape`, `interplay`, `underscores`, `highlights the importance of`, `plays a crucial role`, `fosters`, `leverages`, `tapestry`.
- Avoid formulaic contrast frames: `not only...but also`, `not X but Y`, `this is not merely`.
- Avoid performative emphasis and em-dash overuse.
- Prefer specific nouns over empty demonstratives: replace `this approach` with the actual method when repetition will not confuse.
- Use hedge words deliberately and proportionally: `suggest`, `are consistent with`, `may`, `likely` only when the evidence requires them.
- Vary rhythm modestly. Human scientific prose does not need faux-literary flourishes.

## Claim calibration

Match verbs to evidence:
- `show` or `demonstrate`: direct support from the study
- `find` or `observe`: descriptive result
- `suggest` or `indicate`: plausible but not definitive inference
- `are consistent with`: supportive but indirect
- `establish`: reserve for very strong, convergent evidence

Never use stronger verbs in the title or abstract than the data justify.

## Anti-slop revision pass

After drafting, do three passes:

1. `Structure pass` — can a non-specialist scientist follow the logic?
2. `Evidence pass` — does each claim point to data, analysis, or citation?
3. `Voice pass` — remove AI tells without flattening the prose

During the voice pass, aggressively cut:
- vague declarations of importance
- filler throat-clearing
- repeated sentence openings
- generic signposting
- adjectives doing the work of evidence
- summaries of what the paper "seeks to" do when the paper already did it

Useful replacements:
- replace `These findings highlight the critical role of X` with the exact implication
- replace `In the broader context` with the specific broader context
- replace `Taken together` with a sentence that directly states the integrated conclusion

## Working modes

### A. Full manuscript from notes

Deliver:
- a short manuscript brief
- a figure-led outline
- the full draft in the chosen template
- an unresolved gap list
- an optional preflight report

### B. Rewrite an existing draft

Process:
1. identify the paper’s actual claim
2. preserve data and meaning
3. repair structure
4. line-edit for Nature-style clarity and natural voice
5. list any claims that need verification

### C. Abstract or summary paragraph only

Provide 2-3 versions if useful:
- conservative
- balanced or default
- slightly bolder but still defensible

Label the trade-off in claim strength.

### D. Reviewer response or rebuttal

Use [assets/reviewer-response-template.md](assets/reviewer-response-template.md).

Rules:
- answer every point specifically
- separate gratitude from substance
- quote the reviewer briefly, then answer
- specify exactly what changed and where
- do not sound combative or obsequious
- concede when the reviewer is right
- when declining a request, explain why and offer the nearest rigorous alternative

### E. Presubmission enquiry or cover letter

Write for editors, not reviewers.

Include:
- the central advance
- why broad readers should care
- why the evidence is strong
- why the work fits the named journal
- what the paper is not claiming

## Scripted preflight

If Python 3 is available and there is a draft file, run:

```bash
python3 scripts/nature_preflight.py --input draft.md --mode nature-article --format text
```

or the appropriate mode:

```bash
python3 scripts/nature_preflight.py --input draft.md --mode portfolio-article --format text
```

Use the report to fix:
- title length
- missing mandatory sections
- summary paragraph or abstract length
- hype words and AI-tell phrases
- em-dash overuse
- bracket citations that should be converted
- missing data or code availability statements
- missing figure statistics details

If scripting is unavailable, perform the same checks manually using [references/integrity-and-compliance.md](references/integrity-and-compliance.md) and [references/section-rubric.md](references/section-rubric.md).

## Output style

When returning a draft or rewrite:
- state the chosen journal mode and any important assumptions
- give the manuscript itself in clean journal-ready prose
- end with a short `Issues to confirm` list only if necessary

Do not pad the answer with writing advice unless the user asked for it.

## Fast heuristics for good Nature-style prose

- one crisp sentence is better than three inflated ones
- a clear limitation makes the paper sound more, not less, credible
- results should feel inevitable in hindsight, not theatrically revealed
- if a phrase sounds like it could appear in any paper, cut or replace it
- if the only thing making a claim sound important is the adjective, the claim is probably weak
- if the user wants "human sounding", make the prose precise, calm, and specific, not chatty

## Bundled references

- [references/modes.md](references/modes.md) — journal and content-type selection
- [references/section-rubric.md](references/section-rubric.md) — section-by-section guidance
- [references/human-voice.md](references/human-voice.md) — anti-slop, human-sounding scientific prose
- [references/integrity-and-compliance.md](references/integrity-and-compliance.md) — policies, availability statements, reporting expectations
- [references/sources.md](references/sources.md) — curated official source notes

## Bundled assets

- [assets/manuscript-brief-template.md](assets/manuscript-brief-template.md)
- [assets/nature-article-template.md](assets/nature-article-template.md)
- [assets/nature-letter-template.md](assets/nature-letter-template.md)
- [assets/portfolio-article-template.md](assets/portfolio-article-template.md)
- [assets/reviewer-response-template.md](assets/reviewer-response-template.md)

## Authsome (optional)

Optional: [authsome](https://github.com/manojbajaj95/authsome) with the authsome skill handles credential injection for agent runs; you do not need to manually export the API keys, tokens, or other secrets this skill already documents for your app, on that path, for example.

