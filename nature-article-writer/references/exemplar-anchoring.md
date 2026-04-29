# Exemplar anchoring

The best way to make a manuscript feel human and specific is often to anchor it to writing the user already owns or genuinely admires. Use exemplars carefully.

## Best exemplars

Prefer, in order:
1. the user's own accepted papers
2. lab or group style guides
3. internal documents the user authorises as tone anchors
4. recent papers from the target journal used only for calibration, not imitation

Avoid using a named outside author's paper as a phrasing model.

## What to learn from exemplars

Extract habits, not sentences:
- average sentence length and variation
- how often paragraphs begin with explicit signposts
- whether the prose tolerates long synthesis sentences
- how dense the technical detail is before explanation arrives
- how aggressively claims are hedged
- how titles are shaped
- whether conclusions end narrowly or expansively

## What not to copy

Do not transplant:
- distinctive metaphors
- signature turns of phrase
- unusual clause patterns repeated from the exemplar
- uncommon title formulas

The point is to align texture and discipline, not to ventriloquise another writer.

## Suggested workflow

1. Read the exemplar(s).
2. Build a short style card in plain language.
3. Draft the manuscript.
4. Compare draft and exemplars with:
   ```bash
   python3 scripts/prose_fingerprint.py --candidate draft.md --reference exemplar1.md exemplar2.md --format text
   ```
5. Revise only the dimensions that are clearly misaligned and matter for readability.

## When not to anchor heavily

Do not anchor too strongly when:
- the exemplar is from a different article type
- the exemplar is older and the journal has changed style
- the exemplar is exceptionally idiosyncratic
- the current paper needs more explanatory scaffolding than the exemplar did

## Productive framing

Good:
- "Match the restraint and sentence movement of these two accepted papers."

Less good:
- "Make this sound exactly like Author X."

## Useful style-card fields

- title texture
- opening strategy
- paragraph density
- mean sentence length
- sentence-length variation
- tolerance for explicit signposting
- main sources of emphasis
- common ending shapes
- hedge density
- acronym density
