#!/usr/bin/env python3
"""Parse local scripts and all starter outputs, without bytecode or app execution."""
import ast
import json
from pathlib import Path
import sys
from scaffold_textual_app import TEMPLATES, plan


def main():
    root = Path(__file__).resolve().parents[1]
    try:
        for script in (root / 'scripts').glob('*.py'):
            ast.parse(script.read_text(), filename=str(script))
        rendered = 0
        for template in TEMPLATES:
            module = template.replace('-', '_')
            name = ''.join(part.title() for part in module.split('_')) + 'App'
            for filename, content in plan(template, module, name, 'A "quoted" title').items():
                if filename.endswith('.py'):
                    ast.parse(content, filename=filename)
            rendered += 1
        print(json.dumps({'status': 'parsed', 'templates': rendered, 'runtime_tested': False}))
        return 0
    except (OSError, ValueError, SyntaxError) as error:
        print(json.dumps({'status': 'error', 'error': str(error)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
