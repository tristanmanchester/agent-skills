---
name: nature-article-writer
description: >-
  Draft, revise, or critique a primary-research manuscript for a specifically
  chosen Nature or Nature Portfolio journal, or deliberately develop that
  broad-reader scientific style. Ground claims in the supplied results and
  calibrate journal requirements separately. Do not impose this journal style
  on generic documentation, reviews, press releases, or unrelated writing.
compatibility: File read/write access for drafts; Python 3.10+ for optional local checks. Current journal requirements need their official guide or a supplied dated copy. The checker accepts UTF-8 text/ATX Markdown, not PDF, Word, or LaTeX directly.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Evidence-led scientific writing

Make the scientific argument clear before polishing its language. Keep the
user's evidence, uncertainty, and voice; do not inflate novelty or make the work
sound more complete than it is. A journal-like style is not submission approval.

## Establish the brief and actual journal

Identify the journal and current content type, the central claim, its importance
to adjacent-field readers, the supporting results/figures, strongest relevant
prior work, boundary conditions, and missing facts. Use the supplied materials
rather than reconstructing unseen data from an abstract or README.

Check the official guide for that **journal and content type**. Record the rule,
source URL, review date, and whether it is mandatory or advisory. There is no
universal Nature Portfolio abstract limit. Do not assume a journal currently
accepts Letters because a bundled template has that name. For an unspecified
journal, draft without claiming journal-specific compliance.

Read [journal calibration](references/journal-calibration.md) and
[structural modes](references/modes.md). Use a few relevant recent papers to
understand structure and level of explanation, not to override an explicit
submission rule or copy distinctive wording.

## Build the argument, then write

Create a brief figure-to-claim map: each main claim, its evidence, alternative
explanations, and the figure/method needed to support it. Order Results by the
questions answered, not the chronology of experiments. Draft Methods while
checking what was actually done, then Discussion, context, abstract, title, and
legends. This is a useful default, not a compulsory ritual for a one-paragraph edit.

Retain and use the relevant templates:
[brief](assets/manuscript-brief-template.md),
[editorial blueprint](assets/editorial-blueprint-template.md),
[figure–claim matrix](assets/figure-claim-matrix-template.md), and
[paragraph map](assets/paragraph-map-template.md).
For deeper structure use [editorial architecture](references/editorial-architecture.md).

Give each paragraph a purpose, supporting evidence, and a useful conclusion or
transition. Connect familiar information to new findings; put the important point
where the reader expects emphasis. Use concrete verbs and explanations that an
adjacent-field scientist can follow. Keep necessary technical detail, exact units,
replicate definitions, analysis choices, and uncertainty.

## Edit without changing the evidence

Replace generic significance claims with the specific implication. Distinguish
observation, interpretation, and proposed mechanism. Do not turn association into
causation, technical repeats into independent samples, absent data into a null
result, or an exploratory analysis into a preregistered test.

Remove formulaic transitions, redundant conclusions, inflated adjectives, and
unnecessary noun chains. Vary rhythm naturally, not to hit a score. Passive voice,
repeated terms, and technical compounds can be the clearest choices.
A shorter
sentence is not automatically a better scientific sentence.

Use [sentence craft](references/sentence-craft.md),
[voice and variation](references/voice-and-variation.md), and
[section rubric](references/section-rubric.md) as editorial heuristics, not journal
rules. For supplied exemplars, use [exemplar anchoring](references/exemplar-anchoring.md).
Keep material limitations explicit without adding defensive filler to every claim.

## Check the selected opening, not an invented generic mode

Resolve `SKILL_DIR` to this skill's installed directory. The local checker now
requires an exact dated profile or a validated custom profile:

```bash
python3 "$SKILL_DIR/scripts/nature_preflight.py" --input /absolute/draft.md \
  --profile nature-communications-article
```

The built-in Nature Communications Article profile checks a 200-word maximum;
the Nature Article profile treats the 200-word summary target as advisory. For
a separate plain-text abstract/summary add `--opening-only`. Otherwise use exactly
one ATX heading matching the profile, such as `## Abstract`. The checker refuses
missing/duplicate/nested headings rather than guessing a first paragraph.

It counts whitespace-separated tokens; portal/word-processor conventions can
differ. It checks only opening length, not references, scientific validity,
article-type eligibility, or the rest of the manuscript. Every result says
`submission_readiness: NOT_ASSESSED`. Exit 0 means within the configured length;
1 means a mandatory length exceeded; 2 means advisory excess, unverified input,
or a tool/usage error. Inspect the JSON status. Old `--mode`/`--format` flags are
removed, not mapped to misleading generic defaults.

For other journals create `--profile-file` using the documented schema in
[journal calibration](references/journal-calibration.md) after checking the real
guide. Do not copy a built-in limit into another journal by changing only its name.

Optional prose metrics/fingerprint scripts remain editorial aids. Run their help
from `"$SKILL_DIR/scripts/..."`; they are not AI detectors or objective quality
scores, and their warnings do not establish publication-policy violations.

## Integrity and final deliverable

Never invent results, references, approvals, sample counts, software versions,
accessions, or completed analyses. Mark genuinely missing facts and verify source
citations against their actual content. Preserve original image/data evidence;
do not use generative imagery to fabricate observations. Check the journal's
current AI-use, disclosure, and image policy for the actual activity, rather than
assuming all copy editing is exempt or all computational plots are prohibited.
Human authors review and take responsibility for the manuscript.

Use [integrity checks](references/integrity-and-compliance.md). For reviewer replies,
answer each point, name the actual change and location, and distinguish completed
work from proposals. For a cover letter, explain the advance, evidence, and fit
without overclaiming; templates for both remain in `assets/`.

Return the revised prose/patch first, with the chosen target and only the important
unresolved facts. For an audit, prioritise concrete structural/scientific problems
before sentence preferences. State which journal checks actually ran and which
remain. Maintainer regression tests:
`python3 -m unittest discover -s "$SKILL_DIR/tests" -v`.
