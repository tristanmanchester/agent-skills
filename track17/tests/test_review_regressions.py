import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from test_track17 import t, message

class PollReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/'track.sqlite3'
        self.item=message()['data'] | {'param':'required-carrier-param','lang':'de'}
        with t.connect(self.path) as conn, patch.object(t,'now',return_value='2026-09-14T00:00:00+00:00'):
            t.apply_item(conn,self.item)
        conn.close()
    def stored(self):
        conn=t.connect(self.path)
        try: return dict(conn.execute('SELECT * FROM parcels').fetchone())
        finally: conn.close()
    def run_command(self,*arguments,time='2026-09-14T01:00:00+00:00'):
        with patch.object(t,'database_path',return_value=self.path),patch.object(t,'now',return_value=time),patch.object(t,'api',return_value={'data':{'accepted':[self.item]}}) as api:
            out,code=t.run(t.parser().parse_args(list(arguments)))
            self.assertEqual(code,0)
            return out,api.call_args.args
    def test_single_refresh_preserves_param_and_language(self):
        out,args=self.run_command('status',self.item['number'],'--carrier',str(self.item['carrier']),'--refresh')
        self.assertEqual(args,('gettrackinfo',[{k:self.item[k] for k in ('number','carrier','param','lang')}]))
        self.assertEqual(out['last_refreshed_at'],'2026-09-14T01:00:00+00:00')
    def test_identical_sync_updates_only_refresh_timestamp(self):
        before=self.stored(); self.run_command('sync');after=self.stored()
        self.assertEqual(before['snapshot'],after['snapshot'])
        self.assertEqual(before['updated_at'],after['updated_at'])
        self.assertIsNone(before['last_refreshed_at']);self.assertIsNotNone(after['last_refreshed_at'])
        self.run_command('sync',time='2026-09-14T02:00:00+00:00')
        self.assertEqual(self.stored()['last_refreshed_at'],'2026-09-14T02:00:00+00:00')
    def test_failed_poll_does_not_record_success(self):
        before=self.stored()
        with patch.object(t,'database_path',return_value=self.path),patch.object(t,'api',side_effect=t.Track17Error('synthetic')):
            with self.assertRaises(t.Track17Error):t.run(t.parser().parse_args(['sync']))
        self.assertEqual(self.stored(),before)
