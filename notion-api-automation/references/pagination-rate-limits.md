# Pagination + rate limits (patterns that don't break)

## Pagination (Notion style)
Most “list/query/search” endpoints return:
- `results` (array)
- `has_more` (boolean)
- `next_cursor` (string|null)

To paginate:
- send `page_size` (typically up to 100)
- send `start_cursor` = previous `next_cursor`

### JS/TS loop (raw)
```js
let cursor = undefined
const all = []

do {
  const resp = await notion.dataSources.query({
    data_source_id,
    start_cursor: cursor,
    page_size: 100,
    // filter/sorts optional
  })
  all.push(...resp.results)
  cursor = resp.next_cursor ?? undefined
} while (cursor)
```

## Rate limits
- Throttle writes; use sequential or a strict concurrency limit.
- On HTTP 429:
  - read `Retry-After` seconds and sleep
  - retry the same request
- Also retry transient 5xx with exponential backoff.

### Backoff pseudocode
- For attempt in 1..N:
  - call API
  - if 429: sleep Retry-After
  - else if 5xx: sleep 2^attempt + jitter
  - else: return
