#!/usr/bin/env python3
"""Read-only source inventory. Never determines App Store submission readiness."""
from __future__ import annotations
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import plistlib
import sys
from xml.parsers.expat import ExpatError
from urllib.parse import urlsplit

IGNORE = {'.git', 'node_modules', 'Pods', 'build', 'DerivedData', '.expo', '.venv'}
MAX_BYTES = 2 * 1024 * 1024


def inventory(repo: Path, max_entries: int = 20000) -> dict:
    root = Path(repo).resolve(strict=True)
    if not root.is_dir():
        raise ValueError('Repository must be a directory')
    if type(max_entries) is not int or not 1 <= max_entries <= 100000:
        raise ValueError('max_entries must be between 1 and 100000')
    result = {
        'schema_version': 1, 'scope': 'source-inventory',
        'submission_readiness': 'NOT_ASSESSED',
        'root': str(root), 'generated_at': dt.datetime.now(dt.timezone.utc).isoformat(),
        'coverage': {'complete_within_scope': True, 'entries_seen': 0,
                     'excluded_directory_names': sorted(IGNORE), 'skipped_symlinks': []},
        'projects': [], 'packages': [], 'expo_configs': [], 'dynamic_configs': [],
        'icons': [], 'plists': [], 'privacy_manifests': [], 'entitlements': [],
        'launch_assets': [], 'issues': [],
    }

    def rel(p: Path) -> str:
        return p.relative_to(root).as_posix()

    def issue(p: Path, reason: str) -> None:
        result['issues'].append({'path': rel(p), 'reason': reason})
        result['coverage']['complete_within_scope'] = False

    def load(p: Path, parser):
        # No project code, shell, package manager, or dynamic config is executed.
        if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to(root):
            issue(p, 'non-regular file, symlink, or outside source root')
            return None
        try:
            with p.open('rb') as stream:
                raw = stream.read(MAX_BYTES + 1)
            if len(raw) > MAX_BYTES:
                raise ValueError('source metadata exceeds size bound')
            value = parser(raw)
            if not isinstance(value, dict):
                raise ValueError('expected an object/dictionary')
            return value
        except (OSError, ValueError, TypeError, OverflowError, plistlib.InvalidFileException, ExpatError) as error:
            issue(p, f'cannot parse bounded metadata ({type(error).__name__})')
            return None

    def reference(base: Path, value) -> dict:
        if not isinstance(value, str) or not value:
            return {'state': 'invalid-reference'}
        try:
            if urlsplit(value).scheme in {'http', 'https'}:
                return {'reference': value, 'state': 'remote-not-fetched'}
        except ValueError:
            return {'state': 'invalid-reference'}
        p = base / value
        if p.is_absolute() and not p.resolve().is_relative_to(root):
            return {'reference': value, 'state': 'outside-scope'}
        if p.is_symlink() or not p.resolve().is_relative_to(root):
            return {'reference': value, 'state': 'symlink-or-outside-scope'}
        return {'reference': value, 'state': 'exists' if p.exists() else 'missing'}

    def inspect(p: Path) -> None:
        name = p.name
        if name == 'package.json':
            data = load(p, json.loads)
            if data is not None:
                deps = data.get('dependencies', {})
                dev = data.get('devDependencies', {})
                deps = {**(dev if isinstance(dev, dict) else {}), **(deps if isinstance(deps, dict) else {})}
                result['packages'].append({'path': rel(p), 'frameworks': {
                    key: deps[key] for key in ('expo', 'react-native') if isinstance(deps.get(key), str)}})
        elif name == 'app.json':
            data = load(p, json.loads)
            expo = data.get('expo') if data else None
            if isinstance(expo, dict):
                ios = expo.get('ios') if isinstance(expo.get('ios'), dict) else {}
                icon = ios.get('icon', expo.get('icon'))
                values = icon if isinstance(icon, dict) else {'default': icon} if icon is not None else {}
                result['expo_configs'].append({'path': rel(p), 'resolved': False,
                    'declared': {k: v for k, v in {'bundleIdentifier': ios.get('bundleIdentifier'),
                        'version': expo.get('version'), 'buildNumber': ios.get('buildNumber')}.items() if isinstance(v, str)},
                    'icon_references': {k: reference(p.parent, v) for k, v in values.items()}})
        elif name.startswith('app.config.'):
            result['dynamic_configs'].append(rel(p))
        elif name == 'Contents.json' and p.parent.suffix == '.appiconset':
            data = load(p, json.loads)
            images = data.get('images') if data else None
            entries = []
            if isinstance(images, list):
                for image in images:
                    if isinstance(image, dict):
                        entries.append({**{k: image[k] for k in ('idiom', 'size', 'scale', 'platform') if isinstance(image.get(k), str)},
                                        'file': reference(p.parent, image.get('filename'))})
            result['icons'].append({'path': rel(p.parent), 'kind': 'asset-catalog',
                                    'entries': entries, 'compiled_validity': 'NOT_ASSESSED'})
        elif name == 'Info.plist':
            data = load(p, plistlib.loads)
            if data is not None:
                ats = data.get('NSAppTransportSecurity', {})
                result['plists'].append({'path': rel(p), 'resolved': False,
                    'declared': {k: data[k] for k in ('CFBundleIdentifier', 'CFBundleShortVersionString', 'CFBundleVersion', 'UILaunchStoryboardName') if isinstance(data.get(k), str)},
                    'usage_description_keys': sorted(k for k in data if k.startswith('NS') and k.endswith('UsageDescription')),
                    'arbitrary_loads': ats.get('NSAllowsArbitraryLoads') if isinstance(ats, dict) else None,
                    'declarative_launch_screen': 'UILaunchScreen' in data})
        elif name == 'PrivacyInfo.xcprivacy' or p.suffix == '.entitlements':
            data = load(p, plistlib.loads)
            target = 'privacy_manifests' if name == 'PrivacyInfo.xcprivacy' else 'entitlements'
            result[target].append({'path': rel(p), 'parseable': data is not None, 'conformance': 'NOT_ASSESSED'})
        elif p.suffix == '.icon':
            result['icons'].append({'path': rel(p), 'kind': 'icon-composer', 'compiled_validity': 'NOT_ASSESSED'})
        elif p.suffix in {'.storyboard', '.xib'}:
            result['launch_assets'].append(rel(p))

    def walk_error(error):
        result['coverage']['complete_within_scope'] = False
        result['issues'].append({'reason': f'directory traversal failed ({type(error).__name__})'})

    for directory, dirs, names in os.walk(root, followlinks=False, onerror=walk_error):
        base = Path(directory)
        for name in sorted(dirs + names):
            p = base / name
            result['coverage']['entries_seen'] += 1
            if result['coverage']['entries_seen'] > max_entries:
                issue(base, 'entry limit reached; inventory is partial')
                return result
            if p.is_symlink():
                result['coverage']['skipped_symlinks'].append(rel(p))
                result['coverage']['complete_within_scope'] = False
                if name in dirs:
                    dirs.remove(name)
                continue
            if name in dirs:
                if name in IGNORE:
                    dirs.remove(name)
                elif p.suffix in {'.xcodeproj', '.xcworkspace'}:
                    result['projects'].append(rel(p))
                elif p.suffix == '.icon':
                    inspect(p)
                    dirs.remove(name)
            else:
                inspect(p)
        dirs.sort()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', required=True, type=Path)
    parser.add_argument('--max-entries', type=int, default=20000)
    args = parser.parse_args()
    try:
        result = inventory(args.repo, args.max_entries)
    except (OSError, ValueError) as error:
        print(json.dumps({'error': str(error), 'submission_readiness': 'NOT_ASSESSED'}), file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0 if result['coverage']['complete_within_scope'] else 2


if __name__ == '__main__':
    raise SystemExit(main())
