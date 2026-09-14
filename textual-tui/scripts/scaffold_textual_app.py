#!/usr/bin/env python3
"""Render reviewed Textual starters into a new directory; never execute them."""
from __future__ import annotations
import argparse
import ast
import json
import keyword
from pathlib import Path
import re
import sys

TEMPLATES = ('dashboard', 'form', 'chat', 'data-explorer', 'file-browser', 'settings',
             'wizard', 'log-monitor', 'editor', 'admin-modes', 'download-demo')
ASSETS = Path(__file__).resolve().parents[1] / 'assets' / 'templates'
MAX_TEMPLATE_BYTES = 262144


def identifier(value: str) -> str:
    if not isinstance(value, str) or not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', value) or keyword.iskeyword(value):
        raise ValueError('Module and class names must be non-keyword Python identifiers')
    return value


def render_python(text: str, module: str, class_name: str, title: str) -> str:
    # Identifiers are validated; free text is inserted into AST string constants,
    # never interpolated into executable source or evaluated.
    text = text.replace('{{MODULE}}', identifier(module)).replace('{{CLASS_NAME}}', identifier(class_name))
    tree = ast.parse(text)
    class Strings(ast.NodeTransformer):
        def visit_Constant(self, node):
            if isinstance(node.value, str):
                node.value = node.value.replace('{{APP_TITLE}}', title)
            return node
    tree = Strings().visit(tree)
    # Template placeholders must be resolved before output. Check the structure
    # before adding free text, so a title containing {{literal}} remains valid.
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in {'MODULE', 'CLASS_NAME', 'APP_TITLE'}:
            raise ValueError('Unresolved template identifier')
    result = ast.unparse(ast.fix_missing_locations(tree)) + '\n'
    ast.parse(result)
    return result


def plan(template: str, module: str, class_name: str, title: str, assets: Path = ASSETS) -> dict[str, str]:
    if template not in TEMPLATES:
        raise ValueError('Unknown template')
    identifier(module); identifier(class_name)
    if not isinstance(title, str) or not title.strip() or len(title) > 1000:
        raise ValueError('App title must contain 1 to 1000 characters')
    stem = template.replace('-', '_')
    inputs = {}
    for kind in ('app.py', 'tcss', 'test.py'):
        p = assets / f'{stem}_{kind}.tmpl'
        if p.is_symlink() or not p.is_file():
            raise ValueError(f'Missing or non-regular template: {p.name}')
        with p.open('rb') as stream:
            raw = stream.read(MAX_TEMPLATE_BYTES + 1)
        if len(raw) > MAX_TEMPLATE_BYTES:
            raise ValueError('Template exceeds size bound')
        text = raw.decode('utf-8')
        unknown = set(re.findall(r'\{\{([A-Z_]+)\}\}', text)) - {'MODULE', 'CLASS_NAME', 'APP_TITLE'}
        if unknown:
            raise ValueError('Unrecognised template placeholder')
        inputs[kind] = text
    css = inputs['tcss']
    if '{{APP_TITLE}}' in css:
        raise ValueError('Free text is not permitted in TCSS placeholders')
    css = css.replace('{{MODULE}}', module).replace('{{CLASS_NAME}}', class_name)
    return {
        f'{module}.py': render_python(inputs['app.py'], module, class_name, title),
        f'{module}.tcss': css,
        f'tests/test_{module}.py': render_python(inputs['test.py'], module, class_name, title),
    }


def write_plan(files: dict[str, str], destination: Path) -> None:
    # Preflight all names before creating anything. Output is intentionally a new
    # private directory; failure can leave a partial draft, never an overwritten app.
    if not files or any(Path(p).is_absolute() or '..' in Path(p).parts for p in files):
        raise ValueError('Invalid output path')
    destination.mkdir(mode=0o700)  # No parents=True or exist_ok; explicit new target.
    for name, text in files.items():
        output = destination / name
        output.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
        with output.open('x', encoding='utf-8') as stream:
            output.chmod(0o600)
            stream.write(text)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list-templates', action='store_true')
    parser.add_argument('--template', choices=TEMPLATES)
    parser.add_argument('--module')
    parser.add_argument('--class-name')
    parser.add_argument('--app-title')
    parser.add_argument('--output-dir', type=Path)
    parser.add_argument('--write', action='store_true', help='Write into a new directory; otherwise print a preview')
    args = parser.parse_args(argv)
    if args.list_templates:
        print(json.dumps(TEMPLATES)); return 0
    if any(x is None for x in (args.template, args.module, args.class_name, args.app_title)):
        parser.error('--template, --module, --class-name and --app-title are required')
    try:
        files = plan(args.template, args.module, args.class_name, args.app_title)
        if args.write:
            if args.output_dir is None:
                raise ValueError('--write requires --output-dir with an existing parent and a new final directory')
            write_plan(files, args.output_dir.expanduser())
        print(json.dumps({'status': 'written' if args.write else 'preview', 'files': files}, indent=2))
        return 0
    except (OSError, ValueError, SyntaxError, UnicodeError) as error:
        print(json.dumps({'status': 'error', 'error': str(error)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
