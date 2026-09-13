#!/usr/bin/env python3
"""Check an explicitly selected opening against a dated journal profile, not submission readiness."""
from __future__ import annotations
import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

PROFILES = {
    'nature-communications-article': {
        'journal': 'Nature Communications', 'article_type': 'Article',
        'opening_heading': 'Abstract', 'max_words': 200, 'limit_kind': 'mandatory',
        'citation_policy': 'no references', 'reviewed': '2026-09-13',
        'source_url': 'https://www.nature.com/ncomms/submit/article',
    },
    'nature-article': {
        'journal': 'Nature', 'article_type': 'Article',
        'opening_heading': 'Summary paragraph', 'max_words': 200, 'limit_kind': 'advisory',
        'citation_policy': 'fully referenced summary', 'reviewed': '2026-09-13',
        'source_url': 'https://www.nature.com/nature/for-authors/formatting-guide',
    },
}
MAX_BYTES = 2 * 1024 * 1024


def validate_profile(profile):
    if not isinstance(profile, dict) or set(profile) != set(PROFILES['nature-article']):
        raise ValueError('Profile must contain exactly the documented profile fields')
    for key in ('journal', 'article_type', 'opening_heading', 'citation_policy', 'reviewed', 'source_url'):
        if not isinstance(profile[key], str) or not profile[key].strip():
            raise ValueError(f'Profile {key} must be nonempty text')
    if type(profile['max_words']) is not int or not 1 <= profile['max_words'] <= 10000:
        raise ValueError('Invalid max_words')
    if profile['limit_kind'] not in {'mandatory', 'advisory'}:
        raise ValueError('limit_kind must be mandatory or advisory')
    date.fromisoformat(profile['reviewed'])
    url = urlsplit(profile['source_url'])
    if url.scheme != 'https' or not url.netloc or url.username or url.password:
        raise ValueError('Profile source must be a credential-free HTTPS URL')
    return profile


def bounded_text(path):
    with Path(path).open('rb') as stream:
        raw = stream.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds the 2 MiB metadata/text bound')
    return raw.decode('utf-8-sig')


def extract_opening(text, heading):
    """ATX Markdown only; no guessed first paragraph, duplicate heading, or nested structure."""
    lines = text.splitlines()
    headers = []
    fence = None
    for index, line in enumerate(lines):
        marker = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if marker:
            token, rest = marker.groups()
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not rest.strip():
                fence = None
            continue
        if fence:
            continue
        match = re.match(r'^ {0,3}(#{1,6})[ \t]+(.+?)\s*$', line)
        if match:
            name = re.sub(r'\s+#+\s*$', '', match[2]).strip()
            headers.append((index, len(match[1]), name))
    if fence:
        raise ValueError('Unclosed fenced block makes the document ambiguous')
    hits = [entry for entry in headers if entry[2].casefold() == heading.casefold()]
    if len(hits) != 1:
        raise ValueError('Exactly one explicit opening heading is required; use --opening-only for a separate plain-text opening')
    start, level, _ = hits[0]
    end = len(lines)
    for index, depth, _ in headers:
        if index <= start:
            continue
        if depth > level:
            raise ValueError('Opening contains a nested heading; supply the opening separately')
        end = index
        break
    opening = '\n'.join(lines[start + 1:end]).strip()
    if re.search(r'^ {0,3}(`{3,}|~{3,})', opening, re.M):
        raise ValueError('Opening contains a fenced block; supply plain prose')
    return opening


def check(text, profile, opening_only=False):
    profile = validate_profile(profile)
    opening = text.strip() if opening_only else extract_opening(text, profile['opening_heading'])
    if not opening:
        raise ValueError('Opening is empty')
    count = len(opening.split())
    over = count > profile['max_words']
    state = 'over-limit' if over and profile['limit_kind'] == 'mandatory' else 'over-guidance' if over else 'within-configured-limit'
    return {'scope': 'opening-length-only', 'submission_readiness': 'NOT_ASSESSED',
            'profile': dict(profile), 'word_count': count, 'count_method': 'whitespace-separated tokens',
            'status': state, 'citation_policy_checked': False,
            'next_check': 'Verify current journal policy, citations, counting conventions, and all other submission requirements'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    profile_group = parser.add_mutually_exclusive_group(required=True)
    profile_group.add_argument('--profile', choices=sorted(PROFILES))
    profile_group.add_argument('--profile-file', type=Path)
    parser.add_argument('--opening-only', action='store_true', help='Input is only the chosen opening text, not a manuscript')
    options = parser.parse_args()
    try:
        profile = PROFILES[options.profile] if options.profile else json.loads(bounded_text(options.profile_file))
        report = check(bounded_text(options.input), profile, options.opening_only)
        print(json.dumps(report, indent=2))
        return {'within-configured-limit': 0, 'over-limit': 1, 'over-guidance': 2}[report['status']]
    except (OSError, UnicodeError, ValueError, TypeError) as error:
        print(json.dumps({'status': 'unverified', 'submission_readiness': 'NOT_ASSESSED', 'error': str(error)}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
