import unittest
from test_preflight import m

class CommentReviewTests(unittest.TestCase):
    def test_hidden_abstract_is_not_an_opening(self):
        with self.assertRaises(ValueError):m.extract_opening('<!--\n## Abstract\nHidden\n-->\n## Results\nData','Abstract')
    def test_hidden_peer_does_not_truncate_real_abstract(self):
        opening=m.extract_opening('## Abstract\nFirst words\n<!--\n## Results\nHidden words\n-->\nLast words\n## Results\nActual','Abstract')
        self.assertEqual(opening.split(),['First','words','Last','words'])
    def test_hidden_duplicate_does_not_make_visible_heading_ambiguous(self):
        self.assertEqual(m.extract_opening('<!-- ## Abstract -->\n## Abstract\nVisible','Abstract'),'Visible')
    def test_inline_comment_keeps_words_separate(self):
        self.assertEqual(m.extract_opening('## Abstract\nFirst<!-- note -->last','Abstract').split(),['First','last'])
    def test_unclosed_comment_is_unverified(self):
        with self.assertRaises(ValueError):m.extract_opening('## Abstract\nWords\n<!-- unclosed','Abstract')
