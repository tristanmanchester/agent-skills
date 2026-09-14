import importlib.util
from pathlib import Path
import json
import unittest

spec=importlib.util.spec_from_file_location('diversity',Path(__file__).parents[1]/'scripts/diversity_audit.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

class DiversityTests(unittest.TestCase):
    def test_malformed_json_does_not_become_a_prose_idea(self):
        for raw in ['[broken','{"concept":"test"}']:
            with self.assertRaises(ValueError): m.parse_ideas(raw)
    def test_empty_or_nontext_objects_rejected(self):
        for raw in ['[]','[null]','[{"concept":9}]','[""]']:
            with self.assertRaises(ValueError): m.parse_ideas(raw)
    def test_markdown_and_object_inputs(self):
        self.assertEqual(len(m.parse_ideas('- First proposal\n2. Second proposal')),2)
        self.assertEqual(m.parse_ideas('[{"name":"Example","description":"Useful proposal"}]')[0]['concept'],'Useful proposal')
    def test_duplicate_candidates_are_not_novelty_verdicts(self):
        result=m.audit(m.parse_ideas('["Shared equipment insurance pool","Shared equipment insurance pool"]'))
        self.assertEqual(result['candidate_pairs'][0]['jaccard'],1)
        self.assertEqual(result['novelty'],'NOT_ASSESSED')
    def test_names_do_not_inflate_similarity(self):
        result=m.audit(m.parse_ideas('[{"name":"Same name","concept":"Repair bicycles locally"},{"name":"Same name","concept":"Insure shared tools"}]'))
        self.assertEqual(result['candidate_pairs'],[])
    def test_nonenglish_letters_retained(self):
        self.assertIn('münchen',m.tokens('München Werkzeugtausch'))
    def test_bounds_are_explicit(self):
        for raw in [json.dumps(['Idea']*201),json.dumps(['x'*2001]),'x'*(m.MAX_INPUT+1)]:
            with self.assertRaises(ValueError): m.parse_ideas(raw)

if __name__=='__main__': unittest.main()
