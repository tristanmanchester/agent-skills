#!/usr/bin/env python3
"""Bounded, read-only PetTracer portal lookups. Unofficial protocol; no device writes."""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import math
import os
import re
import sys
import urllib.error
import urllib.request

ORIGIN = 'https://portal.pettracer.com/api'
OPERATIONS = {'login': ('POST', '/user/login'), 'devices': ('GET', '/map/getccs'),
              'history': ('POST', '/map/getccpositions')}
MAX_BYTES = 2 * 1024 * 1024

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('Refusing portal redirect; verify the service endpoint')

def request(operation, *, token=None, payload=None, timeout=20):
    if operation not in OPERATIONS:
        raise ValueError('Unsupported operation')
    if type(timeout) is not int or not 1 <= timeout <= 60:
        raise ValueError('Timeout must be 1 to 60 seconds')
    method, endpoint = OPERATIONS[operation]
    headers = {'Accept': 'application/json', 'User-Agent': 'pettracer-skill/1.0'}
    if operation != 'login':
        if not isinstance(token, str) or not token or any(c in token for c in '\r\n'):
            raise ValueError('An access token is required')
        headers['Authorization'] = 'Bearer ' + token
    data = None
    if payload is not None:
        data = json.dumps(payload, allow_nan=False).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(ORIGIN + endpoint, method=method, headers=headers, data=data)
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=timeout) as response:
            raw = response.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('Portal response exceeds size bound')
            return json.loads(raw, parse_constant=lambda _: (_ for _ in ()).throw(ValueError('Non-finite JSON')))
    except urllib.error.HTTPError as error:
        raise ValueError(f'Portal HTTP {error.code}; no automatic retry or re-login') from None
    except (urllib.error.URLError, TimeoutError, OSError):
        raise ValueError('Portal transport failed; no response is not an empty result') from None

def authenticate(timeout):
    token = os.environ.get('PETTRACER_TOKEN')
    if token:
        return token
    user, password = os.environ.get('PETTRACER_USERNAME'), os.environ.get('PETTRACER_PASSWORD')
    if not user or not password:
        raise ValueError('Set PETTRACER_TOKEN or PETTRACER_USERNAME and PETTRACER_PASSWORD privately')
    response = request('login', payload={'login': user, 'password': password}, timeout=timeout)
    token = response.get('access_token') if isinstance(response, dict) else None
    if not isinstance(token, str) or not token:
        raise ValueError('Login did not return the expected access_token')
    return token

