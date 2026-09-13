# Journal-specific calibration

Treat the journal, content type, submission stage, and dated guide as the rule
identity. A sample paper shows editorial practice, not necessarily the current
submission limit. A publisher-wide style is not one shared schema.

## Reviewed opening profiles

Reviewed 2026-09-13 from official guide text surfaced in search:

| Profile | Opening | Length rule | Citation rule |
| --- | --- | --- | --- |
| Nature Communications / Article | Abstract | Maximum 200 words | No references |
| Nature / Article | Summary paragraph | Ideally no more than 200 words | Fully referenced |

Sources: [Nature Communications Article](https://www.nature.com/ncomms/submit/article)
and [Nature formatting guide](https://www.nature.com/nature/for-authors/formatting-guide).
Direct full-page retrieval was unavailable during this maintenance review; these
profiles encode the specific surfaced opening rules, not a review of every
requirement on either page. Recheck the actual guide for each submission. The
Nature recommendation is not promoted to a hard cutoff by the checker.

## Custom profile

For another verified journal/content type, supply a JSON object with exactly:

```json
{
  "journal": "Exact journal",
  "article_type": "Exact current content type",
  "opening_heading": "Abstract",
  "max_words": 200,
  "limit_kind": "mandatory",
  "citation_policy": "Copy the verified rule in your own words",
  "reviewed": "2026-09-13",
  "source_url": "https://example.org/official-guide"
}
```

This is a schema example, not a claim that the unnamed journal has a 200-word
limit. Replace every field with checked information. `limit_kind` is mandatory
or advisory. `citation_policy` is recorded, **not automatically validated**. The
checker does not fetch the URL or confirm the editor's authority; profile accuracy
is the reviewer's responsibility.

Use `--profile-file /absolute/profile.json`. For Markdown use an explicit ATX
heading matching `opening_heading`; for a separate prose file use `--opening-only`.
Extract Word/PDF/LaTeX using appropriate tools and inspect the resulting text
before counting. Mark unverified when the opening cannot be separated reliably.

## The rest of the manuscript

Check title, main-text counting exclusions, article type, display items, reference
style, section/end-matter order, ethics/reporting forms, availability statements,
figure files, and editorial correspondence against the actual guide. Distinguish
required items from recommendations and applicability conditions. Do not create
fictional declarations to fill missing headings.

Check [current AI policy](https://www.nature.com/nature-portfolio/editorial-policies/ai)
for the actual tool use and disclosure language. When the full policy is inaccessible,
report that limitation and obtain the current text before asserting an exemption.
