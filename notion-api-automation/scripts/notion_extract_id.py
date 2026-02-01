#!/usr/bin/env python3
"""
Extract a Notion UUID-ish id from a Notion URL or accept an id as-is.

Usage:
  python scripts/notion_extract_id.py "https://www.notion.so/My-Page-a07589e357414b3285a8d02beb8fd9dd"
  python scripts/notion_extract_id.py "a07589e357414b3285a8d02beb8fd9dd"
"""

from __future__ import annotations

import re
import sys

# Matches UUID with or without dashes, but returns the compact 32-hex form if possible.
UUID_32 = re.compile(r"([0-9a-fA-F]{32})")
UUID_36 = re.compile(r"([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})")


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: notion_extract_id.py <notion-url-or-id>", file=sys.stderr)
        return 2

    s = sys.argv[1].strip()

    m32 = UUID_32.search(s)
    if m32:
        print(m32.group(1))
        return 0

    m36 = UUID_36.search(s)
    if m36:
        print(m36.group(1))
        return 0

    print("ERROR: No Notion-style id found.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
