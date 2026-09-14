"""Strict, bounded inputs and finite arithmetic for decision aids, not forecasts."""
from __future__ import annotations
import argparse
from decimal import Decimal
import json
import math
from pathlib import Path
import sys

MAX_BYTES = 1048576

def number(value, label):
    if type(value) not in (int, float):
        raise ValueError(f'{label} must be a finite JSON number, not a boolean or string')
    try:
        finite = math.isfinite(value)
    except OverflowError:
        finite = False
    if not finite:
        raise ValueError(f'{label} must be finite')
    return Decimal(str(value))

def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError('Calculated value exceeds the finite output range')
    return result

def name(value, label):
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise ValueError(f'{label} must be nonempty text of at most 200 characters')
    return value

def object_keys(value, required, optional=()):
    if not isinstance(value, dict) or not set(required) <= set(value) or set(value) - set(required) - set(optional):
        raise ValueError(f'Expected object fields {sorted(required)} with optional {sorted(optional)}')

def unique_rows(rows, minimum):
    if not isinstance(rows, list) or not minimum <= len(rows) <= 1000:
        raise ValueError(f'Expected {minimum} to 1000 rows')
    names = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError('Each row must be an object')
        value = name(row.get('name'), 'Row name')
        if value in names:
            raise ValueError('Row names must be unique')
        names.add(value)
    return rows

def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError('Duplicate JSON object key')
        result[key] = value
    return result

def load_input(path):
    path = Path(path)
    if path.is_symlink() or not path.is_file():
        raise ValueError('Input must be a regular JSON file, not a symlink')
    with path.open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds the 1 MiB bound')
    def invalid(_):
        raise ValueError('Non-finite JSON number')
    return json.loads(raw, object_pairs_hook=pairs, parse_constant=invalid)

def cli(compute, description):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--input', required=True, type=Path)
    args = parser.parse_args()
    try:
        result = compute(load_input(args.input))
        print(json.dumps(result, allow_nan=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, ArithmeticError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 1
