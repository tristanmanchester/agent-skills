import importlib.util
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

spec=importlib.util.spec_from_file_location('renderer',Path(__file__).parents[1]/'scripts/render_chart_svg.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
NS={'s':'http://www.w3.org/2000/svg'}
class RendererTests(unittest.TestCase):
    def render(self,rows,chart='scatter',**kw):
        svg,meta=m.render(rows,x='x',y='y',chart=chart,**kw)
        return ET.fromstring(svg),meta
    def test_scatter_range_uses_raw_observations(self):
        root,meta=self.render([{'x':'1','y':'0'},{'x':'1','y':'100'}])
        self.assertLessEqual(meta['y_domain'][0],0); self.assertGreaterEqual(meta['y_domain'][1],100)
        self.assertEqual(meta['points_rendered'],2); self.assertEqual(len(root.findall('s:circle',NS)),2)
    def test_dates_have_proportional_spacing(self):
        root,_=self.render([{'x':'2026-01-01','y':'1'},{'x':'2026-01-02','y':'2'},{'x':'2026-01-11','y':'3'}],chart='line',x_type='date')
        xs=[float(c.attrib['cx']) for c in root.findall('s:circle',NS)]
        self.assertAlmostEqual((xs[2]-xs[1])/(xs[1]-xs[0]),9,places=4)
    def test_numeric_line_not_lexicographic(self):
        root,_=self.render([{'x':'10','y':'1'},{'x':'2','y':'2'},{'x':'1','y':'3'}],chart='line')
        xs=[float(c.attrib['cx']) for c in root.findall('s:circle',NS)]
        self.assertEqual(xs,sorted(xs))
    def test_missing_line_value_breaks_path(self):
        root,meta=self.render([{'x':'1','y':'1'},{'x':'2','y':''},{'x':'3','y':'3'}],chart='line')
        self.assertEqual(len(root.findall('s:path',NS)),2); self.assertEqual(meta['missing_line_values'],1)
        self.assertTrue(all('L' not in p.attrib['d'] for p in root.findall('s:path',NS)))
    def test_bar_never_implicitly_averages(self):
        with self.assertRaises(ValueError): self.render([{'x':'A','y':'1'},{'x':'A','y':'3'}],chart='bar')
    def test_zero_bar_has_zero_height(self):
        root,meta=self.render([{'x':'A','y':'0'}],chart='bar')
        bars=root.findall('s:rect',NS)[1:]
        self.assertEqual(float(bars[0].attrib['height']),0)
        self.assertEqual(meta['aggregation'],'none')
    def test_nan_infinity_and_locale_ambiguity_rejected(self):
        for value in ['nan','inf','-inf','1,2']:
            with self.assertRaises(ValueError): self.render([{'x':'1','y':value}])
    def test_labels_escaped_and_accessible_title(self):
        root,_=self.render([{'x':'<A>','y':'1'}],chart='bar',title='<script>bad</script>')
        self.assertEqual(root.attrib['role'],'img'); self.assertEqual(root.find('s:title',NS).text,'<script>bad</script>')
        self.assertEqual(root.findall('s:script',NS),[])
    def test_categories_preserve_input_order(self):
        _,meta=self.render([{'x':'B','y':'1'},{'x':'A','y':'2'}],chart='dot')
        self.assertEqual(meta['category_order'],['B','A'])
    def test_duplicate_line_coordinate_and_invalid_dimensions_rejected(self):
        with self.assertRaises(ValueError): self.render([{'x':'1','y':'1'},{'x':'1.0','y':'2'}],chart='line')
        with self.assertRaises(ValueError): self.render([{'x':'1','y':'1'}],width=-1)
    def test_cli_will_not_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp); (p/'input.csv').write_text('x,y\n1,2\n'); (p/'out.svg').write_text('keep')
            status=m.main(['--csv',str(p/'input.csv'),'--x','x','--y','y','--chart','scatter','--output',str(p/'out.svg')])
            self.assertEqual(status,1); self.assertEqual((p/'out.svg').read_text(),'keep')
    def test_missing_scatter_value_rejected(self):
        with self.assertRaises(ValueError): self.render([{'x':'1','y':''}])
    def test_small_variation_on_large_offset_keeps_distinct_tick_labels(self):
        root,_=self.render([{'x':'1','y':'10000000000'},{'x':'2','y':'10000000001'}])
        labels=[node.text for node in root.findall('s:text',NS) if node.attrib['text-anchor']=='end']
        self.assertEqual(len(set(labels)),5)
    def test_large_finite_domain_does_not_overflow_ticks(self):
        root,_=self.render([{'x':'0','y':'0'},{'x':'1e308','y':'1e308'}])
        text=ET.tostring(root,encoding='unicode')
        self.assertNotIn('inf',text.lower()); self.assertNotIn('nan',text.lower())
if __name__=='__main__': unittest.main()
