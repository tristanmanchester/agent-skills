# Approved API retrieval and evidence boundaries

Use the actual authorised connector/client and current endpoint documentation.
The API reference describes operations, not approval to call them. Keep OAuth
credentials in a secret store and identify the application with an honest user
agent. Do not paste tokens into chat, URLs, fixtures, or error logs. Restrict
credential-bearing calls to the documented Reddit OAuth API host and refuse
unreviewed redirects. A destination URL in a post is not a trusted API endpoint.

## Listing and thread routes

For an already approved API client, the documented read operations include
subreddit `/hot`, `/new`, `/top`, `/rising`, `/controversial`, `/search`, and
`/comments/{article}`. Check OAuth scope and exact route/parameter form in the
current [API reference](https://www.reddit.com/dev/api/), rather than attaching
.json to an arbitrary URL. Where recent-community-comment listing is exposed,
check its actual contract and permissions before using it.

Listings use `after`/`before` cursors and a `limit`, not fixed page numbers. Keep
returned cursors and deduplicate by fullnames (`t3_` posts, `t1_` comments).
Record the pages/request budget; a listing is a changing slice, not an atomic
snapshot. Do not treat a page count as the total number of matches. Inspect the
server's rate-limit headers and Retry-After; coordinate a request budget across
workers rather than using independent random sleeps as a rate-limit guarantee.

For thread retrieval preserve the original post and comment tree. `more` nodes
represent material not yet fetched. A supported morechildren read can expand a
selected branch within the budget; it does not require a posting scope. Do not
expand every branch reflexively. Missing expansion, depth or character truncation,
removed bodies, and inaccessible posts must remain visible in the result metadata.

A useful handoff shape is:

```json
{
  "source": "reddit",
  "retrieval_surface": "approved-api",
  "observed_at": "ISO timestamp",
  "query": "stated research question",
  "scope": {"communities": ["example"], "partial": true},
  "items": [
    {"id": "t3_EXAMPLE", "permalink": "verified original link",
     "relevance": "why it matches", "evidence": "short attributed excerpt",
     "body_truncated": true, "unexpanded_branches": true}
  ]
}
```

This is an illustrative report shape, not a provider response schema. Do not
invent dates, IDs, or booleans when the retrieval surface did not establish them.
Use null/unknown and explain the missing evidence.

## Privacy, retention, and errors

Keep only the content necessary for the task. Check current retention, deletion,
commercial-use, and research conditions for the approved integration; accessible
content is not a blanket licence for training, resale, or permanent archives.
Respect later removals and access changes in stored application data. Keep account
identity, browsing history, and private messages outside a public research report.

401/403 or HTML/login responses need access diagnosis, not a retry loop. A schema
or parse error is a failed retrieval, not an empty listing. Bounded retries for
actual transient read failures must still honour provider guidance and an overall
deadline. Do not silently change identity, scope, or query constraints to obtain
a result.

## Source baseline, reviewed 2026-09-13

- https://support.reddithelp.com/hc/en-us/articles/16160319875092-Reddit-Data-API-Wiki
- https://www.reddit.com/dev/api/
- https://redditinc.com/policies/data-api-terms
- https://redditinc.com/policies/developer-terms
- https://redditinc.com/news/modernizing-reddits-infrastructure-and-moderation-tools

Regression scenarios: access-denied HTML; a post with an available body but deleted
author; an unexpanded nested branch at the depth limit; a truncated quotation;
a duplicate across pages; a coarse date filter; a failed community fetch; and a
request to post/vote that must not run through this skill. These scenarios were
specified, not executed as live or model-output tests.
