#!/usr/bin/env python3
"""17TRACK v2.2 parcel CLI: explicit storage, polling, authenticated webhooks.

TRACK17_TOKEN is the API key and the webhook signing key. No secret CLI flags.
All commands print JSON; errors use stderr and a non-zero exit status.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timezone
import hashlib
import hmac
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import re
import socket
import sqlite3
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.17track.net/track/v2.2"
CARRIERS_URL = "https://res.17track.net/asset/carrier/info/apicarrier.all.json"
MAX_BODY = 4 * 1024 * 1024


class Track17Error(RuntimeError):
    pass


class AuthenticationError(Track17Error):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise Track17Error("Unexpected redirect; credentials were not forwarded")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def token() -> str:
    value = os.environ.get("TRACK17_TOKEN", "")
    if not value:
        raise AuthenticationError("Set TRACK17_TOKEN in the environment")
    return value


def signature(raw: bytes, key: str) -> str:
    return hashlib.sha256(raw + b"/" + key.encode("utf-8")).hexdigest()


def verify_signature(raw: bytes, sign: str | None, key: str | None) -> None:
    if not key or not sign or not re.fullmatch(r"[0-9a-fA-F]{64}", sign):
        raise AuthenticationError("Missing or malformed webhook authentication")
    if not hmac.compare_digest(signature(raw, key), sign.lower()):
        raise AuthenticationError("Invalid webhook signature")


def api(endpoint: str, payload: Any = None) -> dict[str, Any]:
    allowed = {"register", "gettrackinfo", "getquota", "stoptrack", "retrack", "deletetrack"}
    if endpoint not in allowed:
        raise Track17Error("Unsupported endpoint")
    body = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = Request(f"{API_BASE}/{endpoint}", data=body, method="POST", headers={
        "Content-Type": "application/json", "17token": token(), "User-Agent": "track17-skill/2"
    })
    try:
        with build_opener(NoRedirect).open(request, timeout=30) as response:
            result = json.load(response)
    except HTTPError as exc:
        raise Track17Error(f"17TRACK HTTP {exc.code}; no request was automatically retried") from None
    except (URLError, TimeoutError, OSError) as exc:
        raise Track17Error("17TRACK request failed; write outcome may be unknown. Reconcile before retrying.") from None
    except (ValueError, UnicodeError):
        raise Track17Error("17TRACK returned invalid JSON; reconcile writes before retrying") from None
    if not isinstance(result, dict) or result.get("code") not in (0, "0"):
        raise Track17Error("17TRACK returned an API error")
    return result


def accepted(response: dict[str, Any]) -> tuple[list[dict[str, Any]], list[Any]]:
    data = response.get("data")
    if not isinstance(data, dict) or data.get("errors"):
        raise Track17Error("17TRACK rejected the request")
    good, bad = data.get("accepted", []), data.get("rejected", [])
    if not isinstance(good, list) or not all(isinstance(x, dict) for x in good) or not isinstance(bad, list):
        raise Track17Error("Unexpected 17TRACK response shape")
    return good, bad


def require_accepted(response: dict[str, Any]) -> list[dict[str, Any]]:
    good, bad = accepted(response)
    if bad or not good:
        raise Track17Error("17TRACK did not confirm the requested change; local state was not changed")
    return good


def database_path() -> Path:
    directory = os.environ.get("TRACK17_DATA_DIR")
    if not directory:
        raise Track17Error("Set TRACK17_DATA_DIR to a private absolute data directory")
    path = Path(directory).expanduser()
    if not path.is_absolute():
        raise Track17Error("TRACK17_DATA_DIR must be an absolute path")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path / "track17.sqlite3"


def connect(path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(path, timeout=10)
    if conn.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='packages'").fetchone():
        conn.close()
        raise Track17Error("Legacy database detected; it was left unchanged. Use a new TRACK17_DATA_DIR and re-register selected parcels.")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS parcels (
      number TEXT NOT NULL, carrier INTEGER NOT NULL, label TEXT NOT NULL DEFAULT '',
      param TEXT NOT NULL DEFAULT '', lang TEXT NOT NULL DEFAULT 'en',
      snapshot TEXT NOT NULL DEFAULT '{}', updated_at TEXT NOT NULL,
      PRIMARY KEY(number, carrier)
    );
    CREATE TABLE IF NOT EXISTS receipts (
      digest TEXT PRIMARY KEY, received_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS parcel_events (
      number TEXT NOT NULL, carrier INTEGER NOT NULL, digest TEXT NOT NULL,
      event_json TEXT NOT NULL, PRIMARY KEY(number, carrier, digest),
      FOREIGN KEY(number, carrier) REFERENCES parcels(number, carrier) ON DELETE CASCADE
    );
    """)
    conn.commit()
    return conn


