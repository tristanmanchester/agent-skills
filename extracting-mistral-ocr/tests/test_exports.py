import base64
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

SPEC = importlib.util.spec_from_file_location("ocr_extract", Path(__file__).resolve().parents[1] / "scripts" / "mistral_ocr_extract.py")
o = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = o
SPEC.loader.exec_module(o)


def response():
    return {"model": "fixture-model", "pages": [{"index": 0, "markdown": "![figure](img-0.png)\n[table](tbl-0.html)",
        "images": [{"id": "img-0.png", "image_base64": base64.b64encode(b"image-fixture").decode()}],
        "tables": [{"id": "tbl-0.html", "format": "html", "content": "<table><tr><td>42</td></tr></table>"}]}],
        "document_annotation": '{"total":42}'}


class ExportTests(unittest.TestCase):
    def test_page_selection(self):
        self.assertEqual(o.parse_pages_spec("0,2-4,2"), [0, 2, 3, 4])
        for value in ("", "1,", "3-1", "-1", "0-999999999"):
            with self.assertRaises(o.CLIError):
                o.parse_pages_spec(value)

    def test_assets_and_relative_links_and_annotations(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "export"
            o.write_outputs(out, response())
            self.assertIn("](images/page-000-img-0.png)", (out / "combined.md").read_text())
            self.assertIn("](../tables/page-000-tbl-0.html)", (out / "pages/page-000.md").read_text())
            self.assertEqual((out / "images/page-000-img-0.png").read_bytes(), b"image-fixture")
            self.assertEqual(json.loads((out / "document_annotation.json").read_text()), {"total": 42})
            self.assertEqual(json.loads((out / "raw_response.json").read_text()), response())

    def test_untrusted_asset_paths_leave_no_published_output(self):
        for identifier in ("../secret", "/tmp/x", "C:\\x", "a/b", "a\\b", ".", "..", "x\x00.png"):
            with self.subTest(identifier=identifier), tempfile.TemporaryDirectory() as directory:
                out = Path(directory) / "export"
                fixture = response()
                fixture["pages"][0]["images"][0]["id"] = identifier
                with self.assertRaises(o.CLIError):
                    o.write_outputs(out, fixture)
                self.assertFalse(out.exists())
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory) / "export"
            out.mkdir()
            (out / "keep").write_text("existing")
            with self.assertRaises(o.CLIError):
                o.write_outputs(out, response())
            self.assertEqual((out / "keep").read_text(), "existing")

    def test_upload_closed_and_cleanup_after_ocr_failure(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "input.pdf"
            path.write_bytes(b"%PDF-fixture")
            args = o.build_arg_parser().parse_args(["--input", str(path), "--out", str(Path(directory) / "out")])
            client = SimpleNamespace(files=Mock(), ocr=Mock())
            client.files.upload.return_value = SimpleNamespace(id="uploaded-fixture")
            client.ocr.process.side_effect = RuntimeError("synthetic OCR failure")
            with self.assertRaises(RuntimeError):
                o.execute(client, args)
            upload_args = client.files.upload.call_args.kwargs
            self.assertTrue(upload_args["file"]["content"].closed)
            self.assertEqual(client.ocr.process.call_args.kwargs["document"], {"type": "file", "file_id": "uploaded-fixture"})
            client.files.delete.assert_called_once_with(file_id="uploaded-fixture")

    def test_annotation_requires_json_schema_and_block_confidence_requires_blocks(self):
        with tempfile.TemporaryDirectory() as directory:
            schema = Path(directory) / "schema.json"
            schema.write_text('{"type":"object","properties":{},"additionalProperties":false}')
            args = o.build_arg_parser().parse_args(["--url", "https://example.test/a.pdf?x=1", "--out", "out", "--annotation-schema", str(schema), "--annotation-prompt", "Extract fields"])
            options = o.request_options(args)
            self.assertEqual(options["document_annotation_format"]["type"], "json_schema")
            self.assertIn("schema_definition", options["document_annotation_format"]["json_schema"])
            args.annotation_schema = None
            with self.assertRaises(o.CLIError):
                o.request_options(args)
            args.annotation_prompt, args.confidence = None, "block"
            with self.assertRaises(o.CLIError):
                o.request_options(args)

    def test_url_type_is_explicit_not_guessed_from_query_string(self):
        args = o.build_arg_parser().parse_args(["--url", "https://example.test/file.pdf?token=signed", "--out", "out"])
        self.assertEqual(o.prepare_source(None, args).payload["type"], "document_url")
        args.url = "https://user:secret@example.test/a.pdf"
        with self.assertRaises(o.CLIError):
            o.prepare_source(None, args)

    def test_filename_collision_is_rejected(self):
        fixture = response()
        fixture["pages"][0]["tables"] = [{"id": name, "format": "markdown", "content": "x"} for name in ("same", "same.md")]
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(o.CLIError):
                o.write_outputs(Path(directory) / "out", fixture)


if __name__ == "__main__":
    unittest.main()
