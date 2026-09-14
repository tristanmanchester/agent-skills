import json
import unittest
from unittest.mock import patch
from test_env import module

class EnvironmentReviewTests(unittest.TestCase):
    def test_nvidia_names_without_values(self):
        with patch.dict('os.environ',{'NVIDIA_VISIBLE_DEVICES':'secret-device-set'}):
            report=module.build_report()
        self.assertIn('NVIDIA_VISIBLE_DEVICES',report['environment_names_only'])
        self.assertNotIn('secret-device-set',json.dumps(report))
    def test_unreadable_package_metadata_is_structured_and_not_ok(self):
        with patch.object(module.importlib.metadata,'version',side_effect=PermissionError('private-message')):
            report=module.build_report()
        self.assertFalse(report['ok']);self.assertEqual(report['package_errors']['jax'],'PermissionError')
        self.assertNotIn('private-message',json.dumps(report))
