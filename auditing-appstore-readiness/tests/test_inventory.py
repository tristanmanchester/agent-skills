import importlib.util
import json
from pathlib import Path
import plistlib
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('inventory', Path(__file__).parents[1] / 'scripts/inspect_repo.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
    def write(self, path, value):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(value if isinstance(value, bytes) else value.encode())
        return target
    def run_inventory(self, **kwargs):
        return module.inventory(self.root, **kwargs)
    def test_empty_is_not_submission_ready(self):
        result = self.run_inventory()
        self.assertEqual(result['submission_readiness'], 'NOT_ASSESSED')
        self.assertEqual(result['plists'], [])
        self.assertNotIn('verdict', result)
    def test_modern_universal_icon_arbitrary_name(self):
        self.write('Brand.appiconset/icon.png', b'fixture')
        self.write('Brand.appiconset/Contents.json', json.dumps({'images':[{'idiom':'universal','platform':'ios','size':'1024x1024','filename':'icon.png'}]}))
        icon = self.run_inventory()['icons'][0]
        self.assertEqual(icon['entries'][0]['file']['state'], 'exists')
        self.assertEqual(icon['compiled_validity'], 'NOT_ASSESSED')
    def test_icon_composer_directory(self):
        (self.root / 'Brand.icon').mkdir()
        self.assertEqual(self.run_inventory()['icons'][0]['kind'], 'icon-composer')
    def test_binary_plist_ats_and_generated_values(self):
        self.write('Info.plist', plistlib.dumps({'CFBundleIdentifier':'$(PRODUCT_BUNDLE_IDENTIFIER)', 'NSAppTransportSecurity':{'NSAllowsArbitraryLoads':True}, 'UILaunchScreen':{}}, fmt=plistlib.FMT_BINARY))
        item = self.run_inventory()['plists'][0]
        self.assertTrue(item['arbitrary_loads'])
        self.assertTrue(item['declarative_launch_screen'])
        self.assertFalse(item['resolved'])
    def test_dynamic_config_is_not_executed(self):
        self.write('app.config.js', "require('fs').writeFileSync('EXECUTED', 'bad'); throw Error('bad')")
        self.assertEqual(self.run_inventory()['dynamic_configs'], ['app.config.js'])
        self.assertFalse((self.root / 'EXECUTED').exists())
    def test_symlinks_skipped_and_partial(self):
        (self.root / 'Info.plist').symlink_to('/etc/passwd')
        result = self.run_inventory()
        self.assertEqual(result['plists'], [])
        self.assertFalse(result['coverage']['complete_within_scope'])
    def test_malformed_metadata_reported(self):
        self.write('Info.plist', b'not plist')
        result = self.run_inventory()
        self.assertTrue(result['issues'])
        self.assertFalse(result['coverage']['complete_within_scope'])
    def test_malformed_xml_reported(self):
        self.write('Info.plist', b'<?xml version="1.0"?><plist><dict><key>bad</key></plist>')
        self.assertTrue(self.run_inventory()['issues'])
    def test_entry_limit_reported(self):
        self.write('a', 'x'); self.write('b', 'x')
        self.assertFalse(self.run_inventory(max_entries=1)['coverage']['complete_within_scope'])
    def test_native_project_directories_detected(self):
        self.write('ios/A.xcodeproj/project.pbxproj', '// fixture')
        self.write('ios/B.xcodeproj/project.pbxproj', '// fixture')
        self.assertEqual(len(self.run_inventory()['projects']), 2)
        self.assertNotIn('bestProject', self.run_inventory())
    def test_expo_appearance_icon_object(self):
        self.write('assets/light.png', b'fixture')
        self.write('app.json', json.dumps({'expo':{'ios':{'icon':{'light':'./assets/light.png','dark':'missing.png'}}}}))
        icons = self.run_inventory()['expo_configs'][0]['icon_references']
        self.assertEqual(icons['light']['state'], 'exists')
        self.assertEqual(icons['dark']['state'], 'missing')
    def test_remote_expo_icon_is_not_a_missing_local_file(self):
        self.write('app.json', json.dumps({'expo':{'icon':'https://example.com/icon.png'}}))
        entry = self.run_inventory()['expo_configs'][0]['icon_references']['default']
        self.assertEqual(entry['state'], 'remote-not-fetched')
    def test_oversized_metadata(self):
        self.write('package.json', b' ' * (module.MAX_BYTES + 1))
        self.assertTrue(self.run_inventory()['issues'])
    def test_external_asset_is_not_read(self):
        self.write('App.appiconset/Contents.json', json.dumps({'images':[{'filename':'/etc/passwd'}]}))
        self.assertEqual(self.run_inventory()['icons'][0]['entries'][0]['file']['state'], 'outside-scope')

if __name__ == '__main__':
    unittest.main()
