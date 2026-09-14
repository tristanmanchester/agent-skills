import importlib.util
from contextlib import closing
import hashlib
import http.client
import json
from pathlib import Path
import sqlite3
import tempfile
import threading
import unittest
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location("track17", Path(__file__).resolve().parents[1] / "scripts" / "track17.py")
t = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(t)
KEY = "a! not a production key"


def message(status="InTransit", time="2026-09-13T10:00:00Z"):
    return {"event": "TRACKING_UPDATED", "data": {"number": "RR123456789CN", "carrier": 3011,
        "track_info": {"latest_status": {"status": status}, "latest_event": {"time_utc": time},
                       "tracking": {"providers": []}}}}


def encode(value):
    return json.dumps(value, ensure_ascii=False).encode()


class IngestionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "test.sqlite3"
        self.conn = t.connect(self.path)
        self.raw = encode(message())

    def tearDown(self):
        self.conn.close()
        self.temp.cleanup()

    def snapshot(self):
        return "\n".join(self.conn.iterdump())

    def test_signature_uses_exact_bytes_and_api_key(self):
        raw = b'{"unicode": "\\u00e9", "space": 1}'
        self.assertEqual(t.signature(raw, KEY), hashlib.sha256(raw + b"/" + KEY.encode()).hexdigest())
        t.verify_signature(raw, t.signature(raw, KEY).upper(), KEY)
        with self.assertRaises(t.AuthenticationError):
            t.verify_signature(raw + b" ", t.signature(raw, KEY), KEY)

    def test_unauthenticated_requests_change_no_tables(self):
        t.ingest_payload(self.conn, self.raw, t.signature(self.raw, KEY), KEY)
        before = self.snapshot()
        for key, sign, raw in [(None, None, self.raw), (KEY, None, self.raw), (KEY, "0" * 64, self.raw),
                               (KEY, "not-hex", self.raw), ("wrong", t.signature(self.raw, KEY), self.raw),
                               (KEY, t.signature(self.raw, KEY), self.raw + b" ")]:
            with self.subTest(key=key, sign=sign), self.assertRaises(t.AuthenticationError):
                t.ingest_payload(self.conn, raw, sign, key)
            self.assertEqual(before, self.snapshot())

    def test_duplicate_does_not_reapply_or_change_timestamps(self):
        self.assertTrue(t.ingest_payload(self.conn, self.raw, t.signature(self.raw, KEY), KEY)["changed"])
        before = self.snapshot()
        self.assertEqual(t.ingest_payload(self.conn, self.raw, t.signature(self.raw, KEY), KEY), {"duplicate": True, "changed": False})
        self.assertEqual(before, self.snapshot())

    def test_malformed_authenticated_event_rolls_back(self):
        payload = message()
        payload["data"]["track_info"]["tracking"]["providers"] = [{"events": [42]}]
        raw = encode(payload)
        before = self.snapshot()
        with self.assertRaises(t.Track17Error):
            t.ingest_payload(self.conn, raw, t.signature(raw, KEY), KEY)
        self.assertEqual(before, self.snapshot())

    def test_stale_signed_delivery_cannot_regress_snapshot(self):
        latest = encode(message("Delivered", "2026-09-13T10:00:00Z"))
        older = encode(message("InTransit", "2026-09-12T10:00:00Z"))
        t.ingest_payload(self.conn, latest, t.signature(latest, KEY), KEY)
        self.assertFalse(t.ingest_payload(self.conn, older, t.signature(older, KEY), KEY)["changed"])
        stored = json.loads(self.conn.execute("SELECT snapshot FROM parcels").fetchone()[0])
        self.assertEqual(stored["track_info"]["latest_status"]["status"], "Delivered")

    def test_invalid_payload_shape_and_identity(self):
        for payload in ([1], {"event": "OTHER", "data": {}}, {"event": "TRACKING_UPDATED", "data": {"number": "", "carrier": 1}}):
            raw = encode(payload)
            with self.assertRaises(t.Track17Error):
                t.ingest_payload(self.conn, raw, t.signature(raw, KEY), KEY)
        self.assertEqual(self.conn.execute("SELECT count(*) FROM receipts").fetchone()[0], 0)

    def test_remote_rejection_and_empty_acceptance_are_failures(self):
        for response in ({"data": {"accepted": []}}, {"data": {"errors": [{"code": -1}]}},
                         {"data": {"accepted": [{}], "rejected": [{}]}}):
            with self.assertRaises(t.Track17Error):
                t.require_accepted(response)

    def test_existing_database_is_never_silently_replaced(self):
        old = Path(self.temp.name) / "legacy.sqlite3"
        with closing(sqlite3.connect(old)) as conn:
            conn.execute("CREATE TABLE packages(id INTEGER)")
            conn.commit()
        with self.assertRaises(t.Track17Error):
            t.connect(old)
        with closing(sqlite3.connect(old)) as conn:
            self.assertEqual(conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall(), [("packages",)])

    def test_http_authentication_and_commit_before_acknowledgement(self):
        server = t.WebhookServer(("127.0.0.1", 0), self.path, KEY)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for headers, expected in [({}, 401), ({"sign": "0" * 64}, 401), ({"sign": t.signature(self.raw, KEY)}, 200)]:
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                conn.request("POST", "/", body=self.raw, headers=headers)
                response = conn.getresponse()
                self.assertEqual(response.status, expected)
                response.read()
                conn.close()
            self.assertEqual(self.conn.execute("SELECT count(*) FROM receipts").fetchone()[0], 1)
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_http_storage_failure_is_not_success(self):
        server = t.WebhookServer(("127.0.0.1", 0), self.path, KEY)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(t, "connect", side_effect=sqlite3.OperationalError("synthetic")):
                conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=3)
                conn.request("POST", "/", body=self.raw, headers={"sign": t.signature(self.raw, KEY)})
                response = conn.getresponse()
                self.assertEqual(response.status, 503)
                response.read()
                conn.close()
        finally:
            server.shutdown()
            server.server_close()
            thread.join()


if __name__ == "__main__":
    unittest.main()
