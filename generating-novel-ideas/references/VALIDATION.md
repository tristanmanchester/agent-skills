# Validation and Trigger Tests

Use this file to maintain the skill over time.

## Should trigger

These prompts should strongly activate the skill:

- Help me brainstorm differentiated app ideas for tradespeople.
- This product concept is boring. Find genuinely fresher directions.
- I need novel research directions in battery diagnostics.
- Give me campaign territories for a new coffee brand.
- We need creative but commercially sensible membership ideas for a museum.
- Name this product, but first strengthen the concept.
- Find non-obvious service ideas for an imaging consultancy.
- Help us escape generic feature brainstorming for our SaaS roadmap.

## Should also trigger on paraphrases

- Come up with fresh options
- Ideate around this
- Push this into more original territory
- Break me out of generic answers
- Find stronger concept families
- What are some non-obvious angles here?

## Should not trigger

These prompts should usually not activate the skill:

- Proofread this email.
- Summarise this report.
- What is the capital of Peru?
- Give me the latest semiconductor news.
- Translate this paragraph into German.
- Write the code for this exact API spec.

Edge case:

- If the user asks to design options, explore alternatives, or invent stronger concepts
  before implementation, the skill should trigger even if code or documents are part of
  the eventual output.

## Quick quality checks

A healthy run should usually show:

- at least three distinct mechanism families in the raw set
- at least one far-analogy-derived concept when novelty matters
- at least one clear adoption wedge in the finalists
- one cheap test attached to every finalist
- a final portfolio with spread across risk and ambition

## Failure signals

The skill is underperforming if:

- the final ideas are polished but obviously similar
- every concept uses the same category cliché
- no idea has a believable first user and first context
- the final recommendation could have been produced by a generic brainstorming prompt
- the naming layer is doing all the work

## Manual regression suite

Run these tests after edits:

1. A blank-page startup prompt
2. A weak existing concept that needs improvement
3. A research idea prompt
4. A campaign or creative territory prompt
5. A process redesign prompt

For each run, check:

- Did the skill partition the search space?
- Did it delay judgement?
- Did it use at least one novelty lens and one practical lens?
- Did it criticise and repair finalists?
- Did it present a portfolio rather than near-duplicates?
