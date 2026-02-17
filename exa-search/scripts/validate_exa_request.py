#!/usr/bin/env python3
"""
validate_exa_request.py — lightweight validator for Exa /search request JSON.

Usage:
  python scripts/validate_exa_request.py request.json
  cat request.json | python scripts/validate_exa_request.py -

Exit codes:
  0  OK
  2  Invalid request
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict


FORBIDDEN_FOR_COMPANY_PEOPLE = {
    "startPublishedDate",
    "endPublishedDate",
    "startCrawlDate",
    "endCrawlDate",
    "includeText",
    "excludeText",
    "excludeDomains",
}


def die(msg: str) -> int:
    print(f"Invalid: {msg}", file=sys.stderr)
    return 2


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: validate_exa_request.py <request.json|->", file=sys.stderr)
        return 2

    path = sys.argv[1]
    raw = sys.stdin.read() if path == "-" else open(path, "r", encoding="utf-8").read()
    try:
        payload: Dict[str, Any] = json.loads(raw)
    except Exception as e:
        return die(f"Could not parse JSON: {e}")

    if not isinstance(payload.get("query"), str) or not payload["query"].strip():
        return die("Missing non-empty 'query' (string)")

    t = payload.get("type", "auto")
    if t != "deep" and payload.get("additionalQueries"):
        return die("'additionalQueries' only works with type='deep'")

    n = payload.get("numResults", 10)
    if not isinstance(n, int) or n < 1 or n > 100:
        return die("'numResults' must be an integer in [1, 100]")

    category = payload.get("category")
    if category in {"company", "people"}:
        bad = [k for k in FORBIDDEN_FOR_COMPANY_PEOPLE if k in payload]
        if bad:
            return die(f"category '{category}' does not support: {', '.join(sorted(bad))}")

    # contents sanity checks (optional)
    contents = payload.get("contents")
    if contents is not None and not isinstance(contents, dict):
        return die("'contents' must be an object if provided")

    print("OK", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
