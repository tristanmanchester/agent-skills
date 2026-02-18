#!/usr/bin/env python3
"""Redact an OpenClaw JSON config file for safe sharing.

This script performs a best-effort redaction:
- Any key containing token/password/secret/key (case-insensitive) is masked.
- Any string value that looks like a long secret is partially masked.
- The output is JSON (pretty-printed) suitable for sharing with auditors.

Usage:
  python3 scripts/redact_openclaw_config.py ~/.openclaw/openclaw.json > openclaw.json.redacted
"""

from __future__ import annotations
import json
import re
import sys
from typing import Any

SENSITIVE_KEY_RE = re.compile(r"(token|password|secret|apikey|api_key|clientsecret|privatekey|key)\b", re.IGNORECASE)
# crude heuristic for "likely secret" strings
LIKELY_SECRET_RE = re.compile(r"^[A-Za-z0-9_\-]{24,}$")

def mask(s: str) -> str:
    if len(s) <= 8:
        return "***"
    return s[:4] + "…" + s[-4:]

def redact(obj: Any) -> Any:
    if isinstance(obj, dict):
        out = {}
        for k, v in obj.items():
            if SENSITIVE_KEY_RE.search(str(k)):
                # mask whole value regardless of type
                if isinstance(v, str):
                    out[k] = mask(v)
                else:
                    out[k] = "***"
            else:
                out[k] = redact(v)
        return out
    if isinstance(obj, list):
        return [redact(x) for x in obj]
    if isinstance(obj, str):
        if LIKELY_SECRET_RE.match(obj):
            return mask(obj)
        return obj
    return obj

def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: redact_openclaw_config.py <path-to-openclaw.json>", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    redacted = redact(data)
    json.dump(redacted, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")

if __name__ == "__main__":
    main()
