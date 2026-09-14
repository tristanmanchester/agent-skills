#!/usr/bin/env python3
"""Preview selected agent-facing drafts; --write creates a new private directory."""
from __future__ import annotations
import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ASSETS = {
    'core': [('AGENTS.md.template', 'AGENTS.md.draft'), ('CAPABILITY_MAP.csv', 'capability-map.csv')],
    'web': [('LLMS_TXT.template', 'llms.txt.draft')],
    'api': [('API_AGENT_CONTRACT.md.template', 'api-contract.md'), ('api-catalog.linkset.json', 'api-catalog.json')],
    'cli': [('CLI_AGENT_CONTRACT.md.template', 'cli-contract.md')],
    'app': [('ACTION_PARITY_REVIEW.md.template', 'action-parity.md'), ('CONTEXT_INJECTION.md.template', 'context-contract.md')],
    'a2a': [('a2a-agent-card.json', 'agent-card.json')],
    'mcp': [('mcp-server-card.json', 'local-mcp-description.json')],
    'skills': [('agent-skills-index.json', 'local-skills-index.json')],
    'security': [('permission-matrix.csv', 'permission-matrix.csv')],
    'evals': [('EVALS.json', 'evals.json')],
}

def render(text: str, name: str, base: str, *, is_json: bool) -> str:
    replacements = {
        '<Project name>': name, '<project>': name, '<Product or docs name>': name,
        '<target>': name, '<date>': dt.date.today().isoformat(), '<api-name>': name,
        '<cli-name>': re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-') or 'project',
        'https://api.example.com': base.rstrip('/') + '/api', 'https://example.com': base.rstrip('/'),
    }
    def replace(value):
        if isinstance(value, str):
            for before, after in replacements.items():
                value = value.replace(before, after)
            return value
        if isinstance(value, list):
            return [replace(item) for item in value]
        if isinstance(value, dict):
            return {key: replace(item) for key, item in value.items()}
        return value
    return json.dumps(replace(json.loads(text)), indent=2) + '\n' if is_json else replace(text)

def generate(output: Path, name: str, base: str, surfaces: list[str], *, write: bool = False, templates: Path | None = None) -> dict:
    if not name.strip() or any(ord(char) < 32 for char in name):
        raise ValueError('Project name must be nonempty and contain no control characters')
    parsed = urlsplit(base)
    if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('Base URL must be HTTPS without credentials, query, or fragment')
    if not surfaces or any(surface not in ASSETS for surface in surfaces):
        raise ValueError('Choose explicit supported surfaces')
    templates = templates or Path(__file__).resolve().parents[1] / 'assets/templates'
    files = {}
    for surface in dict.fromkeys(surfaces):
        for source, target in ASSETS[surface]:
            text = (templates / source).read_text(encoding='utf-8')
            files[target] = render(text, name, base, is_json=source.endswith('.json'))
    output = Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise FileExistsError('Choose a new output directory; existing paths are never overwritten')
    report = {'mode': 'written' if write else 'preview', 'output': str(output),
              'files': sorted(files), 'publication': 'DRAFTS_ONLY'}
    if not write:
        return report
    # Preflight all templates first. Parent must exist; do not create arbitrary trees.
    output.mkdir(mode=0o700)
    for target, content in files.items():
        with (output / target).open('x', encoding='utf-8') as stream:
            stream.write(content)
    # A missing final manifest indicates an interrupted/partial write, not success.
    with (output / 'manifest.json').open('x', encoding='utf-8') as stream:
        json.dump({**report, 'complete': True}, stream, indent=2)
    return report

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--project-name', required=True)
    parser.add_argument('--base-url', required=True)
    parser.add_argument('--surface', action='append', choices=sorted(ASSETS), required=True)
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(argv)
    try:
        report = generate(args.output, args.project_name, args.base_url, args.surface, write=args.write)
    except (OSError, ValueError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}), file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
