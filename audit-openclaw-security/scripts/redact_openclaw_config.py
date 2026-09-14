#!/usr/bin/env python3
"""Redact parsed JSON/JSON5 configuration; never emit unparsed source text.

JSON5 input requires json5 or pyjson5. Output is JSON, not a usable backup.
Unknown secret names and secrets in free text still require human review.
"""
from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

REDACTED = "[REDACTED]"
SENSITIVE_KEY_RE = re.compile(
    r"token|password|passwd|passphrase|secret|apikey|privatekey|sessionkey|"
    r"cookie|bearer|authorization|credential|signature", re.IGNORECASE
)
URL_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+.-]*://[^\s<>\"']+")
OPAQUE_RE = re.compile(r"(?:[A-Za-z0-9_-]{24,}|[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+)\Z")


def sensitive_key(key: str) -> bool:
    normalised = re.sub(r"[^a-z0-9]", "", key.lower())
    return bool(SENSITIVE_KEY_RE.search(normalised))


def redact_url(match: re.Match[str]) -> str:
    try:
        parts = urlsplit(match.group(0))
        # Remove all userinfo, not just passwords. Do not expose URI fragments.
        authority = parts.netloc.rsplit("@", 1)[-1]
        if "@" in parts.netloc:
            authority = "REDACTED@" + authority
        query = urlencode([
            (key, REDACTED if sensitive_key(key) or key.lower() in {"key", "code", "sig"} else value)
            for key, value in parse_qsl(parts.query, keep_blank_values=True)
        ])
        return urlunsplit((parts.scheme, authority, parts.path, query, "REDACTED" if parts.fragment else ""))
    except ValueError:
        return REDACTED


def redact_string(value: str) -> str:
    if "PRIVATE KEY-----" in value or OPAQUE_RE.fullmatch(value):
        return REDACTED
    return URL_RE.sub(redact_url, value)


def redact_obj(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            str(key): REDACTED if sensitive_key(str(key)) else redact_obj(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact_obj(item) for item in value]
    if isinstance(value, str):
        return redact_string(value)
    return value


def parse_config(raw: str) -> dict[str, Any]:
    try:
        value = json.loads(raw)
    except ValueError:
        value = None
        for name in ("json5", "pyjson5"):
            try:
                parser = importlib.import_module(name)
            except ImportError:
                continue
            try:
                value = parser.loads(raw)
                break
            except Exception:
                # Parser errors can contain the source line: do not print them.
                continue
        if value is None:
            raise ValueError("Cannot parse configuration. Install json5 for JSON5 input; no output was produced.") from None
    if not isinstance(value, dict):
        raise ValueError("Configuration must be an object; no output was produced.")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="-", help="JSON/JSON5 file, or - for stdin")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.path == "-" else Path(args.path).expanduser().read_text(encoding="utf-8")
        # Serialize completely before writing: parsing/encoding errors produce no stdout.
        result = json.dumps(redact_obj(parse_config(raw)), indent=2, ensure_ascii=False, allow_nan=False)
    except (OSError, UnicodeError, ValueError, RecursionError):
        print("Redaction failed: provide valid UTF-8 JSON/JSON5 (JSON5 needs json5 or pyjson5). No configuration was emitted.", file=sys.stderr)
        return 2
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