def identity(item: dict[str, Any]) -> tuple[str, int]:
    number = item.get("number")
    carrier = item.get("carrier")
    if not isinstance(number, str) or not re.fullmatch(r"[A-Za-z0-9-]{5,50}", number):
        raise Track17Error("Invalid tracking number")
    if isinstance(carrier, bool) or not isinstance(carrier, int) or carrier <= 0:
        raise Track17Error("A resolved positive carrier code is required")
    return number, carrier


def event_time(item: dict[str, Any]) -> datetime | None:
    info = item.get("track_info") or {}
    event = info.get("latest_event") or {}
    value = event.get("time_utc") or event.get("time_iso")
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.replace(tzinfo=timezone.utc) if parsed.tzinfo is None else parsed.astimezone(timezone.utc)
    except (ValueError, AttributeError, TypeError):
        raise Track17Error("Invalid latest-event timestamp") from None


def validate_item(item: dict[str, Any]) -> None:
    identity(item)
    info = item.get("track_info")
    if info is not None and not isinstance(info, dict):
        raise Track17Error("Invalid track_info")
    if info:
        for name in ("latest_event", "latest_status", "tracking"):
            if info.get(name) is not None and not isinstance(info[name], dict):
                raise Track17Error(f"Invalid track_info.{name}")
    event_time(item)


def apply_item(conn: sqlite3.Connection, item: dict[str, Any], *, label: str | None = None) -> bool:
    number, carrier = identity(item)
    current = conn.execute("SELECT * FROM parcels WHERE number=? AND carrier=?", (number, carrier)).fetchone()
    previous = json.loads(current["snapshot"]) if current else {}
    old_time, new_time = event_time(previous), event_time(item)
    # Without ordering evidence, do not replace a dated snapshot with an undated one.
    stale = old_time is not None and (new_time is None or new_time < old_time)
    serialised = json.dumps(item, sort_keys=True, ensure_ascii=False)
    changed = not stale and (not current or current["snapshot"] != serialised)
    if not current:
        conn.execute("INSERT INTO parcels(number,carrier,label,param,lang,snapshot,updated_at) VALUES(?,?,?,?,?,?,?)",
                     (number, carrier, label or "", item.get("param") or "", item.get("lang") or "en", serialised, now()))
    elif changed:
        conn.execute("UPDATE parcels SET snapshot=?,updated_at=? WHERE number=? AND carrier=?", (serialised, now(), number, carrier))
    if label is not None:
        conn.execute("UPDATE parcels SET label=? WHERE number=? AND carrier=?", (label, number, carrier))
    info = item.get("track_info") or {}
    providers = (info.get("tracking") or {}).get("providers") or []
    if not isinstance(providers, list):
        raise Track17Error("Invalid provider list")
    for provider in providers:
        if not isinstance(provider, dict) or not isinstance(provider.get("events") or [], list):
            raise Track17Error("Invalid event provider")
        for event in provider.get("events") or []:
            if not isinstance(event, dict):
                raise Track17Error("Invalid tracking event")
            data = json.dumps({"provider": provider.get("key"), "event": event}, sort_keys=True, ensure_ascii=False)
            digest = hashlib.sha256(data.encode()).hexdigest()
            conn.execute("INSERT OR IGNORE INTO parcel_events VALUES(?,?,?,?)", (number, carrier, digest, data))
    return changed


