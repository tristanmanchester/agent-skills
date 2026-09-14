import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
spec = importlib.util.spec_from_file_location('env_report', Path(__file__).parents[1] / 'scripts/jax_env_report.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class EnvironmentTests(unittest.TestCase):
    def test_secret_values_not_emitted(self):
        with patch.dict('os.environ', {'JAX_TEST_TOKEN':'not-for-the-report', 'XLA_TEST_PATH':'/private/test-path'}):
            report = module.build_report()
        self.assertNotIn('not-for-the-report', json.dumps(report))
        self.assertNotIn('/private/test-path', json.dumps(report))
        self.assertIn('JAX_TEST_TOKEN', report['environment_names_only'])
    def test_cpu_smoke(self):
        report = module.build_report(True)
        self.assertTrue(report['ok'])
        self.assertTrue(report['smoke_test']['ok'])

if __name__ == '__main__': unittest.main()
