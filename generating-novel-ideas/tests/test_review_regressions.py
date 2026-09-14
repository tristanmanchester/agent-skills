import unittest
from test_diversity import m
class ExactMatchReviewTests(unittest.TestCase):
    def test_identical_short_and_stopword_only_concepts_are_candidates(self):
        for concept in ['AI','Go','the','AI and Go']:
            result=m.audit(m.parse_ideas(__import__('json').dumps([concept,concept])))
            self.assertTrue(result['candidate_pairs'][0]['exact_normalised_match'])
            self.assertEqual(result['candidate_pairs'][0]['jaccard'],0)
    def test_different_empty_token_sets_are_not_equal(self):
        self.assertEqual(m.audit(m.parse_ideas('["AI","Go"]'))['candidate_pairs'],[])
    def test_case_and_whitespace_normalisation_preserves_exact_match(self):
        self.assertTrue(m.audit(m.parse_ideas('["AI and Go","ai   AND go"]'))['candidate_pairs'][0]['exact_normalised_match'])
