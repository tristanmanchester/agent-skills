#!/usr/bin/env python3
"""Find lexical overlap in a small idea set; not a semantic or novelty assessment."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import sys

MAX_INPUT = 1024 * 1024
MAX_IDEAS = 200
MAX_TEXT = 2000
STOP = set('a an and are as at be by for from in into is it of on or that the their this to using with'.split())


def parse_ideas(raw: str) -> list[dict[str, str]]:
    text = raw.strip()
    if not text or len(raw.encode('utf-8')) > MAX_INPUT:
        raise ValueError('Supply a nonempty idea set of at most 1 MiB')
    if text.startswith(('[', '{')):
        data = json.loads(text)  # Malformed JSON must not silently become a prose idea.
        if not isinstance(data, list):
            raise ValueError('JSON input must be an array')
    else:
        data = [re.sub(r'^\s*(?:[-*+]\s+|\d+[.)]\s+)', '', line).strip()
                for line in text.splitlines() if line.strip()]
    if not 1 <= len(data) <= MAX_IDEAS:
        raise ValueError(f'Supply 1..{MAX_IDEAS} ideas')
    ideas = []
    for index, item in enumerate(data, 1):
        if isinstance(item, str):
            name, concept = f'Idea {index}', item
        elif isinstance(item, dict):
            name = item.get('name', f'Idea {index}')
            concept = item.get('concept', item.get('description'))
        else:
            raise ValueError('Ideas must be strings or objects with name and concept/description')
        if not all(isinstance(value, str) and value.strip() and len(value) <= MAX_TEXT for value in (name, concept)):
            raise ValueError(f'Idea {index} needs nonempty text fields of at most {MAX_TEXT} characters')
        ideas.append({'name': name.strip(), 'concept': concept.strip()})
    return ideas


def tokens(text: str) -> set[str]:
    return {word for word in re.findall(r'\w+', text.casefold()) if word not in STOP and len(word) > 2}


def audit(ideas: list[dict[str, str]]) -> dict:
    if not 1 <= len(ideas) <= MAX_IDEAS:
        raise ValueError('Idea count outside supported range')
    normalised = [' '.join(idea['concept'].casefold().split()) for idea in ideas]
    token_sets = [tokens(idea['concept']) for idea in ideas]
    candidates = []
    for left, a in enumerate(token_sets):
        for right in range(left+1, len(token_sets)):
            b = token_sets[right]
            similarity = len(a & b) / len(a | b) if a or b else 0.0
            exact = bool(normalised[left]) and normalised[left] == normalised[right]
            if exact or similarity >= 0.5:
                candidates.append({'left': left+1, 'right': right+1, 'jaccard': similarity,
                                   'exact_normalised_match': exact})
    candidates.sort(key=lambda pair: (-pair['jaccard'], pair['left'], pair['right']))
    return {'scope': 'lexical-overlap-only', 'novelty': 'NOT_ASSESSED', 'ideas': len(ideas),
            'candidate_pairs': candidates,
            'limitation': 'Shared vocabulary can represent different mechanisms; paraphrases can hide the same mechanism. Review concepts against the task and external evidence.'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.path:
            with args.path.open('rb') as stream:
                raw = stream.read(MAX_INPUT+1)
        elif sys.stdin.isatty():
            raise ValueError('Provide a file or pipe one idea per line / a JSON array')
        else:
            raw = sys.stdin.buffer.read(MAX_INPUT+1)
        if len(raw) > MAX_INPUT:
            raise ValueError('Input exceeds 1 MiB')
        report = audit(parse_ideas(raw.decode('utf-8')))
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0
    except (OSError, ValueError, TypeError) as error:
        print(json.dumps({'error': str(error)}), file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
