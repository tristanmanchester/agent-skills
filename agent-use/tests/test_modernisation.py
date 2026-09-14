import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from generate_agent_assets import generate, render
from validate_skill import validate

class AssetsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.skill = self.root / 'sample'
        self.skill.mkdir()
    def skill_text(self, extra='', description='description: Useful test skill for tests'):
        (self.skill / 'SKILL.md').write_text(f'---\nname: sample\n{description}\n{extra}---\n# Sample\n')
    def test_multiline_yaml(self):
        self.skill_text(description='description: >-\n  Test a multiline\n  description correctly.')
        self.assertTrue(validate(self.skill)['valid'])
    def test_long_multiline_rejected(self):
        self.skill_text(description='description: >-\n  ' + 'x' * 1025)
        self.assertFalse(validate(self.skill)['valid'])
    def test_duplicate_keys_rejected(self):
        self.skill_text(extra='name: other\n')
        self.assertFalse(validate(self.skill)['valid'])
    def test_metadata_values_are_strings(self):
        self.skill_text(extra='metadata:\n  nested: {field: value}\n')
        self.assertFalse(validate(self.skill)['valid'])
    def test_scripts_not_executed_or_compiled_to_disk(self):
        self.skill_text()
        (self.skill / 'test.py').write_text(f'from pathlib import Path\nPath({str(self.root / "EXECUTED")!r}).touch()\n')
        self.assertTrue(validate(self.skill)['valid'])
        self.assertFalse((self.root / 'EXECUTED').exists())
        self.assertFalse((self.skill / '__pycache__').exists())
    def test_missing_link_and_symlink_reported(self):
        self.skill_text()
        with (self.skill / 'SKILL.md').open('a') as stream:
            stream.write('[missing](references/absent.md)\n')
        (self.skill / 'evil.py').symlink_to('/etc/passwd')
        self.assertFalse(validate(self.skill)['valid'])
    def test_preview_never_creates_output(self):
        output = self.root / 'absent-parent' / 'out'
        result = generate(output, 'Test', 'https://test.example', ['a2a'], templates=ROOT/'assets/templates')
        self.assertEqual(result['mode'], 'preview')
        self.assertFalse(output.parent.exists())
    def test_write_is_new_directory_only_and_json_escaped(self):
        output = self.root / 'out'
        generate(output, 'A "quoted" project', 'https://test.example', ['a2a'], write=True, templates=ROOT/'assets/templates')
        card = json.loads((output / 'agent-card.json').read_text())
        self.assertEqual(card['name'], 'A "quoted" project')
        self.assertTrue(json.loads((output / 'manifest.json').read_text())['complete'])
        with self.assertRaises(FileExistsError):
            generate(output, 'Test', 'https://test.example', ['a2a'], write=True, templates=ROOT/'assets/templates')
    def test_invalid_url_or_surface_rejected(self):
        for base in ['http://test.example', 'https://user:pass@test.example', 'https://test.example?q=x']:
            with self.assertRaises(ValueError):
                generate(self.root/'out', 'Test', base, ['a2a'])
        with self.assertRaises(ValueError):
            generate(self.root/'out', 'Test', 'https://test.example', ['all'])
    def test_missing_template_preflight_leaves_no_output(self):
        with self.assertRaises(FileNotFoundError):
            generate(self.root/'out', 'Test', 'https://test.example', ['core'], write=True, templates=self.root/'missing')
        self.assertFalse((self.root/'out').exists())
    def test_a2a_template_regression_shape(self):
        card = json.loads((ROOT/'assets/templates/a2a-agent-card.json').read_text())
        for field in ['name','description','version','supportedInterfaces','capabilities','defaultInputModes','defaultOutputModes','skills']:
            self.assertIn(field, card)
        self.assertIsInstance(card['capabilities'], dict)
        self.assertNotIn('auth', card)
        self.assertNotIn('url', card)
        self.assertEqual(card['supportedInterfaces'][0]['protocolVersion'], '1.0')
        self.assertIn('httpAuthSecurityScheme', card['securitySchemes']['bearerAuth'])
        self.assertIn('bearerAuth', card['securityRequirements'][0]['schemes'])

if __name__ == '__main__':
    unittest.main()
