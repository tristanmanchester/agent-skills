import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).parents[1] / 'scripts/nature_preflight.py'
spec = importlib.util.spec_from_file_location('preflight', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
NC = m.PROFILES['nature-communications-article']

def draft(n):
    return '# Title\n\n## Abstract\n' + ' '.join(['word'] * n) + '\n\n## Introduction\nNot part of the abstract.'

class PreflightTests(unittest.TestCase):
    def test_225_word_ncomms_fails_limit(self):
        self.assertEqual(m.check(draft(225), NC)['status'], 'over-limit')
    def test_200_201_boundary(self):
        self.assertEqual(m.check(draft(200), NC)['status'], 'within-configured-limit')
        self.assertEqual(m.check(draft(201), NC)['status'], 'over-limit')
    def test_nature_guidance_is_not_hard_limit(self):
        result = m.check(' '.join(['word'] * 225), m.PROFILES['nature-article'], True)
        self.assertEqual(result['status'], 'over-guidance')
    def test_missing_or_duplicate_heading_not_guessed(self):
        for text in ['A long first paragraph is not a labelled abstract.', draft(20) + '\n## Abstract\nAgain']:
            with self.assertRaises(ValueError): m.check(text, NC)
    def test_any_peer_heading_ends_abstract(self):
        result = m.check(draft(20).replace('Introduction', 'Unexpected section'), NC)
        self.assertEqual(result['word_count'], 20)
    def test_fenced_heading_not_treated_as_abstract(self):
        with self.assertRaises(ValueError): m.check('```md\n## Abstract\nFake\n```', NC)
    def test_nested_and_unclosed_fences_fail(self):
        for text in ['## Abstract\nOne\n### Subheading\nTwo', '## Abstract\n```\nOne']:
            with self.assertRaises(ValueError): m.check(text, NC)
    def test_no_submission_or_citation_pass_claim(self):
        result = m.check(draft(20), NC)
        self.assertEqual(result['submission_readiness'], 'NOT_ASSESSED')
        self.assertFalse(result['citation_policy_checked'])
    def test_invalid_custom_profiles(self):
        for profile in [{}, {**NC, 'max_words': True}, {**NC, 'source_url': 'http://example.org'}, {**NC, 'reviewed':'yesterday'}]:
            with self.assertRaises(ValueError): m.validate_profile(profile)
    def test_cli_nonzero_on_limit_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'draft.md'; path.write_text(draft(225))
            result = subprocess.run([sys.executable, str(SCRIPT), '--input', str(path), '--profile', 'nature-communications-article'], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['word_count'], 225)

if __name__ == '__main__': unittest.main()
