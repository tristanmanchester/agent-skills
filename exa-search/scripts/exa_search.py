#!/usr/bin/env python3
"""
exa_search.py — small CLI for Exa Search API (POST /search)

- No third-party deps (uses urllib).
- Reads API key from EXA_API_KEY by default.
- Prints JSON to stdout.

Examples:
  python scripts/exa_search.py --query "latest research in LLMs" --highlights --num-results 5
  python scripts/exa_search.py --query "latest announcements from OpenAI" --include-domains openai.com --text --max-age-hours 24
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


EXA_API_URL = "https://api.exa.ai/search"


def _split_csv(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    items = [v.strip() for v in value.split(",") if v.strip()]
    return items or None


def _maybe_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    return int(value)


def _build_contents(args: argparse.Namespace) -> Optional[Dict[str, Any]]:
    want_any = (
        args.highlights
        or args.text
        or args.summary
        or args.subpages is not None
        or args.subpage_target is not None
        or args.extras_links is not None
        or args.extras_image_links is not None
        or args.max_age_hours is not None
    )
    if not want_any:
        return None

    contents: Dict[str, Any] = {}

    if args.highlights:
        # Some API versions support object options. Keep it flexible.
        hl_obj: Dict[str, Any] = {}
        if args.highlights_query:
            hl_obj["query"] = args.highlights_query
        if args.num_sentences is not None:
            hl_obj["numSentences"] = args.num_sentences
        if args.highlights_per_url is not None:
            hl_obj["highlightsPerUrl"] = args.highlights_per_url
        if args.highlights_max_chars is not None:
            hl_obj["maxCharacters"] = args.highlights_max_chars

        contents["highlights"] = hl_obj if hl_obj else True

    if args.text:
        if args.text_max_chars is None and not args.include_html_tags and args.text_verbosity is None:
            contents["text"] = True
        else:
            txt_obj: Dict[str, Any] = {}
            if args.text_max_chars is not None:
                txt_obj["maxCharacters"] = args.text_max_chars
            if args.include_html_tags:
                txt_obj["includeHtmlTags"] = True
            if args.text_verbosity is not None:
                txt_obj["verbosity"] = args.text_verbosity
            contents["text"] = txt_obj

    if args.summary:
        if args.summary_query is None:
            contents["summary"] = True
        else:
            contents["summary"] = {"query": args.summary_query}

    if args.subpages is not None:
        contents["subpages"] = args.subpages

    if args.subpage_target is not None:
        target = _split_csv(args.subpage_target)
        contents["subpageTarget"] = target if (target and len(target) > 1) else (target[0] if target else args.subpage_target)

    extras: Dict[str, Any] = {}
    if args.extras_links is not None:
        extras["links"] = args.extras_links
    if args.extras_image_links is not None:
        extras["imageLinks"] = args.extras_image_links
    if extras:
        contents["extras"] = extras

    if args.max_age_hours is not None:
        contents["maxAgeHours"] = args.max_age_hours

    return contents


def _validate(args: argparse.Namespace, payload: Dict[str, Any]) -> None:
    if args.type != "deep" and args.additional_queries:
        raise SystemExit("--additional-queries only works with --type deep")

    category = payload.get("category")
    if category in {"company", "people"}:
        # From Exa docs: these categories support a limited subset of filters.
        forbidden = []
        for k in (
            "startPublishedDate",
            "endPublishedDate",
            "startCrawlDate",
            "endCrawlDate",
            "includeText",
            "excludeText",
            "excludeDomains",
        ):
            if k in payload:
                forbidden.append(k)

        if forbidden:
            raise SystemExit(
                f"Category '{category}' does not support these filters: {', '.join(forbidden)}. "
                f"Remove them or change category."
            )

        if category == "people" and "includeDomains" in payload:
            # People category may limit includeDomains to LinkedIn.
            # We don't enforce the exact domain here, but we warn.
            domains = payload.get("includeDomains") or []
            if any("linkedin.com" not in d for d in domains):
                print(
                    "Warning: category 'people' may only support LinkedIn domains for includeDomains. "
                    "If you get a 400, restrict includeDomains to linkedin.com.",
                    file=sys.stderr,
                )


def exa_search(api_key: str, payload: Dict[str, Any], timeout_s: int = 60) -> Dict[str, Any]:
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
    p = argparse.ArgumentParser(description="Call Exa Search API and print JSON.")
    p.add_argument("--query", required=True, help="Search query string")
    p.add_argument("--type", default="auto", choices=["auto", "instant", "deep", "fast", "neural"], help="Search type")
    p.add_argument("--category", help="Category filter, e.g. news, research paper, company, people")
    p.add_argument("--num-results", type=int, default=10, dest="num_results", help="Number of results (1-100)")
    p.add_argument("--include-domains", help="Comma-separated domains to include, e.g. arxiv.org,paperswithcode.com")
    p.add_argument("--exclude-domains", help="Comma-separated domains to exclude")
    p.add_argument("--start-crawl-date", help="ISO 8601 datetime (e.g. 2023-01-01T00:00:00.000Z)")
    p.add_argument("--end-crawl-date", help="ISO 8601 datetime")
    p.add_argument("--start-published-date", help="ISO 8601 datetime")
    p.add_argument("--end-published-date", help="ISO 8601 datetime")
    p.add_argument("--include-text", help="Phrase that must appear in page text (use sparingly)")
    p.add_argument("--exclude-text", help="Phrase that must NOT appear in page text (use sparingly)")
    p.add_argument("--user-location", help="Two-letter ISO country code (e.g. US)")
    p.add_argument("--additional-queries", help="Comma-separated query variants (deep search only)")
    p.add_argument("--moderation", action="store_true", help="Enable content moderation (if available)")

    # Contents controls
    p.add_argument("--highlights", action="store_true", help="Request highlights in contents")
    p.add_argument("--highlights-query", help="Steer highlight selection with a custom query")
    p.add_argument("--highlights-per-url", type=int, help="Snippets per result (if supported)")
    p.add_argument("--num-sentences", type=int, help="Sentences per snippet (if supported)")
    p.add_argument("--highlights-max-chars", type=int, help="Cap highlight size (if supported)")

    p.add_argument("--text", action="store_true", help="Request full text in contents")
    p.add_argument("--text-max-chars", type=int, help="Cap returned text size")
    p.add_argument("--include-html-tags", action="store_true", help="Include HTML tags in text (if supported)")
    p.add_argument("--text-verbosity", choices=["compact", "standard", "full"], help="Verbosity level (if supported)")

    p.add_argument("--summary", action="store_true", help="Request summaries in contents")
    p.add_argument("--summary-query", help="Steer summaries with a custom query")

    p.add_argument("--subpages", type=int, help="Number of subpages to crawl")
    p.add_argument("--subpage-target", help="Keyword(s) to target subpages; comma-separated for multiple")
    p.add_argument("--extras-links", type=int, help="Number of links to return per result")
    p.add_argument("--extras-image-links", type=int, help="Number of image links to return per result")
    p.add_argument("--max-age-hours", type=int, help="Freshness policy for cached content")

    p.add_argument("--api-key", help="Exa API key (otherwise uses EXA_API_KEY env var)")
    p.add_argument("--timeout", type=int, default=60, help="HTTP timeout seconds (default: 60)")
    p.add_argument("--compact", action="store_true", help="Compact JSON output (no pretty-print)")

    args = p.parse_args()

    api_key = args.api_key or os.environ.get("EXA_API_KEY")
    if not api_key:
        print("Missing API key. Set EXA_API_KEY or pass --api-key.", file=sys.stderr)
        return 2

    payload: Dict[str, Any] = {"query": args.query, "type": args.type, "numResults": args.num_results}

    if args.category:
        payload["category"] = args.category
    if args.include_domains:
        payload["includeDomains"] = _split_csv(args.include_domains)
    if args.exclude_domains:
        payload["excludeDomains"] = _split_csv(args.exclude_domains)

    if args.start_crawl_date:
        payload["startCrawlDate"] = args.start_crawl_date
    if args.end_crawl_date:
        payload["endCrawlDate"] = args.end_crawl_date
    if args.start_published_date:
        payload["startPublishedDate"] = args.start_published_date
    if args.end_published_date:
        payload["endPublishedDate"] = args.end_published_date

    if args.include_text:
        payload["includeText"] = [args.include_text]
    if args.exclude_text:
        payload["excludeText"] = [args.exclude_text]

    if args.user_location:
        payload["userLocation"] = args.user_location

    if args.additional_queries:
        payload["additionalQueries"] = _split_csv(args.additional_queries)

    if args.moderation:
        payload["moderation"] = True

    contents = _build_contents(args)
    if contents is not None:
        payload["contents"] = contents

    _validate(args, payload)

    try:
        res = exa_search(api_key=api_key, payload=payload, timeout_s=args.timeout)
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
