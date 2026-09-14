from datetime import datetime,timedelta,timezone
import unittest
from test_pettracer import m
class PositionReviewTests(unittest.TestCase):
    def setUp(self):self.now=datetime(2026,9,14,tzinfo=timezone.utc)
    def test_only_absent_or_object_position_is_accepted(self):
        self.assertEqual(m.position(None,self.now,900)['freshness'],'no_valid_fix')
        for value in [[],False,0,'schema changed']:
            with self.assertRaises(ValueError):m.position(value,self.now,900)
    def test_history_window_membership_is_independent_of_freshness(self):
        start=self.now-timedelta(hours=3);end=self.now-timedelta(hours=2)
        for measured,expected in [(start,'inside'),(end,'inside'),(start-timedelta(seconds=1),'outside'),(end+timedelta(seconds=1),'outside'),(None,'unknown')]:
            raw={'posLat':0,'posLong':0,'custom':'keep'}
            if measured:raw['timeMeasure']=measured.isoformat()
            result=m.history_position(raw,self.now,900,start,end)
            self.assertEqual(result['window_membership'],expected);self.assertEqual(result['raw'],raw)
            self.assertNotIn('window_membership',raw)