def timestamp(value):
    if not isinstance(value, str) or not re.match(r'^\d{4}-\d{2}-\d{2}T', value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return parsed.astimezone(timezone.utc) if parsed.utcoffset() is not None else None
    except ValueError:
        return None

def number(value, low, high):
    if isinstance(value, bool) or value is None:
        return None
    try:
        parsed = float(value)
        return parsed if math.isfinite(parsed) and low <= parsed <= high else None
    except (TypeError, ValueError, OverflowError):
        return None

def position(raw, now, max_age):
    if type(max_age) is not int or max_age < 1 or max_age > 604800:
        raise ValueError('Freshness threshold must be 1 to 604800 seconds')
    if now.utcoffset() is None:
        raise ValueError('Reference time must include a timezone')
    if raw is None:
        raw = {}
    elif not isinstance(raw, dict):
        raise ValueError('Unexpected position shape; expected an object or absent fix')
    lat, lon = number(raw.get('posLat'), -90, 90), number(raw.get('posLong'), -180, 180)
    measured = timestamp(raw.get('timeMeasure'))
    age = (now - measured).total_seconds() if measured is not None else None
    state = ('no_valid_fix' if lat is None or lon is None else 'time_unknown' if age is None
             else 'future_timestamp' if age < 0 else 'stale' if age > max_age else 'recent')
    return {'lat': lat, 'lon': lon, 'measurement_time': measured.isoformat() if measured else None,
            'measurement_time_raw': raw.get('timeMeasure') if isinstance(raw.get('timeMeasure'), str) else None,
            'database_time': raw.get('timeDb') if isinstance(raw.get('timeDb'), str) else None,
            'age_seconds': age, 'freshness': state, 'freshness_threshold_seconds': max_age,
            'quality_fields_unverified_units': {k: number(raw.get(k), 0, 1e9) for k in ('acc', 'horiPrec')}}

def history_position(raw, now, max_age, start, end):
    item = position(raw, now, max_age)
    measured = timestamp(item['measurement_time'])
    item['window_membership'] = ('unknown' if measured is None else
                                 'inside' if start <= measured <= end else 'outside')
    item['raw'] = raw
    return item


def device_id(value):
    if isinstance(value, bool) or not re.fullmatch(r'[0-9]+', str(value)) or int(value) <= 0:
        raise ValueError('Device ID must be a positive integer')
    return int(value)

def select(devices, requested_id):
    target = device_id(requested_id)
    matches = [d for d in devices if device_id(d.get('id')) == target]
    if len(matches) != 1:
        raise ValueError('Device ID is absent or ambiguous in this account inventory')
    device = matches[0]
    if device.get('type') in (1, '1'):
        raise ValueError('Selected device is a HomeStation, not a pet collar')
    if device.get('type') not in (None, 0, '0') or isinstance(device.get('type'), bool):
        raise ValueError('Unrecognised device type; verify it in the portal')
    return device

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=('list', 'locate', 'history'))
    parser.add_argument('--device-id', type=device_id)
    parser.add_argument('--timeout', type=int, default=20)
    parser.add_argument('--max-age-seconds', type=int, default=900, help='Local freshness policy, not a manufacturer guarantee')
    parser.add_argument('--from-time'); parser.add_argument('--to-time')
    args = parser.parse_args(argv)
    try:
        if args.operation != 'list' and args.device_id is None:
            raise ValueError('--device-id is required; resolve it with list first')
        now = datetime.now(timezone.utc)
        position({}, now, args.max_age_seconds)
        start = timestamp(args.from_time); end = timestamp(args.to_time)
        if args.operation == 'history':
            if start is None or end is None or not 0 < (end - start).total_seconds() <= 604800:
                raise ValueError('History needs timezone-aware --from-time/--to-time, ordered and at most seven days apart')
        elif args.from_time is not None or args.to_time is not None:
            raise ValueError('Time window is only valid for history')
        token = authenticate(args.timeout)
        devices = request('devices', token=token, timeout=args.timeout)
        if not isinstance(devices, list) or any(not isinstance(d, dict) for d in devices):
            raise ValueError('Unexpected device inventory shape')
        for d in devices: device_id(d.get('id'))
        result = {'protocol': 'unofficial-portal', 'retrieved_at': datetime.now(timezone.utc).isoformat()}
        if args.operation == 'list':
            result['devices'] = [{'id': d['id'], 'name': (d.get('details') or {}).get('name') if isinstance(d.get('details'), dict) else None,
                                  'type_raw': d.get('type'), 'has_last_position': isinstance(d.get('lastPos'), dict)} for d in devices]
        else:
            device = select(devices, args.device_id)
            result['device_id'] = args.device_id
            result['device_type_verified'] = device.get('type') in (0, '0')
            if args.operation == 'locate':
                result['last_fix'] = position(device.get('lastPos'), datetime.now(timezone.utc), args.max_age_seconds)
                result['last_contact_raw'] = device.get('lastContact')
                result['battery_raw'] = device.get('bat')
                result['home_raw'] = device.get('home')
            else:
                payload = {'devId': args.device_id, 'filterTime': int(start.timestamp() * 1000), 'toTime': int(end.timestamp() * 1000)}
                raw = request('history', token=token, payload=payload, timeout=args.timeout)
                if not isinstance(raw, list) or any(not isinstance(p, dict) for p in raw):
                    raise ValueError('Unexpected history shape')
                result['requested_window'] = payload
                result['window_bounds'] = {'start': start.isoformat(), 'end': end.isoformat(), 'inclusive': True}
                observed_at = datetime.now(timezone.utc)
                result['positions'] = [history_position(p, observed_at, args.max_age_seconds, start, end) for p in raw]
                result['history_completeness'] = 'not_verified'
                result['order'] = 'provider_response_order'
        print(json.dumps(result, allow_nan=False, indent=2))
        return 0
    except (ValueError, TypeError, OverflowError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
