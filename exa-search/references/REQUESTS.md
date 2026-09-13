# Request contracts

## Search versus Contents

REST search uses `POST https://api.exa.ai/search`, an `Authorization: Bearer` header,
and content controls nested under `contents`. For example:

```json
{
  "query": "published studies of X-ray tomography for corrosion",
  "type": "auto",
  "category": "publication",
  "numResults": 5,
  "contents": {"highlights": {"maxCharacters": 1500}}
}
```

For known source URLs, use the official SDK's `get_contents` or REST `/contents`.
The REST `/contents` request places content options at the **top level**, not under
`contents`. Keep URL arrays intact; comma-splitting a URL string can corrupt valid
URLs containing commas. Read the exact installed method signature before adding
SDK retrieval options. Check every returned URL/status; one successful fetch does
not mean the whole selection succeeded.

For extra page context request bounded `text`, rather than both full text and
multiple generated summaries for every result. In raw JSON use `maxCharacters`;
Python's typed content options use `max_characters`. Subpages/extras are deliberate
additional retrieval, not a default exhaustive crawl.

## Filters and freshness

Use `includeDomains`/`excludeDomains` for source policy, without repeating `site:`
operators in the query. Company/people categories do not accept all publication,
text, and domain-exclusion filters. Inspect the current category-specific contract
before sending; a 400 response is not permission to silently weaken constraints.

`contents.maxAgeHours` controls content fetching on Search: `0` requests a fresh
fetch; `-1` uses cache only; a positive value sets the acceptable cache age. The
Contents endpoint uses the option at top level. Python spells it `max_age_hours`.
A fetch failure may still leave incomplete/stale evidence depending on the selected
contract; inspect status rather than declaring a freshness guarantee.

Publication filters select publication dates, not event dates. For current events,
compare the source's actual publication/update timestamp with the event described.
For historical questions, do not apply a current crawl window as though it were a
historical publication filter.

## Highlights and synthesis

Use `highlights: true` or current highlight options such as `query`/`maxCharacters`.
Remove `numSentences` and `highlightsPerUrl`; adding 'if supported' does not make a
deprecated contract useful. Dynamic Highlights is an opt-in research preview,
requires its documented beta header in raw HTTP, and cannot be combined with
`maxCharacters`. Do not enable previews by default or assume a budget shape from
an older example; verify the installed SDK's handling before using them.

For structured search output, use `outputSchema` (Python `output_schema`) and read
`output.content` together with `output.grounding`. Validate the requested schema
against current depth/property limits and validate the returned object locally.
Do not ask the model to fabricate citation fields when the API already returns
grounding. Check cited passages, not just generated confidence.

A streaming Search request returns SSE (`text/event-stream`), not a single JSON
response. Use a supported streaming client/parser with a deadline and complete-event
handling. An interrupted stream is a partial result; do not JSON-decode arbitrary
chunks or claim final structured output before completion.

## Sources reviewed 2026-09-13

- [Current Search reference](https://exa.ai/docs/reference/search-api-guide-for-coding-agents)
- [Python SDK types](https://exa.ai/docs/sdks/python-sdk-specification)
- [Content freshness](https://exa.ai/docs/reference/livecrawling-contents)

For a new SDK version, re-check the specific method/type used and rerun a bounded
integration test. Do not claim live compatibility from this review date alone.