def parse_webhook(raw: bytes, sign: str | None, key: str | None) -> dict[str, Any]:
    # Authentication precedes parsing and all storage operations.
    verify_signature(raw, sign, key)
    if len(raw) > MAX_BODY:
        raise Track17Error("Webhook exceeds body limit")
    try:
        payload = json.loads(raw)
    except (ValueError, UnicodeError):
        raise Track17Error("Invalid webhook JSON") from None
    if not isinstance(payload, dict) or payload.get("event") != "TRACKING_UPDATED" or not isinstance(payload.get("data"), dict):
        raise Track17Error("Expected a TRACKING_UPDATED event with a data object")
    validate_item(payload["data"])
    return payload["data"]


def ingest_payload(conn: sqlite3.Connection, raw: bytes, sign: str | None, key: str | None) -> dict[str, Any]:
    item = parse_webhook(raw, sign, key)
    digest = hashlib.sha256(raw).hexdigest()
    with conn:
        conn.execute("BEGIN IMMEDIATE")
        if conn.execute("SELECT 1 FROM receipts WHERE digest=?", (digest,)).fetchone():
            return {"duplicate": True, "changed": False}
        changed = apply_item(conn, item)
        conn.execute("INSERT INTO receipts VALUES(?,?)", (digest, now()))
    return {"duplicate": False, "changed": changed, "number": item["number"], "carrier": item["carrier"]}


class WebhookServer(ThreadingHTTPServer):
    def __init__(self, address: tuple[str, int], path: Path, key: str):
        if not key:
            raise AuthenticationError("Webhook server requires TRACK17_TOKEN")
        self.db_path, self.key = path, key
        super().__init__(address, WebhookHandler)


class WebhookHandler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(10)

    def do_POST(self):
        try:
            lengths = self.headers.get_all("Content-Length", [])
            signs = self.headers.get_all("sign", [])
            if self.headers.get("Transfer-Encoding") or len(lengths) != 1:
                self.send_error(411)
                return
            length = int(lengths[0])
            if not 0 < length <= MAX_BODY:
                self.send_error(413)
                return
            if len(signs) != 1:
                raise AuthenticationError("Missing or duplicate sign header")
            raw = self.rfile.read(length)
            if len(raw) != length:
                raise Track17Error("Truncated request")
            # Do not even open/create the DB until authentication and shape checks pass.
            parse_webhook(raw, signs[0], self.server.key)
            with closing(connect(self.server.db_path)) as conn:
                result = ingest_payload(conn, raw, signs[0], self.server.key)
            body = json.dumps(result).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except AuthenticationError:
            self.send_error(401)
        except (Track17Error, ValueError, socket.timeout):
            self.send_error(400)
        except (sqlite3.Error, OSError):
            self.send_error(503)

    def log_message(self, *_args):
        # No bodies, signatures, or tracking identifiers in HTTP logs.
        pass


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    sub = result.add_subparsers(dest="command", required=True)
    sub.add_parser("init")
    sub.add_parser("list")
    sub.add_parser("sync")
    sub.add_parser("quota")
    add = sub.add_parser("add")
    add.add_argument("number")
    add.add_argument("--carrier", type=int, default=0)
    add.add_argument("--label", default="")
    add.add_argument("--param", default="")
    add.add_argument("--lang", default="en")
    for action in ("status", "stop", "retrack", "remove"):
        cmd = sub.add_parser(action)
        cmd.add_argument("number")
        cmd.add_argument("--carrier", type=int, required=True)
        if action == "status":
            cmd.add_argument("--refresh", action="store_true")
        if action == "remove":
            cmd.add_argument("--delete-remote", action="store_true")
    ingest = sub.add_parser("ingest-webhook")
    ingest.add_argument("--file", type=Path, required=True)
    ingest.add_argument("--signature", required=True, help="Exact sign response header; never the signing key")
    serve = sub.add_parser("webhook-server")
    serve.add_argument("--port", type=int, default=8789)
    carriers = sub.add_parser("carriers-search")
    carriers.add_argument("query")
    return result


