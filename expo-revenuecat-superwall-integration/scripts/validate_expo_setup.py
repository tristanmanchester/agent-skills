#!/usr/bin/env python3
"""Read-only Expo billing inventory. An inventory is not a working-store test."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

PACKAGES = ('expo', 'expo-superwall', 'react-native-purchases', 'react-native-purchases-ui', 'expo-build-properties')
REQUIRED = PACKAGES[:3]
IGNORED = {'.git', '.expo', 'node_modules', 'build', 'dist', 'coverage', '.next', '.turbo'}
MARKERS = ('Purchases.configure', 'CustomPurchaseControllerProvider', 'SuperwallProvider',
           'purchasesAreCompletedBy', 'addCustomerInfoUpdateListener', 'removeCustomerInfoUpdateListener',
           'purchaseSubscriptionOption', 'syncPurchasesForResult', 'logIn', 'identify', 'registerPlacement')
KEYS = ('EXPO_PUBLIC_REVENUECAT_IOS_API_KEY', 'EXPO_PUBLIC_REVENUECAT_ANDROID_API_KEY',
        'EXPO_PUBLIC_SUPERWALL_IOS_API_KEY', 'EXPO_PUBLIC_SUPERWALL_ANDROID_API_KEY')


def read_object(path: Path) -> dict:
    value = json.loads(path.read_text(encoding='utf-8'))
    if not isinstance(value, dict):
        raise ValueError('Expected a JSON object')
    return value


def inspect(root: Path) -> dict:
    package = read_object(root / 'package.json')
    declared = {}
    for field in ('dependencies', 'devDependencies', 'peerDependencies'):
        values = package.get(field, {})
        if not isinstance(values, dict):
            raise ValueError('Invalid dependency map')
        declared.update(values)
    dependencies = {}
    for name in PACKAGES:
        installed = root / 'node_modules' / name / 'package.json'
        resolved = read_object(installed).get('version') if installed.is_file() else None
        dependencies[name] = {'declared': declared.get(name), 'installed': resolved}
    blockers = [f'Missing required dependency: {name}' for name in REQUIRED if name not in declared]
    matches = {name: [] for name in MARKERS}
    warnings = []
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = [name for name in dirs if name not in IGNORED and not (Path(directory) / name).is_symlink()]
        for name in files:
            path = Path(directory) / name
            if path.is_symlink() or path.suffix not in {'.ts', '.tsx', '.js', '.jsx', '.mjs', '.cjs'}:
                continue
            relative = str(path.relative_to(root))
            try:
                if path.stat().st_size > 2_000_000:
                    warnings.append(f'Not scanned (size limit): {relative}')
                    continue
                text = path.read_text(encoding='utf-8')
            except (OSError, UnicodeError):
                warnings.append(f'Not scanned: {relative}')
                continue
            for marker in MARKERS:
                if marker in text:
                    matches[marker].append(relative)
    # Only presence is reported. Values, unrelated environment variables, and source lines never leave the scanner.
    presence = {key: [] for key in KEYS}
    for path in sorted(root.glob('.env*')):
        if not path.is_file() or path.is_symlink():
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            warnings.append(f'Could not inspect {path.name}')
            continue
        for key in KEYS:
            if re.search(rf'^\s*(?:export\s+)?{re.escape(key)}\s*=', text, flags=re.MULTILINE):
                presence[key].append(path.name)
    configs = [name for name in ('app.json', 'app.config.json', 'app.config.js', 'app.config.ts', 'app.config.mjs', 'app.config.cjs') if (root / name).is_file()]
    activities = []
    manifest = root / 'android/app/src/main/AndroidManifest.xml'
    if manifest.is_file():
        ns = '{http://schemas.android.com/apk/res/android}'
        try:
            for activity in ET.parse(manifest).iter('activity'):
                activities.append({'name': activity.get(ns + 'name'), 'declared_launch_mode': activity.get(ns + 'launchMode', 'standard')})
        except (ET.ParseError, OSError):
            warnings.append('Could not parse source Android manifest')
    return {
        'scope': 'static-inventory', 'runtime_verified': False,
        'dependencies': dependencies, 'config_files': configs,
        'source_occurrences_not_execution_proof': matches,
        'environment_key_locations_no_values': presence,
        'source_manifest_activities_not_merged_manifest': activities,
        'blockers': blockers, 'warnings': warnings,
        'requires_verification': [
            'Resolve Expo config using the trusted project/build profile; dynamic config was not executed.',
            'Check platform minima against the installed Expo and native SDKs. Do not lower defaults to old examples.',
            'Inspect the merged Android manifest and actual billing activity launch mode.',
            'Prove one purchase-completion owner, exact offer selection, listener cleanup, and identity-change gating.',
            'Test store purchase, cancellation, pending, restore, account switching, and entitlement fulfilment on real builds.',
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--project-root', type=Path, default=Path.cwd())
    parser.add_argument('--json', action='store_true', help='JSON is the output format for all invocations')
    args = parser.parse_args()
    try:
        result = inspect(args.project_root.expanduser().resolve())
    except (OSError, ValueError, TypeError):
        print('Cannot inspect project: provide a readable package.json with valid dependency maps.', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['blockers'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
