import ast
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('scaffold', Path(__file__).parents[1] / 'scripts/scaffold_textual_app.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class ScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name); self.assets = self.root / 'assets'; self.assets.mkdir()
        self.put('app.py', 'class {{CLASS_NAME}}:\n    TITLE = "{{APP_TITLE}}"\n    CSS_PATH = "{{MODULE}}.tcss"\n')
        self.put('tcss', '{{CLASS_NAME}} { height: 1fr; }')
        self.put('test.py', 'from {{MODULE}} import {{CLASS_NAME}}\n')
    def put(self, kind, text):
        (self.assets / f'chat_{kind}.tmpl').write_text(text)
    def plan(self, title='Sample'):
        return m.plan('chat', 'sample', 'SampleApp', title, self.assets)
    def test_titles_are_literals_not_source(self):
        for title in ['A "quoted" title', 'x\npass\n#', '"; print("injected"); x="', '{{LITERAL}}', 'Ünicode \\ title']:
            tree = ast.parse(self.plan(title)['sample.py'])
            cls = tree.body[0]
            self.assertEqual(len(tree.body), 1)
            self.assertEqual(cls.body[0].value.value, title)
    def test_keyword_identifiers_rejected(self):
        for bad in ['class', 'x/y', '../x', 'a.b', 'A;pass']:
            with self.assertRaises(ValueError): m.plan('chat', bad, 'App', 'Title', self.assets)
    def test_preview_has_no_destination_writes(self):
        before = list(self.root.rglob('*')); self.plan()
        self.assertEqual(before, list(self.root.rglob('*')))
    def test_missing_or_bad_template_fails_preflight(self):
        self.put('app.py', 'this is not python !!!')
        with self.assertRaises(SyntaxError): self.plan()
        (self.assets / 'chat_test.py.tmpl').unlink()
        with self.assertRaises(ValueError): self.plan()
    def test_exclusive_destination(self):
        dest = self.root / 'draft'; m.write_plan(self.plan(), dest)
        self.assertTrue((dest / 'sample.py').exists())
        with self.assertRaises(FileExistsError): m.write_plan(self.plan(), dest)
    def test_unknown_placeholders_and_free_text_css_rejected(self):
        self.put('app.py', 'TITLE = "{{SURPRISE}}"')
        with self.assertRaises(ValueError): self.plan()
        self.put('app.py', 'TITLE = "{{APP_TITLE}}"')
        self.put('tcss', '{{APP_TITLE}}')
        with self.assertRaises(ValueError): self.plan()
    def test_symlink_template_rejected(self):
        p = self.assets / 'chat_app.py.tmpl'; p.unlink(); p.symlink_to('/etc/passwd')
        with self.assertRaises(ValueError): self.plan()
    def test_traversal_names_do_not_create_destination(self):
        dest = self.root / 'draft'
        with self.assertRaises(ValueError): m.write_plan({'../bad.py': 'bad'}, dest)
        self.assertFalse(dest.exists())

if __name__ == '__main__': unittest.main()
