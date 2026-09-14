import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest
from urllib.parse import parse_qs, urlsplit

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "redact_openclaw_config.py"
spec = importlib.util.spec_from_file_location("redactor", SCRIPT)
redactor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(redactor)


class RedactionTests(unittest.TestCase):
    def test_sensitive_keys_mask_every_value(self):
        for key in ("password", "apiKey", "access_token", "client-secret", "Authorization", "cookie", "private_key"):
            for value in ("abc", "p@ss! with spaces", "", 1234, None, {"nested": "s"}, ["s"]):
                with self.subTest(key=key, value=value):
                    self.assertEqual(redactor.redact_obj({key: value})[key], redactor.REDACTED)

    def test_nested_arrays_and_non_secret_settings(self):
        data = {"gateway": {"auth": {"mode": "token", "token": "x"}}, "accounts": [{"password": "x"}], "port": 18789}
        out = redactor.redact_obj(data)
        self.assertEqual(out["gateway"]["auth"]["mode"], "token")
        self.assertEqual(out["gateway"]["auth"]["token"], redactor.REDACTED)
        self.assertEqual(out["accounts"][0]["password"], redactor.REDACTED)
        self.assertEqual(out["port"], 18789)

    def test_urls(self):
        out = redactor.redact_string("https://bob:p%40ss@example.test/a?access%5Ftoken=abc&key=x&sig=y&page=2#secret")
        parts = urlsplit(out)
        self.assertEqual(parts.netloc, "REDACTED@example.test")
        self.assertEqual(parts.fragment, "REDACTED")
        self.assertEqual(parse_qs(parts.query), {"access_token": [redactor.REDACTED], "key": [redactor.REDACTED], "sig": [redactor.REDACTED], "page": ["2"]})

    def test_no_partial_secret_disclosure(self):
        for value in ("a" * 40, "eyJhbGci.eyJ1c2Vy.signature", "-----BEGIN PRIVATE KEY-----\nabc\n-----END PRIVATE KEY-----"):
            self.assertEqual(redactor.redact_string(value), redactor.REDACTED)

    def test_invalid_input_fails_without_echoing_source(self):
        for raw in ('{"password": "DO_NOT_ECHO"', "not JSON DO_NOT_ECHO", '"DO_NOT_ECHO"', '{"port": NaN}'):
            result = subprocess.run([sys.executable, str(SCRIPT), "-"], input=raw, capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout, "")
            self.assertNotIn("DO_NOT_ECHO", result.stderr)

    def test_cli_json(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "-"], input='{"password":"a!","port":18789}', capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), {"password": redactor.REDACTED, "port": 18789})


if __name__ == "__main__":
    unittest.main()
