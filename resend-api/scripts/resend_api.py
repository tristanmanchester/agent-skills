#!/usr/bin/env python3
"""Resend API helper for agent skills.

Features:
- List endpoints from the bundled catalogue
- Inspect a compact schema summary for an endpoint
- Make live API calls with auth, user-agent, JSON parsing, cautious retries, and optional pagination

Environment:
- RESEND_API_KEY        Required for `request`
- RESEND_BASE_URL       Optional, defaults to https://api.resend.com
- RESEND_USER_AGENT     Optional, defaults to resend-api-skill/1.0
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CATALOG_PATH = SKILL_ROOT / "assets" / "endpoint-catalog.json"
DEFAULT_BASE_URL = "https://api.resend.com"
DEFAULT_USER_AGENT = "resend-api-skill/1.0"

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def load_catalog() -> Dict[str, Any]:
    with CATALOG_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def iter_endpoints(catalog: Dict[str, Any], include_beta: bool = False) -> Iterable[Dict[str, Any]]:
    for tag in catalog.get("tags", []):
        for endpoint in tag.get("endpoints", []):
            item = dict(endpoint)
            item["group"] = tag.get("name")
            item["group_description"] = tag.get("description")
            yield item

    if include_beta:
        beta = catalog.get("beta_notes", {})
        for beta_group, info in beta.items():
            for endpoint in info.get("confirmed_endpoints", []):
                item = dict(endpoint)
                item["group"] = f"beta:{beta_group}"
                item["group_description"] = info.get("ga_stability")
                item["beta_status"] = info.get("status")
                yield item


def endpoint_match_score(template_path: str, actual_path: str) -> Optional[int]:
    if template_path == actual_path:
        return 1000
    pattern = re.sub(r"\{[^/]+\}", "[^/]+", template_path)
    pattern = "^" + pattern + "$"
    if re.match(pattern, actual_path):
        literal_chars = len(re.sub(r"\{[^/]+\}", "", template_path))
        return 100 + literal_chars
    return None


def find_endpoint(catalog: Dict[str, Any], method: str, path: str, include_beta: bool = True) -> Dict[str, Any]:
    method = method.upper()
    candidates: List[tuple[int, Dict[str, Any]]] = []
    for endpoint in iter_endpoints(catalog, include_beta=include_beta):
        if endpoint.get("method", "").upper() != method:
            continue
        score = endpoint_match_score(endpoint["path"], path)
        if score is not None:
            candidates.append((score, endpoint))
    if not candidates:
        raise SystemExit(f"Error: could not find endpoint metadata for {method} {path}")
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def parse_kv_pairs(pairs: Optional[List[str]]) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for item in pairs or []:
        if "=" not in item:
            raise SystemExit(f"Error: expected KEY=VALUE, got: {item!r}")
        key, value = item.split("=", 1)
        result[key] = value
    return result


def parse_headers(header_items: Optional[List[str]]) -> Dict[str, str]:
    headers: Dict[str, str] = {}
    for item in header_items or []:
        if ":" not in item:
            raise SystemExit(f"Error: expected 'Header: value', got: {item!r}")
        name, value = item.split(":", 1)
        headers[name.strip()] = value.strip()
    return headers


def print_json(data: Any) -> None:
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def command_catalog(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    results = []
    for endpoint in iter_endpoints(catalog, include_beta=args.include_beta):
        if args.group and endpoint.get("group", "").lower() != args.group.lower():
            continue
        if args.method and endpoint.get("method", "").upper() != args.method.upper():
            continue
        haystack = " ".join(
            str(endpoint.get(k, "")) for k in ("group", "path", "summary", "description")
        ).lower()
        if args.search and args.search.lower() not in haystack:
            continue
        if not args.include_deprecated and endpoint.get("deprecated"):
            continue
        results.append(
            {
                "group": endpoint.get("group"),
                "method": endpoint.get("method"),
                "path": endpoint.get("path"),
                "summary": endpoint.get("summary"),
                "deprecated": bool(endpoint.get("deprecated", False)),
            }
        )

    if args.format == "json":
        print_json({"count": len(results), "endpoints": results})
        return 0

    if not results:
        print("No endpoints matched.", file=sys.stderr)
        return 1

    group_width = max(len(item["group"] or "") for item in results)
    method_width = max(len(item["method"] or "") for item in results)
    path_width = max(len(item["path"] or "") for item in results)
    header = f"{'GROUP'.ljust(group_width)}  {'METHOD'.ljust(method_width)}  {'PATH'.ljust(path_width)}  SUMMARY"
    print(header)
    print("-" * len(header))
    for item in results:
        print(
            f"{(item['group'] or '').ljust(group_width)}  "
            f"{(item['method'] or '').ljust(method_width)}  "
            f"{(item['path'] or '').ljust(path_width)}  "
            f"{item['summary'] or ''}"
        )
    return 0


def command_schema(args: argparse.Namespace) -> int:
    catalog = load_catalog()
    endpoint = find_endpoint(catalog, args.method, args.path, include_beta=True)
    result = {
        "group": endpoint.get("group"),
        "method": endpoint.get("method"),
        "path": endpoint.get("path"),
        "summary": endpoint.get("summary"),
        "description": endpoint.get("description"),
        "deprecated": endpoint.get("deprecated", False),
        "beta_status": endpoint.get("beta_status"),
        "parameters": endpoint.get("parameters"),
        "request_body": endpoint.get("request_body"),
        "responses": endpoint.get("responses"),
        "group_description": endpoint.get("group_description"),
    }
    print_json(result)
    return 0


def build_url(base_url: str, path: str, query: Dict[str, str]) -> str:
    if not path.startswith("/"):
        raise SystemExit("Error: path must start with '/'")
    url = base_url.rstrip("/") + path
    if query:
        url += "?" + urllib.parse.urlencode(query, doseq=True)
    return url


def should_retry(method: str, status: Optional[int], attempt: int, max_retries: int) -> bool:
    # attempt is the current failed attempt number. Retries are allowed while attempt <= max_retries.
    if attempt > max_retries:
        return False
    if status is None:
        return True
    return status in RETRYABLE_STATUSES


def parse_response_body(content_type: str, raw_bytes: bytes) -> Any:
    lowered = (content_type or "").lower()
    if "application/json" in lowered or lowered.endswith("+json"):
        try:
            return json.loads(raw_bytes.decode("utf-8"))
        except Exception:
            return {"_raw_text": raw_bytes.decode("utf-8", errors="replace")}
    if lowered.startswith("text/") or "charset=" in lowered:
        return raw_bytes.decode("utf-8", errors="replace")
    return {
        "_binary_base64": base64.b64encode(raw_bytes).decode("ascii"),
        "_content_type": content_type,
        "_byte_length": len(raw_bytes),
        "_hint": "Binary response. Prefer --output FILE for attachments or other large payloads."
    }


def maybe_paginate(
    opener: urllib.request.OpenerDirector,
    method: str,
    url: str,
    headers: Dict[str, str],
    timeout: float,
    page_limit: int,
) -> Dict[str, Any]:
    pages: List[Any] = []
    page_urls: List[str] = []
    next_url = url
    page_count = 0

    while next_url and page_count < page_limit:
        req = urllib.request.Request(next_url, method=method, headers=headers)
        with opener.open(req, timeout=timeout) as resp:
            raw = resp.read()
            content_type = resp.headers.get("Content-Type", "")
            body = parse_response_body(content_type, raw)
            pages.append(body)
            page_urls.append(next_url)
            page_count += 1

            next_candidate = None
            if (
                isinstance(body, dict)
                and body.get("object") == "list"
                and body.get("has_more")
                and isinstance(body.get("data"), list)
                and body["data"]
                and isinstance(body["data"][-1], dict)
                and body["data"][-1].get("id")
            ):
                parsed = urllib.parse.urlparse(next_url)
                current_query = dict(urllib.parse.parse_qsl(parsed.query))
                current_query["after"] = str(body["data"][-1]["id"])
                next_candidate = urllib.parse.urlunparse(
                    (
                        parsed.scheme,
                        parsed.netloc,
                        parsed.path,
                        parsed.params,
                        urllib.parse.urlencode(current_query, doseq=True),
                        parsed.fragment,
                    )
                )
            next_url = next_candidate

    return {
        "pages": pages,
        "page_urls": page_urls,
        "page_count": page_count,
        "truncated": page_count >= page_limit and next_url is not None,
    }


def command_request(args: argparse.Namespace) -> int:
    method = args.method.upper()
    query = parse_kv_pairs(args.query)
    extra_headers = parse_headers(args.header)
    base_url = os.environ.get("RESEND_BASE_URL", DEFAULT_BASE_URL)
    user_agent = os.environ.get("RESEND_USER_AGENT", DEFAULT_USER_AGENT)
    api_key = os.environ.get("RESEND_API_KEY")

    if method not in SAFE_METHODS and args.retries > 0 and not (args.idempotency_key or args.unsafe_retries):
        raise SystemExit(
            "Error: refusing to auto-retry a non-safe method without --idempotency-key or --unsafe-retries"
        )

    if args.paginate and method != "GET":
        raise SystemExit("Error: --paginate is only supported for GET requests")

    body_bytes: Optional[bytes] = None
    body_obj: Any = None
    if args.json and args.json_file:
        raise SystemExit("Error: choose either --json or --json-file, not both")
    if args.json:
        try:
            body_obj = json.loads(args.json)
        except json.JSONDecodeError as e:
            raise SystemExit(f"Error: invalid --json payload: {e}")
    elif args.json_file:
        try:
            body_obj = json.loads(Path(args.json_file).read_text(encoding="utf-8"))
        except Exception as e:
            raise SystemExit(f"Error: failed to read --json-file: {e}")

    if body_obj is not None:
        body_bytes = json.dumps(body_obj).encode("utf-8")

    headers: Dict[str, str] = {
        "User-Agent": user_agent,
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if body_bytes is not None:
        headers["Content-Type"] = "application/json"
    if args.idempotency_key:
        headers["Idempotency-Key"] = args.idempotency_key
    headers.update(extra_headers)

    if args.require_auth and "Authorization" not in headers and not args.dry_run:
        raise SystemExit("Error: RESEND_API_KEY is required for request mode")

    url = build_url(base_url, args.path, query)

    prepared = {
        "method": method,
        "url": url,
        "headers": headers,
        "json_body": body_obj,
    }
    if args.dry_run:
        print_json({"dry_run": True, "request": prepared})
        return 0

    opener = urllib.request.build_opener()
    attempt = 0
    last_status: Optional[int] = None

    while True:
        attempt += 1
        req = urllib.request.Request(url, data=body_bytes, method=method, headers=headers)
        try:
            if args.paginate:
                paginated = maybe_paginate(
                    opener=opener,
                    method=method,
                    url=url,
                    headers=headers,
                    timeout=args.timeout,
                    page_limit=args.page_limit,
                )
                result = {
                    "ok": True,
                    "status": 200,
                    "request": prepared,
                    "pagination": paginated,
                }
                if args.output:
                    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                    print_json({"ok": True, "status": 200, "output_file": str(args.output)})
                else:
                    print_json(result)
                return 0

            with opener.open(req, timeout=args.timeout) as resp:
                status = resp.getcode()
                last_status = status
                raw = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                parsed_body = parse_response_body(content_type, raw)
                result = {
                    "ok": 200 <= status < 300,
                    "status": status,
                    "request": prepared,
                    "response": {
                        "content_type": content_type,
                        "body": parsed_body,
                    },
                }
                if args.include_headers:
                    result["response"]["headers"] = dict(resp.headers.items())

                if args.output:
                    if isinstance(parsed_body, dict) and "_binary_base64" in parsed_body and args.binary_output:
                        Path(args.binary_output).write_bytes(base64.b64decode(parsed_body["_binary_base64"]))
                        result["response"]["saved_binary_to"] = str(args.binary_output)
                    Path(args.output).write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
                    print_json({"ok": result["ok"], "status": status, "output_file": str(args.output)})
                else:
                    print_json(result)
                return 0 if result["ok"] else 1

        except urllib.error.HTTPError as e:
            last_status = e.code
            raw = e.read()
            content_type = e.headers.get("Content-Type", "")
            parsed_body = parse_response_body(content_type, raw)
            error_result = {
                "ok": False,
                "status": e.code,
                "request": prepared,
                "response": {
                    "content_type": content_type,
                    "body": parsed_body,
                },
                "attempt": attempt,
            }
            if args.include_headers:
                error_result["response"]["headers"] = dict(e.headers.items())

            if should_retry(method, e.code, attempt, args.retries):
                print(
                    f"Retrying after HTTP {e.code} (attempt {attempt} of {args.retries + 1})...",
                    file=sys.stderr,
                )
                time.sleep(args.backoff)
                continue

            if args.output:
                Path(args.output).write_text(json.dumps(error_result, indent=2, ensure_ascii=False), encoding="utf-8")
                print_json({"ok": False, "status": e.code, "output_file": str(args.output)})
            else:
                print_json(error_result)
            return 1

        except urllib.error.URLError as e:
            if should_retry(method, None, attempt, args.retries):
                print(
                    f"Retrying after network error: {e.reason} (attempt {attempt} of {args.retries + 1})...",
                    file=sys.stderr,
                )
                time.sleep(args.backoff)
                continue
            print_json(
                {
                    "ok": False,
                    "status": last_status,
                    "request": prepared,
                    "error": {
                        "type": "network_error",
                        "message": str(e.reason),
                    },
                    "attempt": attempt,
                }
            )
            return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect the bundled Resend API catalogue or make live Resend API requests."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_catalog = subparsers.add_parser("catalog", help="List known stable endpoints")
    p_catalog.add_argument("--group", help="Filter by group/tag name, e.g. Emails")
    p_catalog.add_argument("--method", help="Filter by HTTP method, e.g. POST")
    p_catalog.add_argument("--search", help="Free-text filter over group/path/summary")
    p_catalog.add_argument("--format", choices=["json", "table"], default="table")
    p_catalog.add_argument("--include-beta", action="store_true", help="Include beta/private-alpha notes")
    p_catalog.add_argument("--include-deprecated", action="store_true", help="Include deprecated endpoints")
    p_catalog.set_defaults(func=command_catalog)

    p_schema = subparsers.add_parser("schema", help="Show schema/parameter summary for an endpoint")
    p_schema.add_argument("method", help="HTTP method, e.g. POST")
    p_schema.add_argument("path", help="Endpoint path, e.g. /emails or /domains/{domain_id}")
    p_schema.set_defaults(func=command_schema)

    p_request = subparsers.add_parser("request", help="Make a live API request")
    p_request.add_argument("method", help="HTTP method, e.g. GET or POST")
    p_request.add_argument("path", help="Endpoint path, e.g. /domains")
    p_request.add_argument("--query", action="append", help="Query parameter as KEY=VALUE", default=[])
    p_request.add_argument("--header", action="append", help="Additional header as 'Name: value'", default=[])
    p_request.add_argument("--json", help="Inline JSON request body")
    p_request.add_argument("--json-file", help="Path to a JSON request body")
    p_request.add_argument("--idempotency-key", help="Idempotency-Key header value")
    p_request.add_argument("--timeout", type=float, default=30.0, help="Request timeout in seconds (default: 30)")
    p_request.add_argument("--retries", type=int, default=0, help="Retry count for 429/5xx/network errors")
    p_request.add_argument("--backoff", type=float, default=1.0, help="Sleep between retries in seconds")
    p_request.add_argument("--dry-run", action="store_true", help="Print the prepared request without sending it")
    p_request.add_argument("--paginate", action="store_true", help="Follow cursor pagination for GET list endpoints")
    p_request.add_argument("--page-limit", type=int, default=5, help="Maximum pages when --paginate is used")
    p_request.add_argument("--output", help="Write the structured result JSON to a file")
    p_request.add_argument(
        "--binary-output",
        help="When the response is binary and --output is used, also decode and save the bytes here",
    )
    p_request.add_argument("--include-headers", action="store_true", help="Include response headers in JSON output")
    p_request.add_argument("--unsafe-retries", action="store_true", help="Allow retries for non-safe methods")
    p_request.add_argument(
        "--no-auth-check",
        dest="require_auth",
        action="store_false",
        help="Allow unauthenticated requests (default is to require RESEND_API_KEY)",
    )
    p_request.set_defaults(func=command_request, require_auth=True)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
