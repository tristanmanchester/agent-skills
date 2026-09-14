import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock,patch
from test_exports import o,response

class OCRReviewTests(unittest.TestCase):
    def test_all_valid_json_annotation_scalars_are_exported(self):
        for annotation in ['"hello"','""','0','false','null','[]']:
            with self.subTest(annotation=annotation),tempfile.TemporaryDirectory() as d:
                out=Path(d)/'out';fixture=response();fixture['document_annotation']=annotation
                o.write_outputs(out,fixture)
                self.assertEqual(json.loads((out/'document_annotation.json').read_text()),json.loads(annotation))
                self.assertFalse((out/'document_annotation.txt').exists())
    def test_non_json_annotation_stays_text(self):
        with tempfile.TemporaryDirectory() as d:
            fixture=response();fixture['document_annotation']='plain prose'
            out=Path(d)/'out';o.write_outputs(out,fixture)
            self.assertEqual((out/'document_annotation.txt').read_text(),'plain prose')
    def test_invalid_destination_parent_precedes_upload_and_ocr(self):
        with tempfile.TemporaryDirectory() as d:
            parent=Path(d)/'not-a-directory';parent.write_text('keep')
            source=Path(d)/'input.pdf';source.write_bytes(b'%PDF-test')
            args=o.build_arg_parser().parse_args(['--input',str(source),'--out',str(parent/'out')])
            client=SimpleNamespace(files=Mock(),ocr=Mock())
            with self.assertRaises(OSError):o.execute(client,args)
            client.files.upload.assert_not_called();client.ocr.process.assert_not_called()
            self.assertEqual(parent.read_text(),'keep')
    def test_unwritable_staging_precedes_remote_work(self):
        with tempfile.TemporaryDirectory() as d:
            args=o.build_arg_parser().parse_args(['--url','https://example.test/test.pdf','--out',str(Path(d)/'out')])
            client=SimpleNamespace(files=Mock(),ocr=Mock())
            with patch.object(o.tempfile,'TemporaryDirectory',side_effect=PermissionError('synthetic')):
                with self.assertRaises(PermissionError):o.execute(client,args)
            client.files.upload.assert_not_called();client.ocr.process.assert_not_called()
    def test_staging_exists_during_processing_and_disappears_on_failure(self):
        with tempfile.TemporaryDirectory() as d:
            args=o.build_arg_parser().parse_args(['--url','https://example.test/test.pdf','--out',str(Path(d)/'out')])
            def fail(**kwargs):
                self.assertEqual(len(list(Path(d).glob('.mistral-ocr-*'))),1)
                raise RuntimeError('synthetic')
            client=SimpleNamespace(files=Mock(),ocr=Mock());client.ocr.process.side_effect=fail
            with self.assertRaises(RuntimeError):o.execute(client,args)
            self.assertEqual(list(Path(d).iterdir()),[])
