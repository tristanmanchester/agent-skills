# Exa Search — best-practice recipes

## Pick the right search type

- `auto`: best general quality.
- `instant`: low latency, great for autocomplete and quick suggestions.
- `deep`: comprehensive research; can use query expansion.
- `fast` / `neural`: lightweight alternatives.

## Token efficiency: prefer highlights

For multi-step agent workflows, request **highlights** first and only fetch full **text** when necessary.

A common pattern:
1) `contents.highlights` on 10 results.
2) If needed, `contents.text` on the best 3 results (cap with `maxCharacters`).

## Control verbosity when using full text

When requesting `text`, use:
- `maxCharacters` to cap size
- (if supported) `verbosity` to include/exclude boilerplate like navigation, footers, etc.

## Freshness: be explicit when “latest” matters

Use `maxAgeHours` to control cache vs live crawling:

- `24`: cache if <24h old, otherwise live-crawl
- `1`: cache if <1h old, otherwise live-crawl
- `0`: always live-crawl
- `-1`: cache only
- omit: default fallback behaviour

## Category filters

Use `category` to target sources:
- `news`, `research paper`, `personal site`, `financial report`, `tweet`, plus entity-focused categories like `company` and `people`.

When using `company`/`people`, keep filters minimal to avoid unsupported-parameter errors.
