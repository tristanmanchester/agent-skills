#!/usr/bin/env python3
"""
Lightweight Notion API requester for agent workflows.

Usage:
  python scripts/notion_request.py GET  /v1/users/me
  python scripts/notion_request.py POST /v1/search --json '{"query":"foo","page_size":5}'
  python scripts/notion_request.py POST /v1/data_sources/<id>/query --paginate --json '{"page_size":100}'

Environment:
  NOTION_TOKEN (preferred) or NOTION_API_KEY or NOTION_API_TOKEN
  NOTION_VERSION (default: 2025-09-03)
  NOTION_BASE_URL (default: https://api.notion.com)
"""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple

DEFAULT_VERSION = "2025-09-03"
DEFAULT_BASE_URL = "https://api.notion.com"

EXIT_SUCCESS = 0
EXIT_ERROR = 1
EXIT_INVALID_ARGS = 2
EXIT_PERMISSION = 4
EXIT_TIMEOUT = 5


def _get_env_token() -> Optional[str]:
    for k in ("NOTION_TOKEN", "NOTION_API_KEY", "NOTION_API_TOKEN"):
        v = os.getenv(k)
        if v:
            return v.strip()
    return None


def _build_url(base_url: str, path_or_url: str) -> str:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        return path_or_url
    # allow passing "/v1/..." or "v1/..." or "/pages/...".
    path = path_or_url
    if not path.startswith("/"):
        path = "/" + path
    # If user passed "/v1/...", join onto base without duplicating "/v1"
    return urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))


def _request(
    method: str,
    url: str,
    token: str,
    notion_version: str,
    body: Optional[Dict[str, Any]] = None,
    timeout_s: int = 60,
) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": notion_version,
        "Accept": "application/json",
    }
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url=url, method=method.upper(), headers=headers, data=data)
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read().decode("utf-8")
            payload = json.loads(raw) if raw else {}
            # normalise header keys
            resp_headers = {k: v for k, v in resp.headers.items()}
            return resp.status, payload, resp_headers
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8") if e.fp else ""
        try:
            payload = json.loads(raw) if raw else {}
        except Exception:
            payload = {"raw": raw}
        resp_headers = {k: v for k, v in e.headers.items()} if e.headers else {}
        return e.code, payload, resp_headers
    except urllib.error.URLError as e:
        return 0, {"error": "url_error", "message": str(e)}, {}
    except TimeoutError:
        return 0, {"error": "timeout"}, {}


def _sleep_with_jitter(base_seconds: float) -> None:
    jitter = random.random() * 0.25 * base_seconds
    time.sleep(base_seconds + jitter)


def call_with_retries(
    method: str,
    url: str,
    token: str,
    notion_version: str,
    body: Optional[Dict[str, Any]],
    timeout_s: int,
    max_attempts: int,
) -> Tuple[int, Dict[str, Any]]:
    attempt = 0
    while True:
        attempt += 1
        status, payload, headers = _request(
            method=method, url=url, token=token, notion_version=notion_version, body=body, timeout_s=timeout_s
        )

        # Success
        if 200 <= status < 300:
            return status, payload

        # Rate limited
        if status == 429:
            retry_after = headers.get("Retry-After")
            if retry_after and retry_after.isdigit():
                _sleep_with_jitter(float(retry_after))
            else:
                _sleep_with_jitter(2.0)
        # Transient server issues
        elif status in (500, 503) or (status == 0 and payload.get("error") in ("url_error", "timeout")):
            backoff = min(30.0, 2.0 ** attempt)
            _sleep_with_jitter(backoff)
        else:
            # Non-retryable
            return status, payload

        if attempt >= max_attempts:
            return status, payload


def paginate_notion_style(
    method: str,
    url: str,
    token: str,
    notion_version: str,
    body: Optional[Dict[str, Any]],
    timeout_s: int,
    max_attempts: int,
    results_key: str = "results",
) -> Dict[str, Any]:
    if method.upper() not in ("POST", "GET", "PATCH"):
        raise ValueError("Pagination helper currently supports POST/GET/PATCH only.")

    all_results = []
    next_cursor: Optional[str] = None
    has_more = True

    while has_more:
        page_body = dict(body or {})
        if next_cursor:
            page_body["start_cursor"] = next_cursor

        status, payload = call_with_retries(
            method=method,
            url=url,
            token=token,
            notion_version=notion_version,
            body=page_body if method.upper() != "GET" else None,
            timeout_s=timeout_s,
            max_attempts=max_attempts,
        )
        if not (200 <= status < 300):
            return {"error": True, "status": status, "payload": payload}

        chunk = payload.get(results_key)
        if isinstance(chunk, list):
            all_results.extend(chunk)
        else:
            # Some endpoints use different keys; preserve payload and stop.
            return {"error": True, "status": 200, "payload": payload, "message": f"Expected list at key '{results_key}'."}

        has_more = bool(payload.get("has_more"))
        next_cursor = payload.get("next_cursor")

        if not next_cursor:
            has_more = False

    return {"object": "list", results_key: all_results, "has_more": False, "next_cursor": None}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("method", help="HTTP method, e.g. GET/POST/PATCH/DELETE")
    p.add_argument("path", help="Path like /v1/users/me or full URL")
    p.add_argument("--json", dest="json_str", help="JSON body as a string")
    p.add_argument("--json-file", dest="json_file", help="JSON body from a file")
    p.add_argument("--paginate", action="store_true", help="Auto-paginate Notion-style responses")
    p.add_argument("--results-key", default="results", help="List key in paginated responses (default: results)")
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--max-attempts", type=int, default=6)
    args = p.parse_args()

    token = _get_env_token()
    if not token:
        print("ERROR: missing NOTION_TOKEN (or NOTION_API_KEY/NOTION_API_TOKEN) in environment.", file=sys.stderr)
        return EXIT_INVALID_ARGS

    notion_version = os.getenv("NOTION_VERSION", DEFAULT_VERSION).strip()
    base_url = os.getenv("NOTION_BASE_URL", DEFAULT_BASE_URL).strip()

    url = _build_url(base_url, args.path)

    body: Optional[Dict[str, Any]] = None
    if args.json_str and args.json_file:
        print("ERROR: use only one of --json or --json-file", file=sys.stderr)
        return EXIT_INVALID_ARGS

    if args.json_str:
        body = json.loads(args.json_str)
    elif args.json_file:
        with open(args.json_file, "r", encoding="utf-8") as f:
            body = json.load(f)

    if args.paginate:
        out = paginate_notion_style(
            method=args.method,
            url=url,
            token=token,
            notion_version=notion_version,
            body=body,
            timeout_s=args.timeout,
            max_attempts=args.max_attempts,
            results_key=args.results_key,
        )
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return EXIT_SUCCESS if not out.get("error") else EXIT_ERROR

    status, payload = call_with_retries(
        method=args.method,
        url=url,
        token=token,
        notion_version=notion_version,
        body=body,
        timeout_s=args.timeout,
        max_attempts=args.max_attempts,
    )

    print(json.dumps({"status": status, "payload": payload}, ensure_ascii=False, indent=2))

    if 200 <= status < 300:
        return EXIT_SUCCESS
    if status in (401, 403):
        return EXIT_PERMISSION
    if status == 0 and payload.get("error") == "timeout":
        return EXIT_TIMEOUT
    return EXIT_ERROR


if __name__ == "__main__":
    raise SystemExit(main())
