#!/usr/bin/env python3
"""Draft an llms.txt file from a documentation tree.

The output is intentionally conservative: a concise curated index that an agent
or human should review before publishing.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import urllib.parse
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

EXCLUDED_DIRS = {".git", "node_modules", ".next", "dist", "build", "target", ".venv", "venv", "__pycache__"}
DOC_EXTS = {".md", ".mdx", ".rst", ".html", ".htm"}
MAX_FILE_BYTES = 200_000


def iter_docs(root: Path, max_files: int) -> Iterable[Path]:
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIRS and not d.startswith(".")]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() not in DOC_EXTS:
                continue
            if filename.lower() in {"llms.txt", "llms-full.txt"}:
                continue
            yield path
            count += 1
            if count >= max_files:
                return


def read_text(path: Path) -> str:
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return ""
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def strip_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    meta: Dict[str, str] = {}
    if text.startswith("---\n"):
        end = text.find("\n---", 4)
        if end != -1:
            fm = text[4:end]
            text = text[end + 4 :]
            for line in fm.splitlines():
                if ":" in line:
                    key, value = line.split(":", 1)
                    meta[key.strip().lower()] = value.strip().strip('"\'')
    return meta, text


def first_heading(text: str) -> Optional[str]:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+?)\s*$", line.strip())
        if m:
            return re.sub(r"\s+", " ", m.group(1)).strip()
        html = re.search(r"<h1[^>]*>(.*?)</h1>", line, re.I)
        if html:
            return re.sub(r"<[^>]+>|\s+", " ", html.group(1)).strip()
    return None


def first_description(meta: Dict[str, str], text: str) -> str:
    for key in ("description", "summary", "excerpt"):
        if meta.get(key):
            return compact(meta[key], 180)
    body = re.sub(r"```.*?```", "", text, flags=re.S)
    body = re.sub(r"<[^>]+>", " ", body)
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("---") or stripped.startswith("import "):
            continue
        if stripped.startswith(">"):
            stripped = stripped.lstrip("> ")
        if len(stripped) >= 30:
            return compact(stripped, 180)
    return "Reference page."


def compact(text: str, limit: int) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "…"


def title_for(path: Path, root: Path, text: str, meta: Dict[str, str]) -> str:
    for key in ("title", "name"):
        if meta.get(key):
            return compact(meta[key], 80)
    heading = first_heading(text)
    if heading:
        return compact(heading, 80)
    stem = path.stem.replace("-", " ").replace("_", " ").strip()
    return stem.title() or root.name


def url_for(path: Path, root: Path, site_url: str, preserve_extensions: bool) -> str:
    rel = path.relative_to(root).as_posix()
    if not preserve_extensions:
        if rel.endswith("/index.md") or rel.endswith("/index.mdx"):
            rel = rel.rsplit("/", 1)[0] + "/"
        elif Path(rel).suffix.lower() in {".md", ".mdx", ".rst"}:
            rel = rel[: -len(Path(rel).suffix)]
    return urllib.parse.urljoin(site_url.rstrip("/") + "/", rel)


def section_for(path: Path, root: Path) -> str:
    rel = path.relative_to(root)
    if len(rel.parts) <= 1:
        return "Core"
    first = rel.parts[0].replace("-", " ").replace("_", " ").strip().title()
    common = {
        "Docs": "Guides",
        "Guide": "Guides",
        "Guides": "Guides",
        "Reference": "Reference",
        "Api": "API",
        "Sdk": "SDK",
        "Examples": "Examples",
        "Tutorials": "Tutorials",
    }
    return common.get(first, first or "Reference")


def generate(root: Path, site_url: str, title: str, summary: str, max_links: int, preserve_extensions: bool) -> str:
    entries: List[Tuple[str, str, str, str]] = []
    for path in iter_docs(root, max_links * 5):
        text = read_text(path)
        if not text:
            continue
        meta, body = strip_frontmatter(text)
        page_title = title_for(path, root, body, meta)
        desc = first_description(meta, body)
        url = url_for(path, root, site_url, preserve_extensions)
        entries.append((section_for(path, root), page_title, url, desc))

    # Prioritize common entry points, then path-derived order.
    priority_words = ("quickstart", "getting started", "overview", "introduction", "api", "reference", "auth", "error", "example", "changelog")
    def priority(entry: Tuple[str, str, str, str]) -> Tuple[int, str, str]:
        title_l = entry[1].lower() + " " + entry[2].lower()
        score = min((i for i, w in enumerate(priority_words) if w in title_l), default=99)
        return (score, entry[0], entry[1])

    entries = sorted(entries, key=priority)[:max_links]
    sections: Dict[str, List[Tuple[str, str, str]]] = {}
    for section, page_title, url, desc in entries:
        sections.setdefault(section, []).append((page_title, url, desc))

    lines: List[str] = [f"# {title}", "", f"> {summary}", ""]
    lines.append("This file is a generated draft. Review the links and descriptions before publishing.")
    for section in preferred_section_order(sections):
        lines.append("")
        lines.append(f"## {section}")
        lines.append("")
        for page_title, url, desc in sections[section]:
            lines.append(f"- [{page_title}]({url}): {desc}")
    lines.append("")
    lines.append("## Optional")
    lines.append("")
    lines.append("- Add links to large references, archived docs, exhaustive API pages, or secondary examples here when they are useful but not essential.")
    return "\n".join(lines).rstrip() + "\n"


def preferred_section_order(sections: Dict[str, List[Tuple[str, str, str]]]) -> List[str]:
    preferred = ["Core", "Guides", "API", "SDK", "Reference", "Examples", "Tutorials"]
    ordered = [s for s in preferred if s in sections]
    ordered.extend(sorted(s for s in sections if s not in ordered))
    return ordered


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a draft llms.txt from a docs directory.")
    parser.add_argument("root", help="Documentation root directory.")
    parser.add_argument("--site-url", required=True, help="Public base URL corresponding to the docs root.")
    parser.add_argument("--title", help="Title for the llms.txt H1. Defaults to directory name.")
    parser.add_argument("--summary", default="Concise index of canonical documentation and references for AI agents.")
    parser.add_argument("--max-links", type=int, default=40, help="Maximum links to include. Default: 40.")
    parser.add_argument("--output", help="Write to file instead of stdout.")
    parser.add_argument("--preserve-extensions", action="store_true", help="Keep .md/.mdx/.rst extensions in generated URLs.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    root = Path(args.root)
    if not root.exists() or not root.is_dir():
        print('{"error":{"code":"invalid_root","message":"root must be an existing directory"}}', file=sys.stderr)
        return 2
    title = args.title or root.name.replace("-", " ").title()
    output = generate(root, args.site_url, title, args.summary, max(1, args.max_links), args.preserve_extensions)
    size = len(output.encode("utf-8", errors="ignore"))
    if size > 50_000:
        print(f"warning: generated llms.txt is {size} bytes; consider reducing --max-links", file=sys.stderr)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
