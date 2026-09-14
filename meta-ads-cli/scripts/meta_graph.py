#!/usr/bin/env python3
"""Bounded Graph API fallback for verified gaps in Meta's official Ads CLI.

No CRUD abstraction, automatic retry, redirect following, or absolute URL input.
Every request has an explicit API version. Writes require an exact plan hash.
The hash is an accidental-change check, not proof of human authorisation.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mimetypes
import os
from pathlib import Path
import re
import sys
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener
import uuid

MAX_UPLOAD = 64 * 1024 * 1024
FORBIDDEN = {'method', 'httpmethod', 'accesstoken', 'authorization', 'batch', 'relativeurl', 'headers'}
SENSITIVE = re.compile(r'token|secret|password|authorization|cookie|credential', re.I)

class GraphError(RuntimeError):
    pass

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise GraphError('Redirect refused; credentials were not forwarded')


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False, allow_nan=False).encode()


def checked_path(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'/?(?:me|search|act_[0-9]+|[0-9]+)(?:/[A-Za-z_][A-Za-z0-9_]*)*', value):
        raise GraphError('Use a relative Graph object/edge path without URL, query, fragment, or traversal')
    return value.lstrip('/')


def checked_params(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or not all(isinstance(k, str) for k in value):
        raise GraphError('Parameters must be a JSON object')
    for key in value:
        normalised = re.sub(r'[^a-z]', '', key.lower())
        if normalised in FORBIDDEN:
            raise GraphError('Authentication and transport override parameters are forbidden')
    canonical(value)
    return value


def form(params: dict[str, Any]) -> str:
    return urlencode({k: json.dumps(v, separators=(',', ':'), ensure_ascii=False) if isinstance(v, (dict, list, bool)) else str(v)
                      for k, v in params.items() if v is not None})


def redact(value: Any, secret: str = '') -> Any:
    if isinstance(value, dict):
        return {k: '[REDACTED]' if SENSITIVE.search(k) else redact(
            {a: b for a, b in v.items() if a not in {'next', 'previous'}}
            if k == 'paging' and isinstance(v, dict) else v, secret) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, secret) for v in value]
    if isinstance(value, str):
        value = value.replace(secret, '[REDACTED]') if secret else value
        # Paging URLs are omitted above; do not expose auth-bearing links elsewhere.
        if re.search(r'(?i)(?:[?&](?:access_token|token|key|secret)=|://[^/\s]+@)', value):
            return '[REDACTED URL]'
    return value


def request(method: str, version: str, path: str, params: dict[str, Any], secret: str,
            upload: tuple[str, bytes, str] | None = None) -> Any:
    if method not in {'GET', 'POST', 'DELETE'} or not re.fullmatch(r'v[1-9][0-9]*\.[0-9]+', version):
        raise GraphError('Invalid method or explicit API version')
    if not secret:
        raise GraphError('Set ACCESS_TOKEN in the environment')
    if path:
        checked_path(path)
    url = f'https://graph.facebook.com/{version}/' + path
    headers = {'Authorization': 'Bearer ' + secret, 'User-Agent': 'meta-ads-skill/3'}
    data = None
    if upload:
        filename, content, field = upload
        boundary = 'meta-skill-' + uuid.uuid4().hex
        chunks = []
        for key, value in params.items():
            if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', key):
                raise GraphError('Invalid multipart field name')
            rendered = json.dumps(value) if isinstance(value, (dict, list, bool)) else str(value)
            chunks.append(f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{rendered}\r\n'.encode())
        mime = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        chunks.extend([f'--{boundary}\r\nContent-Disposition: form-data; name="{field}"; filename="{filename}"\r\nContent-Type: {mime}\r\n\r\n'.encode(),
                       content, f'\r\n--{boundary}--\r\n'.encode()])
        data = b''.join(chunks)
        headers['Content-Type'] = f'multipart/form-data; boundary={boundary}'
    elif method in {'GET', 'DELETE'}:
        query = form(params)
        url += '?' + query if query else ''
    else:
        data = form(params).encode()
        headers['Content-Type'] = 'application/x-www-form-urlencoded'
    req = Request(url, data=data, headers=headers, method=method)
    try:
        with build_opener(NoRedirect).open(req, timeout=60) as response:
            payload = json.load(response)
    except HTTPError as exc:
        raise GraphError(f'Graph HTTP {exc.code}; no retry performed. Reconcile a write before repeating it.') from None
    except (URLError, TimeoutError, OSError, ValueError, UnicodeError):
        raise GraphError('Request or response failed; no retry performed. A write may already have succeeded.') from None
    if payload is False or (isinstance(payload, dict) and (payload.get('error') or payload.get('success') is False)):
        raise GraphError('Graph returned an error; no automatic retry performed')
    return payload


def prepare(args: argparse.Namespace) -> tuple[dict[str, Any], tuple[str, bytes, str] | None]:
    if not re.fullmatch(r'v[1-9][0-9]*\.[0-9]+', args.api_version):
        raise GraphError('Supply a currently supported explicit API version such as vNN.0, not a guessed default')
    upload = None
    if args.command == 'batch':
        items = json.loads(args.file.read_text(encoding='utf-8'))
        if not isinstance(items, list) or not 1 <= len(items) <= 50:
            raise GraphError('This helper accepts 1–50 batch operations')
        operations = []
        for item in items:
            if not isinstance(item, dict) or set(item) - {'method', 'path', 'params'}:
                raise GraphError('Batch entries accept only method, path, and params')
            method = item.get('method', 'GET')
            if method not in {'GET', 'POST', 'DELETE'}:
                raise GraphError('Unsupported batch method')
            operations.append({'method': method, 'path': checked_path(item.get('path')), 'params': checked_params(item.get('params', {}))})
        plan = {'kind': 'batch', 'version': args.api_version, 'operations': operations,
                'write': any(item['method'] != 'GET' for item in operations)}
    else:
        params = checked_params(json.loads(args.params.read_text(encoding='utf-8')) if args.params else {})
        path = checked_path(args.path)
        method = 'POST' if args.command == 'upload' else args.method
        plan = {'kind': args.command, 'version': args.api_version, 'method': method, 'path': path, 'params': params, 'write': method != 'GET'}
        if args.command == 'upload':
            if not re.fullmatch(r'act_[0-9]+/(?:adimages|advideos)', path):
                raise GraphError('Upload requires act_ID/adimages or act_ID/advideos')
            filename = args.file.name
            if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*', filename):
                raise GraphError('Use a simple asset filename without control characters or quotes')
            with args.file.open('rb') as stream:
                content = stream.read(MAX_UPLOAD + 1)
            if not content or len(content) > MAX_UPLOAD:
                raise GraphError('This helper accepts non-empty uploads up to 64 MiB; use a documented resumable workflow for larger files')
            field = 'filename' if path.endswith('/adimages') else 'source'
            if field in params:
                raise GraphError('Upload source cannot also be supplied as a parameter')
            upload = (filename, content, field)
            plan['asset'] = {'name': filename, 'bytes': len(content), 'sha256': hashlib.sha256(content).hexdigest()}
    return plan, upload


def run_plan(plan: dict[str, Any], upload: tuple[str, bytes, str] | None, approval: str | None,
             plan_only: bool = False) -> dict[str, Any]:
    digest = hashlib.sha256(canonical(plan)).hexdigest()
    if plan_only:
        return {'executed': False, 'plan_sha256': digest, 'plan': plan}
    if plan['write'] and approval != digest:
        raise GraphError('Write requires --apply-plan with the exact reviewed plan SHA256; first run with --plan')
    secret = os.environ.get('ACCESS_TOKEN', '')
    if plan['kind'] != 'batch':
        payload = request(plan['method'], plan['version'], plan['path'], plan['params'], secret, upload)
        paging = payload.get('paging') if isinstance(payload, dict) else None
        paging = paging if isinstance(paging, dict) else {}
        return {'ok': True, 'executed': True, 'plan_sha256': digest, 'result': redact(payload, secret),
                'more_pages': bool(paging.get('next'))}
    wire = []
    for operation in plan['operations']:
        method, path, params = operation['method'], operation['path'], operation['params']
        item = {'method': method, 'relative_url': path}
        if method == 'POST':
            item['body'] = form(params)
        elif params:
            item['relative_url'] += '?' + form(params)
        wire.append(item)
    payload = request('POST', plan['version'], '', {'batch': wire}, secret)
    if not isinstance(payload, list) or len(payload) != len(wire):
        raise GraphError('Incomplete batch response; reconcile each item before retrying any write')
    results = []
    for index, item in enumerate(payload):
        try:
            body = json.loads(item['body'])
            ok = 200 <= item['code'] < 300 and not (isinstance(body, dict) and (body.get('error') or body.get('success') is False))
        except (TypeError, KeyError, ValueError):
            body, ok = {'error': 'Missing or malformed batch item'}, False
        results.append({'index': index, 'ok': bool(ok), 'result': redact(body, secret)})
    return {'ok': all(item['ok'] for item in results), 'executed': True, 'plan_sha256': digest, 'items': results}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--api-version', required=True)
    parser.add_argument('--plan', action='store_true', help='Validate and print a request plan without network access')
    parser.add_argument('--apply-plan', help='Exact SHA256 of the user-approved write plan')
    sub = parser.add_subparsers(dest='command', required=True)
    raw = sub.add_parser('request')
    raw.add_argument('method', choices=('GET', 'POST', 'DELETE'))
    raw.add_argument('path')
    raw.add_argument('--params', type=Path)
    batch = sub.add_parser('batch')
    batch.add_argument('file', type=Path)
    up = sub.add_parser('upload')
    up.add_argument('path')
    up.add_argument('file', type=Path)
    up.add_argument('--params', type=Path)
    args = parser.parse_args()
    try:
        plan, upload = prepare(args)
        output = run_plan(plan, upload, args.apply_plan, args.plan)
        print(json.dumps(redact(output, os.environ.get('ACCESS_TOKEN', '')), indent=2, ensure_ascii=False))
        return 0 if output.get('ok', True) else 1
    except GraphError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (OSError, ValueError, TypeError):
        # Do not echo provider bodies, input JSON, URLs, or token-bearing exception text.
        print('Graph operation failed or needs an approved plan. No automatic retry occurred; reconcile writes before retrying.', file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
