#!/usr/bin/env python3
"""
exa_contents.py — small CLI for Exa Contents API (POST /contents)

- No third-party deps (uses urllib).
- Reads API key from EXA_API_KEY by default.
- Prints JSON to stdout.

Examples:
  python scripts/exa_contents.py --urls https://example.com,https://example.org --text --text-max-chars 3000
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


EXA_API_URL = "https://api.exa.ai/contents"


def _split_csv(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    items = [v.strip() for v in value.split(",") if v.strip()]
    return items or None


def exa_contents(api_key: str, payload: Dict[str, Any], timeout_s: int = 60) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        EXA_API_URL,
        method="POST",
        data=data,
        headers={
            "content-type": "application/json",
            "accept": "application/json",
            "x-api-key": api_key,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} from Exa: {body}") from e
    except urllib.error.URLError as e:
        raise RuntimeError(f"Network error calling Exa: {e}") from e


def main() -> int:
    p = argparse.ArgumentParser(description="Call Exa Contents API and print JSON.")
    p.add_argument("--urls", help="Comma-separated URLs to fetch contents for")
    p.add_argument("--ids", help="Comma-separated document IDs from Exa search results (legacy)")
    p.add_argument("--text", action="store_true", help="Request full text")
    p.add_argument("--text-max-chars", type=int, help="Cap returned text size")
    p.add_argument("--include-html-tags", action="store_true", help="Include HTML tags in returned text")

    p.add_argument("--highlights", action="store_true", help="Request highlights")
    p.add_argument("--highlights-query", help="Steer highlights with a custom query")
    p.add_argument("--highlights-per-url", type=int, help="Snippets per URL")
    p.add_argument("--num-sentences", type=int, help="Sentences per snippet")

    p.add_argument("--summary", action="store_true", help="Request summaries")
    p.add_argument("--summary-query", help="Steer summaries with a custom query")

    p.add_argument("--subpages", type=int, help="Number of subpages to crawl")
    p.add_argument("--subpage-target", help="Keyword(s) to target subpages; comma-separated for multiple")
    p.add_argument("--extras-links", type=int, help="Number of links to return per page")
    p.add_argument("--extras-image-links", type=int, help="Number of image links to return per page")
    p.add_argument("--max-age-hours", type=int, help="Freshness policy for cached content")

    p.add_argument("--api-key", help="Exa API key (otherwise uses EXA_API_KEY env var)")
    p.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds (default: 60)")
    p.add_argument("--compact", action="store_true", help="Compact JSON output (no pretty-print)")

    args = p.parse_args()

    api_key = args.api_key or os.environ.get("EXA_API_KEY")
    if not api_key:
        print("Missing API key. Set EXA_API_KEY or pass --api-key.", file=sys.stderr)
        return 2

    urls = _split_csv(args.urls)
    ids = _split_csv(args.ids)
    if not urls and not ids:
        print("Provide --urls or --ids.", file=sys.stderr)
        return 2

    payload: Dict[str, Any] = {}
    if urls:
        payload["urls"] = urls
    if ids:
        payload["ids"] = ids

    if args.text:
        if args.text_max_chars is None and not args.include_html_tags:
            payload["text"] = True
        else:
            payload["text"] = {
                "maxCharacters": args.text_max_chars if args.text_max_chars is not None else 10000,
                "includeHtmlTags": bool(args.include_html_tags),
            }

    if args.highlights:
        hl: Dict[str, Any] = {}
        if args.highlights_query:
            hl["query"] = args.highlights_query
        if args.num_sentences is not None:
            hl["numSentences"] = args.num_sentences
        if args.highlights_per_url is not None:
            hl["highlightsPerUrl"] = args.highlights_per_url
        payload["highlights"] = hl if hl else True

    if args.summary:
        payload["summary"] = {"query": args.summary_query} if args.summary_query else True

    if args.subpages is not None:
        payload["subpages"] = args.subpages

    if args.subpage_target is not None:
        target = _split_csv(args.subpage_target)
        payload["subpageTarget"] = target if (target and len(target) > 1) else (target[0] if target else args.subpage_target)

    extras: Dict[str, Any] = {}
    if args.extras_links is not None:
        extras["links"] = args.extras_links
    if args.extras_image_links is not None:
        extras["imageLinks"] = args.extras_image_links
    if extras:
        payload["extras"] = extras

    if args.max_age_hours is not None:
        payload["maxAgeHours"] = args.max_age_hours

    try:
        res = exa_contents(api_key=api_key, payload=payload, timeout_s=args.timeout)
    except Exception as e:
        print(str(e), file=sys.stderr)
        return 1

    if args.compact:
        print(json.dumps(res, ensure_ascii=False))
    else:
        print(json.dumps(res, ensure_ascii=False, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