def run(args: argparse.Namespace) -> tuple[Any, int]:
    command = args.command
    if command == "quota":
        return api("getquota").get("data"), 0
    if command == "carriers-search":
        try:
            with build_opener(NoRedirect).open(CARRIERS_URL, timeout=30) as response:
                carriers = json.load(response)
        except (OSError, ValueError):
            raise Track17Error("Carrier list unavailable") from None
        if not isinstance(carriers, list):
            raise Track17Error("Unexpected carrier list shape")
        return [c for c in carriers if args.query.casefold() in json.dumps(c, ensure_ascii=False).casefold()][:50], 0
    if command == "webhook-server":
        key = token()
        with WebhookServer(("127.0.0.1", args.port), database_path(), key) as server:
            print(json.dumps({"listening": f"http://127.0.0.1:{args.port}", "mode": "authenticated transactional ingestion"}), flush=True)
            server.serve_forever()
        return {}, 0
    if command == "ingest-webhook":
        raw, sign, key = args.file.read_bytes(), args.signature, token()
        parse_webhook(raw, sign, key)
        with closing(connect(database_path())) as conn:
            return ingest_payload(conn, raw, sign, key), 0
    with closing(connect(database_path())) as conn:
        if command == "init":
            return {"database": str(database_path())}, 0
        if command == "list":
            return [dict(row) | {"snapshot": json.loads(row["snapshot"])} for row in conn.execute("SELECT * FROM parcels ORDER BY updated_at DESC")], 0
        if command == "add":
            if not re.fullmatch(r"[A-Za-z0-9-]{5,50}", args.number) or args.carrier < 0:
                raise Track17Error("Invalid tracking number or carrier")
            item = {"number": args.number, "lang": args.lang}
            if args.carrier:
                item["carrier"] = args.carrier
            if args.param:
                item["param"] = args.param
            registered = require_accepted(api("register", [item]))[0]
            resolved = item | registered
            validate_item(resolved)
            with conn:
                apply_item(conn, resolved, label=args.label)
            return {"registered": resolved, "label": args.label}, 0
        if command == "sync":
            rows = list(conn.execute("SELECT * FROM parcels"))
            changes, failures = [], []
            for offset in range(0, len(rows), 40):
                if offset:
                    time.sleep(0.35)
                batch = rows[offset:offset + 40]
                wanted = {(r["number"], r["carrier"]) for r in batch}
                items = [{k: r[k] for k in ("number", "carrier", "param", "lang")} for r in batch]
                good, bad = accepted(api("gettrackinfo", items))
                failures.extend(bad)
                with conn:
                    for item in good:
                        validate_item(item)
                        if identity(item) not in wanted:
                            raise Track17Error("Response contains an unrequested parcel")
                        if apply_item(conn, item):
                            changes.append({"number": item["number"], "carrier": item["carrier"]})
                returned = {identity(item) for item in good}
                if len(good) + len(bad) < len(batch):
                    failures.append({"error": "Incomplete response", "missing": sorted(wanted - returned)})
            return {"changed": changes, "rejected": failures}, int(bool(failures))
        row = conn.execute("SELECT * FROM parcels WHERE number=? AND carrier=?", (args.number, args.carrier)).fetchone()
        if not row:
            raise Track17Error("Parcel not found; use list to resolve number and carrier")
        target = {"number": args.number, "carrier": args.carrier}
        if command == "status":
            if args.refresh:
                item = require_accepted(api("gettrackinfo", [target]))[0]
                validate_item(item)
                if identity(item) != (args.number, args.carrier):
                    raise Track17Error("Response identity mismatch")
                with conn:
                    apply_item(conn, item)
                row = conn.execute("SELECT * FROM parcels WHERE number=? AND carrier=?", (args.number, args.carrier)).fetchone()
            events = [json.loads(e[0]) for e in conn.execute("SELECT event_json FROM parcel_events WHERE number=? AND carrier=?", (args.number, args.carrier))]
            return dict(row) | {"snapshot": json.loads(row["snapshot"]), "events": events}, 0
        if command in {"stop", "retrack"}:
            response = require_accepted(api("stoptrack" if command == "stop" else "retrack", [target]))
            return {"action": command, "accepted": response}, 0
        if command == "remove":
            if args.delete_remote:
                require_accepted(api("deletetrack", [target]))
            with conn:
                conn.execute("DELETE FROM parcels WHERE number=? AND carrier=?", (args.number, args.carrier))
            return {"removed": target, "remote": args.delete_remote}, 0
    raise Track17Error("Unsupported command")


def main() -> int:
    os.umask(0o077)
    try:
        output, status = run(parser().parse_args())
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return status
    except (Track17Error, OSError, sqlite3.Error) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
