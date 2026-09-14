---
name: generating-novel-ideas
description: >-
  Develop differentiated ideas for products, research, campaigns, names, or process
  changes. Use when the user asks to brainstorm, explore alternatives, escape
  generic concepts, or test a promising direction. Compare mechanisms and practical
  constraints; do not claim originality without an appropriately scoped search.
  Do not activate for proofreading, factual lookup, or implementing an exact spec.
compatibility: No required external tools. Current market or technical claims need appropriate research. Optional lexical-overlap helper requires Python 3.10+ and no external packages.
metadata:
  version: "2.1.0"
  reviewed: "2026-09-13"
---

# Generate useful, differentiated ideas

Search for different mechanisms, not different names for one mechanism. Retain
analogy transfer, contradiction solving, diverse viewpoints, and critique-and-repair.
Scale the process to the request: a few names do not require a full product strategy,
and a single requested recommendation does not require a portfolio in the answer.

## Establish the opportunity

Use the supplied goal, audience, constraints, assets, and existing concept. State
important assumptions and resolve consequential gaps from available evidence. Do
not reopen an agreed product brief merely because naming or a small creative task
could be expanded into a bigger exercise.

Identify the real user job and tensions: for example, more control with less
attention, or more confidence with less data disclosure. Keep known technical,
legal, budget, and safety constraints visible from the start. Ideation is not a
reason to postpone a feasibility fact that already rules out an approach.

## Generate before converging

For a substantial task, use several search directions differing in mechanism,
user moment, adoption route, ownership, or ambition. Keep initial concepts short
and postpone cross-comparison until the first passes exist. Choose practical and
novelty-oriented lenses from [LENSES.md](references/LENSES.md) only where useful.

Different passes in the same conversation are **not independent blind samples**.
When genuinely isolated agent contexts are available and appropriate, provide each
with the same brief and distinct search direction without the other outputs.
Otherwise call the work separate perspectives/passes and do not invent agents,
independence, experiments, or unseen results.

Use distant analogies by transferring the mechanism, not the surface style. Explain
what must hold for that mechanism to work in the new domain. Resolve tensions
through sequencing, ownership, reversibility, or different allocations of work;
do not promise improvement on every dimension without a trade-off.

## Compare mechanisms, then repair

Group raw concepts by what actually causes the benefit. Identify disguised
duplicates and missing useful directions before polishing. Do not reject a
legitimate AI, marketplace, or subscription mechanism just because its label is
common; require a concrete role, advantage, and plausible route to adoption.

For promising candidates, state the strongest reason they could work, the most
consequential objection, and a repair. Drop candidates whose repair removes the
benefit or violates constraints. The [evaluation rubric](references/EVALUATION.md)
is a judgement aid, not a numerical proof of novelty or commercial success.

## Ground recommendations

Before making current market, technical, cultural, or regulatory claims, check
appropriate current sources. Identify the closest alternatives and explain the
actual difference. A limited search finding no match does not establish worldwide
novelty, patentability, name clearance, or freedom to operate. Report the search
scope and remaining uncertainty when originality matters.

For research ideas, separate established evidence from the proposed mechanism,
identify measurements and confounders, and specify a discriminating first experiment.
For products, make the first user/context and adoption assumptions explicit.
[Domain modes](references/MODES.md) adapt these checks without imposing one template.

Choose an ethical, low-cost test that could disconfirm the key assumption. Define
the observation and decision it would change. Interviews are not proof of buying
behaviour; a waitlist is not revenue. Fake-door or concierge tests need honest
expectations, appropriate consent, and no unauthorised charging or deceptive claims.

## Optional lexical check

Resolve `SKILL_DIR` to this installed directory:

```bash
python "$SKILL_DIR/scripts/diversity_audit.py" ideas.json
```

Input is a JSON array of strings or objects with `name` and `concept`/`description`,
or one idea per text line. The helper accepts at most 200 ideas, 2,000 characters
per field, and 1 MiB of input. It returns JSON with candidate token-overlap pairs
and `novelty: NOT_ASSESSED`; names do not inflate similarity. It does not infer
mechanism equivalence or decide which ideas to discard. Similar wording can mean
different mechanisms, and paraphrases can hide the same mechanism. The previous
permissive input coercions and mandatory regeneration prompts are removed.

## Deliver the useful result

Lead with the strongest concepts or recommendation in the requested format.
Include enough mechanism, intended benefit, practical entry point, main risk, and
next test for the user to evaluate them. For an exploratory portfolio, preserve
meaningful spread; do not force one safe, one medium, and one bold idea regardless
of quality. Show the raw search process only when it helps the requested deliverable.

Explain differentiation naturally. Do not force every concept into an identical
“This is not just X” sentence, nor invent a novel-sounding twist to satisfy a quota.
An honest outcome may be a narrower improvement, an unresolved hypothesis, or no
candidate yet meeting the constraints.

Maintainers: run `python -m unittest discover -s "$SKILL_DIR/tests" -v` for the
lexical helper. [Validation cases](references/VALIDATION.md) require separate agent
trace review; passing parser tests is not evidence that generated ideas improved.
The embedded distribution ZIP is removed from the source package; use Git history
for the prior artifact and package fresh releases outside the active skill directory.
