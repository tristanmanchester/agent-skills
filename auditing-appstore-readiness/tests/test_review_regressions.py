import plistlib
from test_inventory import module

# Separate cases reuse only fixture helpers, not the original TestCase (no duplicated tests).
import tempfile
from pathlib import Path
import unittest
class InventoryReviewTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.root=Path(self.tmp.name)
    def write(self,path,value):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(value)
    def test_named_and_arbitrary_plists_are_unresolved_candidates(self):
        for name in ['MyApp-Info.plist','Config/ReleaseMetadata.plist']:
            self.write(name,plistlib.dumps({'CFBundleIdentifier':'test.app','NSCameraUsageDescription':'Camera'}))
        items=module.inventory(self.root)['plists'];self.assertEqual(len(items),2)
        self.assertTrue(all(not x['resolved'] and x['target_membership']=='NOT_ASSESSED' for x in items))
    def test_swiftpm_build_tree_does_not_consume_budget(self):
        for i in range(20):self.write('.build/'+str(i)+'/Info.plist',b'invalid')
        self.write('App-Info.plist',plistlib.dumps({'CFBundleIdentifier':'test.app'}))
        report=module.inventory(self.root,max_entries=3)
        self.assertTrue(report['coverage']['complete_within_scope']);self.assertEqual(len(report['plists']),1)
    def test_main_and_arbitrary_views_are_not_launch_assets(self):
        self.write('Main.storyboard',b'');self.write('Detail.xib',b'')
        report=module.inventory(self.root)
        self.assertEqual(report['launch_assets'],[]);self.assertEqual(len(report['interface_assets']),2)
    def test_named_and_referenced_launch_candidates(self):
        self.write('Main.storyboard',b'');self.write('LaunchScreen.storyboard',b'')
        self.write('Brand.storyboard',b'')
        self.write('Release.plist',plistlib.dumps({'UILaunchStoryboardName':'Brand'}))
        self.assertEqual(set(module.inventory(self.root)['launch_assets']),{'Brand.storyboard','LaunchScreen.storyboard'})
    def test_non_dictionary_resource_plist_is_not_malformed_info(self):
        self.write('Resources.plist',plistlib.dumps(['one','two']))
        report=module.inventory(self.root)
        self.assertEqual(report['plists'],[]);self.assertEqual(report['other_plists'],['Resources.plist'])
        self.assertFalse(report['issues'])
