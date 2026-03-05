---
name: parallel-ai-search
description: Search the live web and extract clean, LLM-ready excerpts/markdown from URLs (including PDFs and JS-heavy pages) using Parallel Search + Extract APIs. Use for up-to-date research, domain/date-scoped sourcing (include_domains/after_date), and turning specific URLs into citeable text.
compatibility: Requires Node.js 18+ (global fetch), network access to https://api.parallel.ai, and the PARALLEL_API_KEY environment variable.
metadata:
  author: "openclaw"
  version: "1.1.1"
  homepage: "https://docs.parallel.ai/search/search-quickstart"
  openclaw: "{\"emoji\":\"🔎\",\"primaryEnv\":\"PARALLEL_API_KEY\"}"
---

# Parallel AI Search

Use this skill to run web research through **Parallel Search** (ranked, LLM-optimised excerpts) and **Parallel Extract** (clean markdown from specific URLs, including JS-heavy pages and PDFs).

This skill follows the Agent Skills format: keep `SKILL.md` focused, and load extra details from `references/` as needed.

## When to use this skill

Use this skill when the user needs any of the following:

- **Up-to-date web research** (“look this up”, “find the latest”, “what changed recently”).
- **Source control** (“only use official docs”, “only these domains”, “after 2025-01-01”).
- **Readable extracts from URLs** (turn a URL/PDF into clean text/excerpts suitable for quoting/citing).
- **Repeatable research loops** (search → shortlist → extract → answer with citations).

## Preconditions

- `PARALLEL_API_KEY` must be available in the environment.
- Node.js 18+ is required (the scripts rely on the built-in `fetch`).

OpenClaw-specific setup notes are in `references/openclaw-config.md`.

## Available scripts

Run scripts using **relative paths from the skill root** (e.g. `node scripts/parallel-search.mjs ...`).

- **`scripts/parallel-search.mjs`** — Calls Parallel Search (`POST /v1beta/search`) to discover sources.
- **`scripts/parallel-extract.mjs`** — Calls Parallel Extract (`POST /v1beta/extract`) to extract clean excerpts/markdown from URLs.
- **`scripts/parallel-search-extract.mjs`** — Convenience pipeline: search then extract the top N results.

Tip: each script supports `--help`, `--dry-run`, and JSON output by default.

## Workflow (recommended)

### 1) Write an objective + queries

- Objective: 1–3 sentences describing the question, preferred source types, and any freshness constraints.
- Queries: 3–8 keyword queries including synonyms, version numbers, dates, or exact error strings.

If you’re unsure, use `references/prompting.md` templates.

### 2) Search (discover)

```bash
node scripts/parallel-search.mjs \
  --objective "Find official documentation explaining how X works. Prefer sources after 2025-01-01." \
  --query "X official documentation" \
  --query "X changelog 2025" \
  --max-results 8
```

Then inspect `results[].url`, `results[].title`, and `results[].publish_date` (if present) and pick the best sources.

### 3) Extract (read)

Extract only the URLs you actually need:

```bash
node scripts/parallel-extract.mjs \
  --url "https://example.com/docs/x" \
  --objective "How does X work? Include the most important constraints." \
  --excerpts \
  --no-full-content
```

Notes:
- Extract supports up to **10 URLs per request**; the script auto-batches if you pass more.
- Prefer `--excerpts` unless you truly need full content.

### 4) Answer (with citations)

- Prefer official/primary sources when possible.
- Quote/paraphrase only the extracted text you need.
- Include URL + publish date (when present) for transparency.
- If sources disagree, report both and explain why.

## High-signal recipes

### Recipe A: Domain-scoped research (official-only)

```bash
node scripts/parallel-search.mjs \
  --objective "Answer the question using official sources only." \
  --query "X authentication guide" \
  --include-domain "docs.vendor.com" \
  --include-domain "github.com" \
  --max-results 10
```

### Recipe B: Freshness constrained

```bash
node scripts/parallel-search.mjs \
  --objective "I need the latest info; prefer sources after 2026-01-01." \
  --query "X release notes" \
  --after-date "2026-01-01" \
  --fetch-max-age-seconds 3600
```

### Recipe C: One command (search → extract top 3)

```bash
node scripts/parallel-search-extract.mjs \
  --objective "Find the latest guidance on Y and extract citeable passages." \
  --query "Y documentation" \
  --query "Y 2026 update" \
  --max-results 8 \
  --top 3 \
  --excerpts
```

## Troubleshooting

### Missing API key / auth failures
- Symptom: errors mentioning missing `PARALLEL_API_KEY` or HTTP 401/403.
- Fix: set `PARALLEL_API_KEY` in the environment. For OpenClaw, see `references/openclaw-config.md`.

### No good results
- Add or refine queries (include synonyms, product names, dates, or exact error messages).
- Add `--include-domain` to constrain sources to known-good domains.
- Add/adjust `--after-date` or `--fetch-max-age-seconds` for freshness.

### Timeouts / slow pages during extract
- Use `--fetch-timeout-seconds` to raise the API-side crawl timeout.
- If you need fresh crawls, set `--fetch-max-age-seconds` (min 600 for extract).
- If cached content is acceptable, avoid `--disable-cache-fallback`.

### Helper files disappear after `npx skills add`
- Avoid underscore-prefixed bundled filenames like `scripts/_lib.mjs`.
- Some installers exclude paths whose basename starts with `_`; rename helpers to something like `scripts/lib.mjs` or `scripts/common.mjs`.
- Update any relative imports accordingly.

## References (load on demand)

- `references/parallel-api.md` — Compact field/shape reference for Search/Extract requests and responses.
- `references/prompting.md` — Objective + query templates and research patterns.
- `references/openclaw-config.md` — OpenClaw config + sandbox environment notes.
