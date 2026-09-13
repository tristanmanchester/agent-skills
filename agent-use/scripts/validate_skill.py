#!/usr/bin/env python3
"""Read-only structural checks for one Agent Skill; no script execution or network."""
# /// script
# requires-python = ">=3.10"
# dependencies = ["PyYAML>=6.0.3,<7"]
# ///
from __future__ import annotations
import argparse
import ast
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit
import yaml

LIMIT = 2 * 1024 * 1024
NAME = re.compile(r'^(?!.*--)[a-z0-9](?:[a-z0-9-]{0,62}[a-z0-9])?$')
ALLOWED = {'name', 'description', 'license', 'compatibility', 'metadata', 'allowed-tools'}

class UniqueLoader(yaml.SafeLoader):
    pass

def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError('YAML keys must be unique strings')
        result[key] = loader.construct_object(value_node, deep=deep)
    return result

UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)

def read_text(path: Path) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError('Expected a regular, non-symlink file')
    with path.open('rb') as stream:
        content = stream.read(LIMIT + 1)
    if len(content) > LIMIT:
        raise ValueError('File exceeds structural-check size limit')
    return content.decode('utf-8')

def validate(skill_dir: Path) -> dict:
    root = Path(skill_dir).resolve(strict=True)
    errors, warnings = [], []
    if not root.is_dir():
        raise ValueError('Expected a skill directory')
    text = read_text(root / 'SKILL.md')
    match = re.match(r'\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)', text, re.S)
    if not match:
        errors.append('Missing YAML frontmatter delimiters')
        fm = {}
    else:
        try:
            fm = yaml.load(match.group(1), Loader=UniqueLoader)
            if not isinstance(fm, dict):
                raise ValueError('Frontmatter must be a mapping')
        except (yaml.YAMLError, ValueError, TypeError):
            errors.append('Invalid or duplicate-key YAML frontmatter')
            fm = {}
    name = fm.get('name')
    if not isinstance(name, str) or not NAME.fullmatch(name) or name != root.name:
        errors.append('name must match the directory and Agent Skills naming rules')
    for key, maximum, required in [('description', 1024, True), ('compatibility', 500, False)]:
        value = fm.get(key)
        if required or key in fm:
            if not isinstance(value, str) or not 1 <= len(value.strip()) <= maximum:
                errors.append(f'{key} must be nonempty text of at most {maximum} characters')
    for key in ('license', 'allowed-tools'):
        if key in fm and not isinstance(fm[key], str):
            errors.append(f'{key} must be text')
    metadata = fm.get('metadata', {})
    if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items()):
        errors.append('metadata must map string keys to string values')
    if set(fm) - ALLOWED:
        errors.append('Unsupported frontmatter fields: ' + ', '.join(sorted(set(fm) - ALLOWED)))
    if len(text.splitlines()) > 500:
        warnings.append('SKILL.md exceeds the recommended 500 lines')
    checked = 0
    for directory, dirs, files in os.walk(root, followlinks=False):
        dirs[:] = sorted(d for d in dirs if d not in {'.git', '__pycache__', '.venv', 'node_modules'})
        for name in dirs[:]:
            if (Path(directory) / name).is_symlink():
                errors.append('Symlink directory outside validation scope: ' + str((Path(directory) / name).relative_to(root)))
                dirs.remove(name)
        for name in sorted(files):
            checked += 1
            if checked > 20000:
                errors.append('File-count limit reached; validation incomplete')
                return {'valid': False, 'scope': 'structure-only', 'errors': errors, 'warnings': warnings}
            path = Path(directory) / name
            rel = path.relative_to(root).as_posix()
            if path.is_symlink():
                errors.append('Symlink file outside validation scope: ' + rel)
                continue
            if path.suffix not in {'.py', '.json', '.md'}:
                continue
            try:
                content = read_text(path)
                if path.suffix == '.py':
                    ast.parse(content, filename=rel)
                elif path.suffix == '.json':
                    json.loads(content)
                else:
                    # Conventional inline links only, not a complete Markdown parser.
                    for target in re.findall(r'\[[^\]\n]*\]\(([^\s)]+)\)', content):
                        parsed = urlsplit(target)
                        if parsed.scheme or parsed.netloc or not parsed.path or parsed.path.startswith('/'):
                            continue
                        candidate = path.parent / unquote(parsed.path)
                        if not candidate.resolve().is_relative_to(root):
                            warnings.append(f'{rel}: external relative link not checked: {target}')
                        elif not candidate.exists() or candidate.is_symlink():
                            errors.append(f'{rel}: missing or symlinked link target: {target}')
            except (OSError, ValueError, SyntaxError, UnicodeError, RecursionError):
                errors.append(rel + ': unreadable, oversized, or invalid syntax')
    return {'valid': not errors, 'scope': 'structure-only', 'files_seen': checked,
            'errors': errors, 'warnings': warnings, 'runtime_and_protocol_conformance': 'NOT_TESTED'}

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skill-dir', type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        report = validate(args.skill_dir)
    except (OSError, ValueError) as error:
        print(json.dumps({'valid': False, 'error': str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2))
    return 0 if report['valid'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
