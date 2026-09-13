import importlib.util
import io
import json
from pathlib import Path
import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone
import urllib.error

spec = importlib.util.spec_from_file_location('pt', Path(__file__).parents[1] / 'scripts/pettracer.py')
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
NOW = datetime(2026, 9, 13, 12, tzinfo=timezone.utc)

class Tests(unittest.TestCase):
    def pos(self, **kwargs):
        return m.position({'posLat':0,'posLong':0,**kwargs}, NOW, 900)
    def test_zero_coordinates_are_valid(self):
        self.assertEqual(self.pos(timeMeasure='2026-09-13T12:00:00Z')['freshness'], 'recent')
    def test_no_measurement_time_is_not_recent(self):
        self.assertEqual(self.pos(timeDb=NOW.isoformat(), lastContact=NOW.isoformat())['freshness'], 'time_unknown')
    def test_naive_future_stale_times(self):
        for value, state in [('2026-09-13T12:00:00','time_unknown'),('2026-09-13T12:01:00Z','future_timestamp'),('2026-09-13T11:00:00+0000','stale')]:
            self.assertEqual(self.pos(timeMeasure=value)['freshness'], state)
    def test_invalid_coordinates(self):
        for value in [float('nan'), float('inf'), 91, -91, True, 'bad']:
            self.assertEqual(self.pos(posLat=value)['freshness'], 'no_valid_fix')
    def test_no_accuracy_or_battery_guess(self):
        result = self.pos(acc=10, horiPrec=2)
        self.assertNotIn('accuracy_m', result)
        self.assertEqual(result['quality_fields_unverified_units']['horiPrec'],2)
    def test_explicit_account_device_and_type(self):
        for devices in [[{'id':1,'type':1}], [{'id':2}], [{'id':1},{'id':1}], [{'id':1,'type':False}], [{'id':1,'type':7}]]:
            with self.assertRaises(ValueError): m.select(devices,1)
        self.assertEqual(m.select([{'id':1,'type':0}],1)['id'],1)
    def test_bad_window_fails_before_network(self):
        with patch.object(m,'authenticate') as auth, patch('sys.stderr',new=io.StringIO()):
            self.assertEqual(m.main(['history','--device-id','1','--from-time','2026-09-13T12:00:00','--to-time',NOW.isoformat()]),1)
            auth.assert_not_called()
    def test_fixed_origin_and_no_retry(self):
        opener=MagicMock(); opener.open.side_effect=urllib.error.HTTPError('https://portal.pettracer.com',503,'bad',{},io.BytesIO(b'secret'))
        with patch.object(m.urllib.request,'build_opener',return_value=opener):
            with self.assertRaises(ValueError) as err: m.request('devices',token='secret')
            self.assertNotIn('secret',str(err.exception)); self.assertEqual(opener.open.call_count,1)
            self.assertEqual(opener.open.call_args.args[0].full_url,m.ORIGIN+'/map/getccs')
        with self.assertRaises(ValueError): m.request('https://evil.test',token='secret')
    def test_redirect_refusal(self):
        with self.assertRaises(ValueError): m.NoRedirect().redirect_request(None,None,302,'',{},'https://evil.test')
    def test_response_bound(self):
        response=MagicMock(); response.read.return_value=b'x'*(m.MAX_BYTES+1)
        opener=MagicMock(); opener.open.return_value.__enter__.return_value=response
        with patch.object(m.urllib.request,'build_opener',return_value=opener):
            with self.assertRaises(ValueError): m.request('devices',token='secret')
            response.read.assert_called_once_with(m.MAX_BYTES+1)

if __name__ == '__main__': unittest.main()
