# Exa Search API — cheat sheet

This is a condensed reference for the Exa **Search** endpoint and the most-used request fields.

## Endpoint

- `POST https://api.exa.ai/search`

Auth:
- `x-api-key: <YOUR_KEY>` header (or `Authorization: Bearer <YOUR_KEY>`)

## Core request fields

Required:
- `query` (string): natural-language query; can be long and semantically rich.

Common:
- `type` (string): `auto` (default), `instant`, `deep`, `fast`, `neural`
- `category` (string): e.g. `news`, `research paper`, `company`, `people`, `tweet`, `personal site`, `financial report`, etc.
- `numResults` (int): 1–100 (default 10)

Deep search expansion:
- `additionalQueries` (string[]): only for `type: "deep"`.

Filters:
- `includeDomains` / `excludeDomains` (string[])
- `startCrawlDate` / `endCrawlDate` (ISO 8601 datetime)
- `startPublishedDate` / `endPublishedDate` (ISO 8601 datetime)
- `includeText` / `excludeText` (string[]): currently supports 1 phrase (up to ~5 words); `excludeText` checks early page text.
- `userLocation` (string): 2-letter ISO country code (e.g., `US`)

Safety:
- `moderation` (boolean): enable content moderation (if available on your plan).

### Category gotchas (important)

`company` and `people` categories support a limited set of filters. Using unsupported filters may return a 400 error.
In particular, some date/text filters and `excludeDomains` may be unsupported for these categories.

## Returning contents

You can request contents from results directly via `contents`:

```json
{
  "query": "…",
  "contents": {
    "highlights": true,
    "text": { "maxCharacters": 8000, "includeHtmlTags": false },
    "summary": { "query": "…optional steering prompt…" },
    "subpages": 0,
    "subpageTarget": "sources",
    "extras": { "links": 0, "imageLinks": 0 },
    "maxAgeHours": 24
  }
}
```

### Text
- `text: true` returns full text with defaults.
- `text: { maxCharacters, includeHtmlTags }` limits size and optionally preserves HTML tags.

### Highlights
Highlights are short excerpts selected to match your query. Depending on API version, the object form may support:
- `highlights: true` (defaults)
- `highlights: { numSentences, highlightsPerUrl, query }` (more control)

### Summary
Summaries can be steered with:
- `summary: { query: "What you want summarised/extracted" }`

### Freshness / live crawling
Use `maxAgeHours` to control cache vs live-crawl behaviour:
- `24` daily-fresh, `1` near-real-time, `0` always live-crawl, `-1` cache-only, omit for default fallback behaviour.

## Typical response fields

- `requestId`
- `results[]` including `title`, `url`, `publishedDate`, `author`, plus any requested `text` / `highlights` / `summary`
- `searchType` (for `auto`)
- `costDollars` (if enabled)

## When to split into 2 calls

For large or expensive workflows:
1) `POST /search` **without** `contents` to get URLs quickly.
2) `POST /contents` on the top N URLs to fetch only what you need.
