import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit

spec = importlib.util.spec_from_file_location('graph', Path(__file__).resolve().parents[1] / 'scripts/meta_graph.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


def raw_plan(method='GET'):
    return {'kind': 'request', 'version': 'v25.0', 'path': 'act_123/campaigns', 'method': method,
            'params': {'fields': 'id,name'}, 'write': method != 'GET'}

class GraphTests(unittest.TestCase):
    def test_path_rejects_other_hosts_and_encoding_tricks(self):
        for path in ('https://evil.test/a', 'http://graph.facebook.com/a', '//evil.test/a', '../a',
                     'act_123/../me', 'act_123?access_token=x', 'act_123#x', 'act_123/%2e%2e',
                     'act_123\\me', 'act_123\n', '', 'act_x'):
            with self.subTest(path=path), self.assertRaises(g.GraphError):
                g.checked_path(path)
        self.assertEqual(g.checked_path('/act_123/campaigns'), 'act_123/campaigns')

    def test_parameter_overrides_are_rejected(self):
        for key in ('method', 'METHOD', 'http_method', 'access_token', 'Access-Token', 'Authorization', 'batch', 'relative_url', 'headers'):
            with self.subTest(key=key), self.assertRaises(g.GraphError):
                g.checked_params({key: 'x'})
        self.assertEqual(g.checked_params({'targeting': {'geo_locations': {'countries': ['DE']}}}), {'targeting': {'geo_locations': {'countries': ['DE']}}})

    def test_explicit_version_is_validated_before_network(self):
        for version in ('latest', 'v25.0/../v1.0', 'https://x', '25', 'v0.0', 'v25.0\n'):
            with self.assertRaises(g.GraphError):
                g.request('GET', version, 'me', {}, 'secret')

    def test_request_uses_fixed_origin_and_no_redirect_handler(self):
        opener = Mock()
        opener.open.return_value.__enter__ = Mock(return_value=io.StringIO('{"id":"123"}'))
        opener.open.return_value.__exit__ = Mock(return_value=False)
        with patch.object(g, 'build_opener', return_value=opener) as build:
            self.assertEqual(g.request('GET', 'v25.0', 'act_123', {'fields': 'id,name'}, 'do-not-echo'), {'id': '123'})
        self.assertIs(build.call_args.args[0], g.NoRedirect)
        request = opener.open.call_args.args[0]
        self.assertEqual(urlsplit(request.full_url).netloc, 'graph.facebook.com')
        self.assertEqual(parse_qs(urlsplit(request.full_url).query), {'fields': ['id,name']})
        self.assertEqual(request.get_header('Authorization'), 'Bearer do-not-echo')

    def test_redirect_never_forwards_credentials(self):
        with self.assertRaises(g.GraphError):
            g.NoRedirect().redirect_request(None, None, 302, 'redirect', {}, 'https://evil.test')

    def test_network_and_http_failures_are_never_retried(self):
        for method in ('GET', 'POST', 'DELETE'):
            for error in (URLError('private-url'), HTTPError('https://secret', 503, 'private', {}, None)):
                opener = Mock()
                opener.open.side_effect = error
                with patch.object(g, 'build_opener', return_value=opener), self.assertRaises(g.GraphError) as caught:
                    g.request(method, 'v25.0', 'act_123', {}, 'key')
                self.assertEqual(opener.open.call_count, 1)
                self.assertNotIn('private', str(caught.exception))

    def test_write_requires_exact_plan_before_network(self):
        plan = raw_plan('POST')
        with patch.object(g, 'request') as send:
            for approval in (None, '', '0' * 64):
                with self.assertRaises(g.GraphError):
                    g.run_plan(plan, None, approval)
            send.assert_not_called()

    def test_plan_only_never_uses_network(self):
        plan = raw_plan('POST')
        with patch.object(g, 'request') as send:
            result = g.run_plan(plan, None, None, True)
            send.assert_not_called()
        self.assertFalse(result['executed'])
        self.assertEqual(result['plan_sha256'], hashlib.sha256(g.canonical(plan)).hexdigest())

    def test_changed_payload_invalidates_approval(self):
        plan = raw_plan('POST')
        approved = hashlib.sha256(g.canonical(plan)).hexdigest()
        plan['params']['daily_budget'] = 99999
        with patch.object(g, 'request') as send, self.assertRaises(g.GraphError):
            g.run_plan(plan, None, approved)
        send.assert_not_called()

    def test_exact_approved_write_executes_once(self):
        plan = raw_plan('POST')
        approved = hashlib.sha256(g.canonical(plan)).hexdigest()
        with patch.dict(os.environ, {'ACCESS_TOKEN': 'fake'}), patch.object(g, 'request', return_value={'id': '123'}) as send:
            result = g.run_plan(plan, None, approved)
        self.assertTrue(result['executed'])
        self.assertEqual(send.call_count, 1)

    def test_batch_partial_failure_is_not_overall_success(self):
        plan = {'kind': 'batch', 'version': 'v25.0', 'write': False,
                'operations': [{'method': 'GET', 'path': 'act_123', 'params': {}}, {'method': 'GET', 'path': 'me', 'params': {}}]}
        response = [{'code': 200, 'body': '{"id":"123"}'}, {'code': 400, 'body': '{"error":{"message":"bad"}}'}]
        with patch.object(g, 'request', return_value=response) as send:
            result = g.run_plan(plan, None, None)
        self.assertFalse(result['ok'])
        self.assertEqual([item['ok'] for item in result['items']], [True, False])
        self.assertEqual(send.call_count, 1)

    def test_batch_null_or_missing_response_is_incomplete(self):
        plan = {'kind': 'batch', 'version': 'v25.0', 'write': False,
                'operations': [{'method': 'GET', 'path': 'me', 'params': {}}]}
        with patch.object(g, 'request', return_value=[]), self.assertRaises(g.GraphError):
            g.run_plan(plan, None, None)
        with patch.object(g, 'request', return_value=[None]):
            self.assertFalse(g.run_plan(plan, None, None)['ok'])

    def test_paging_urls_not_followed_or_exposed(self):
        payload = {'data': [], 'paging': {'cursors': {'after': 'abc'}, 'next': 'https://evil.test/?access_token=secret'}}
        with patch.object(g, 'request', return_value=payload) as send:
            result = g.run_plan(raw_plan(), None, None)
        self.assertTrue(result['more_pages'])
        self.assertNotIn('evil.test', json.dumps(result))
        self.assertEqual(send.call_count, 1)
        self.assertEqual(result['result']['paging']['cursors']['after'], 'abc')

    def test_redaction_never_exposes_prefixes_or_sensitive_fields(self):
        result = g.redact({'access_token': 'x', 'nested': {'secret': 'p@ss'}, 'message': 'hello abcsecret', 'url': 'https://a/?token=p'}, 'abcsecret')
        rendered = json.dumps(result)
        self.assertNotIn('p@ss', rendered)
        self.assertNotIn('abcsecret', rendered)
        self.assertNotIn('token=p', rendered)

    def test_upload_plan_binds_filename_and_exact_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'creative.png'
            file.write_bytes(b'first')
            args = SimpleNamespace(command='upload', api_version='v25.0', path='act_123/adimages', params=None, file=file)
            plan, data = g.prepare(args)
            self.assertEqual(plan['asset']['sha256'], hashlib.sha256(b'first').hexdigest())
            file.write_bytes(b'second')
            self.assertEqual(data[1], b'first')
            next_plan, _ = g.prepare(args)
            self.assertNotEqual(g.canonical(plan), g.canonical(next_plan))

    def test_batch_requires_structured_safe_entries(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'batch.json'
            args = SimpleNamespace(command='batch', api_version='v25.0', file=file)
            for items in ([], [{'method': 'GET', 'path': 'https://evil.test'}],
                          [{'method': 'GET', 'path': 'me', 'headers': ['Authorization: secret']}],
                          [{'method': 'PATCH', 'path': 'me'}]):
                file.write_text(json.dumps(items))
                with self.assertRaises(g.GraphError):
                    g.prepare(args)

if __name__ == '__main__':
    unittest.main()
