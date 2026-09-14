import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/render_report.py'
spec = importlib.util.spec_from_file_location('review_renderer', SCRIPT)
m = importlib.util.module_from_spec(spec); sys.modules[spec.name] = m; spec.loader.exec_module(m)

class CaptureReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.capture_dir = self.root/'captures'; self.capture_dir.mkdir()
    def capture(self, stem, text, code='0'):
        p = self.capture_dir/(stem+'.txt'); p.write_text('$ command\n'+text)
        if code is not None: p.with_suffix('.exit-code').write_text(code)
        return p
    def render(self):
        out = self.root/'report.md'
        r = subprocess.run([sys.executable, str(SCRIPT), '--input', str(self.capture_dir), '--output', str(out)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        return out
    def test_failed_or_unknown_status_is_not_configuration(self):
        for status in ['1','127','bad','256',None]:
            p = self.capture('openclaw_config_tools_profile','"stderr-as-config"', status)
            if status is None: p.with_suffix('.exit-code').unlink(missing_ok=True)
            self.assertIsNone(m.load_capture(p))
            self.assertIsNone(m.read_config_value(self.capture_dir,'openclaw_config_tools_profile'))
            self.assertIn('unverified',dict(m.build_environment_rows(self.capture_dir))['Tools profile'])
    def test_failed_valid_json_is_not_a_clean_audit(self):
        self.capture('openclaw_security_audit_json','{"findings":[]}', '1')
        out=self.render().read_text()
        self.assertIn('Unverified',out); self.assertIn('failed (exit 1)',out)
        self.assertNotIn('**Overall risk rating:** No parsed findings',out)
    def test_successful_but_wrong_json_shape_is_missing_evidence(self):
        self.capture('openclaw_security_audit_json','{"error":"provider failed"}')
        self.assertIn('unsupported audit JSON', self.render().read_text())
    def test_successful_captures_still_render_findings(self):
        for stem in ('openclaw_security_audit_json','openclaw_security_audit_deep_json'):
            self.capture(stem,json.dumps({'findings':[{'checkId':'test','severity':'high','title':'Synthetic finding'}]}))
        self.assertIn('**Overall risk rating:** High',self.render().read_text())
    @unittest.skipIf(os.name != 'posix','POSIX file modes')
    def test_report_is_private_under_permissive_umask(self):
        mask=os.umask(0o022)
        try: out=self.render()
        finally: os.umask(mask)
        self.assertEqual(out.stat().st_mode & 0o777,0o600)
    def test_existing_output_is_not_overwritten(self):
        out=self.root/'report.md';out.write_text('keep')
        r=subprocess.run([sys.executable,str(SCRIPT),'--input',str(self.capture_dir),'--output',str(out)],capture_output=True)
        self.assertNotEqual(r.returncode,0);self.assertEqual(out.read_text(),'keep')
