import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).parents[1]/'scripts'))
from validate_skill import validate

class ValidationReviewTests(unittest.TestCase):
    def test_real_package_self_validates(self):
        result=validate(Path(__file__).parents[1]);self.assertTrue(result['valid'],result['errors'])
    def test_literal_links_are_ignored_but_real_broken_links_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'sample';root.mkdir()
            f=root/'SKILL.md';header='---\nname: sample\ndescription: Test skill\n---\n'
            f.write_text(header+'````text\n[old](references/absent.md)\n```\n````\n`[old](absent.md)`\n')
            self.assertTrue(validate(root)['valid'])
            f.write_text(f.read_text()+'[broken](absent.md)\n')
            self.assertFalse(validate(root)['valid'])
    def test_wrapper_writes_no_bytecode_without_environment_flag(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)/'sample';root.mkdir();scripts=Path(d)/'scripts';scripts.mkdir()
            (root/'SKILL.md').write_text('---\nname: sample\ndescription: Test skill\n---\n')
            for name in ['validate_agent_assets.py','validate_skill.py']:
                shutil.copyfile(Path(__file__).parents[1]/'scripts'/name,scripts/name)
            env=dict(os.environ);env.pop('PYTHONDONTWRITEBYTECODE',None);env.pop('PYTHONPYCACHEPREFIX',None)
            result=subprocess.run([sys.executable,str(scripts/'validate_agent_assets.py'),'--skill-dir',str(root)],env=env,capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr);self.assertTrue(json.loads(result.stdout)['valid'])
            self.assertFalse(list(Path(d).rglob('*.pyc')))
