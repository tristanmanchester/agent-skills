---
name: display-quantitative-information
description: >-
  Design, critique, or implement quantitative graphics, scientific figures,
  dashboards, and evidence tables. Use for display choice, scale/encoding integrity,
  uncertainty, and accessible chart handoff. Do not use for decorative illustration
  or general data cleaning without a quantitative display.
license: Proprietary
compatibility: Bundled helpers require Python 3.10+ and use the standard library. The SVG renderer is a first-pass tool, not a full plotting or accessibility-validation system.
metadata:
  version: "2.1.0"
  reviewed: "2026-09-13"
  source-note: "Tufte-informed methods adapted from previously supplied study material; source book text and images are not bundled. No missing licence terms have been reconstructed."
---

# Display quantitative information

Help the viewer reason from evidence. Prioritise truthful encoding and useful
comparisons over cosmetic minimalism. Preserve the package's Tufte-informed
methods without turning data-ink or any other maxim into an automatic verdict.

## Work from the analytical task

1. Identify the comparison or decision: lookup, trend, relationship, distribution,
   composition, geography, uncertainty, or monitoring.
2. Inspect grain, units, denominator, groups, missingness, time spacing, transformations,
   sample size, and uncertainty before plotting. Separate observations from summaries.
3. Choose a display for that task using [display selection](references/display-selection.md)
   when needed. Establish intentional aggregation and ordering explicitly.
4. Audit scales and encodings before aesthetics. Check actual data bounds, baseline,
   transformations, temporal spacing, omitted values, and uncertainty against source data.
5. Deliver the requested chart, code, specification, or critique. Verify the output
   itself rather than assuming a successful plotting command preserved its meaning.

For a critique, lead with a demonstrated integrity or comparison problem. A sound
chart may need no change; do not manufacture an improvement to satisfy a template.
For scientific work, retain conditions, uncertainty, calibration, and raw observations
where they affect interpretation. For dashboards, align time windows and denominators
with the actual decision, not decorative KPI symmetry.

## Use helpers deliberately

Resolve `SKILL_DIR` to this installed directory. Bundled scripts do not live in the
target project's `scripts/` directory. Read a helper's help before invoking it.
The spec audit, display suggestions, lie-factor calculation, and text-fingerprint
checks are heuristics or scoped calculations, not a substitute for inspecting data
and the rendered graphic. A repetition score does not establish poor writing or
AI authorship. Preserve clear consistent terminology instead of varying it randomly.

```bash
python "$SKILL_DIR/scripts/suggest_display.py" --csv data.csv --goal auto --format markdown
python "$SKILL_DIR/scripts/audit_visual_display.py" --spec chart.json --format markdown
python "$SKILL_DIR/scripts/render_chart_svg.py" --csv observations.csv \
  --x date --y defect_rate --chart line --x-type date --output new-chart.svg
```

### SVG renderer contract

Choose `bar`, `dot`, `line`, or `scatter` explicitly. The renderer does not guess a
chart type or silently average duplicate observations. It reads at most 10,000 rows
from a CSV of at most 16 MiB. New output paths are required; no output overwrite.

- Scatter plots retain all observations and compute both axis limits from those
  observations, not group means.
- Lines use numeric x values, or `--x-type date` for unambiguous `YYYY-MM-DD` dates,
  with proportional spacing. A blank y value breaks the path; omitted rows cannot
  establish an unrecorded missing interval. Duplicate x values within a line series
  are rejected until the caller selects an appropriate aggregation/representation.
- Bars require unique category/group pairs and include zero. Zero values have zero
  bar height. Dots retain observations; both preserve category encounter order.
- Missing/non-finite/ambiguous numeric values are rejected outside the explicitly
  supported line-gap case. Locale numbers need deliberate normalisation first.

Optional `--group`, `--title`, `--metadata`, `--width`, and `--height` configure the
first-pass output. Metadata records input/point counts, domains, gaps, and lack of
aggregation. SVG title/description and distinct markers help, but do not certify
accessibility. Inspect crowded labels, overplotting, group identification, contrast,
and the source/uncertainty annotations needed for the deliverable. Use a full
plotting library for intervals, complex dates, dense categories, or publication layout.
SVG and optional metadata are separate writes, not an atomic two-file transaction.

## References and assets

Load only the relevant material:
[principles](references/principles.md), [integrity](references/integrity-audit.md),
[redesign](references/redesign-workflow.md), [specification](references/chart-spec.md),
[accessibility](references/accessibility-and-output.md), [examples](references/examples.md),
and [review rubric](references/rubric.md). Rubric scores organise judgement; they
are not empirical accuracy measures. The language/fingerprint material is a review
prompt, not an instruction to distort a good existing voice.

Keep the existing chart-spec, critique-note, and handoff templates as optional
scaffolds. Preserve units, sources, denominators, uncertainty, and exact numerical
meaning through revisions. A cleaner misleading chart is still misleading.

## Maintenance

Run `python -m unittest discover -s "$SKILL_DIR/tests" -v` for the renderer
regressions. These test numerical geometry and output handling, not human readability,
all retained helpers, or a complete accessibility audit. The existing proprietary
licence declaration is retained without a dangling LICENSE.txt link; no new
redistribution permission or unavailable historical licence text is invented.
