import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/validate_expo_setup.py'
spec = importlib.util.spec_from_file_location('inventory', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / 'package.json').write_text(json.dumps({'dependencies': {
            'expo': 'workspace:*', 'expo-superwall': '^1.0.0', 'react-native-purchases': 'latest'}}))
    def tearDown(self):
        self.temp.cleanup()
    def test_no_mandatory_old_platform_overrides(self):
        result = m.inspect(self.root)
        self.assertEqual(result['blockers'], [])
        self.assertFalse(result['runtime_verified'])
        self.assertEqual(result['dependencies']['expo']['declared'], 'workspace:*')
        self.assertIsNone(result['dependencies']['expo']['installed'])
    def test_environment_values_never_appear(self):
        (self.root / '.env').write_text('EXPO_PUBLIC_REVENUECAT_IOS_API_KEY=DO_NOT_ECHO\nPRIVATE_SECRET=DO_NOT_ECHO_EITHER')
        output = json.dumps(m.inspect(self.root))
        self.assertNotIn('DO_NOT_ECHO', output)
        self.assertNotIn('PRIVATE_SECRET', output)
        self.assertIn('EXPO_PUBLIC_REVENUECAT_IOS_API_KEY', output)
    def test_regex_occurrences_are_not_reported_as_runtime_passes(self):
        (self.root / 'app.tsx').write_text('// Purchases.configure is not called here')
        result = m.inspect(self.root)
        self.assertEqual(result['source_occurrences_not_execution_proof']['Purchases.configure'], ['app.tsx'])
        self.assertFalse(result['runtime_verified'])
    def test_dynamic_configuration_not_executed_or_hidden_by_app_json(self):
        (self.root / 'app.json').write_text('{"expo":{}}')
        (self.root / 'app.config.ts').write_text('throw new Error("DO_NOT_EXECUTE")')
        self.assertEqual(m.inspect(self.root)['config_files'], ['app.json', 'app.config.ts'])
    def test_missing_required_dependency_is_nonzero(self):
        (self.root / 'package.json').write_text('{"dependencies":{"expo":"^55"}}')
        run = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 1)
        self.assertEqual(len(json.loads(run.stdout)['blockers']), 2)
    def test_invalid_project_fails_without_dumping_content(self):
        (self.root / 'package.json').write_text('{SECRET_DO_NOT_ECHO')
        run = subprocess.run([sys.executable, str(SCRIPT), '--project-root', str(self.root)], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2)
        self.assertEqual(run.stdout, '')
        self.assertNotIn('SECRET_DO_NOT_ECHO', run.stderr)

if __name__ == '__main__':
    unittest.main()
