#!/usr/bin/env python3
"""Offline structural checks for this package; not a general YAML/Markdown parser.

Checks the simple scalar frontmatter layout used here, local Markdown link
paths and common heading anchors, evaluation schemas, and an optional manifest.
It neither follows external links nor grades writing or model behavior.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

from evaluate import ROOT, load_cases

IGNORED_DIRS = {"__pycache__", ".pytest_cache", ".git"}
IGNORED_NAMES = {".DS_Store"}


def package_files(root: Path) -> list[Path]:
    files = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if any(part in IGNORED_DIRS for part in relative.parts) or path.name in IGNORED_NAMES or path.suffix == ".pyc":
            continue
        if path.is_symlink():
            raise ValueError(f"Symlinks are not supported in the package: {relative}")
        if path.is_file():
            files.append(path)
    return sorted(files)


def check_frontmatter(root: Path) -> dict[str, str]:
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must begin with YAML frontmatter delimiters")
    fields: dict[str, str] = {}
    metadata: dict[str, str] = {}
    in_metadata = False
    for line in match.group(1).splitlines():
        if not line.strip():
            continue
        field = re.fullmatch(r"(  )?([a-z][a-z0-9-]*):(?: (.*))?", line)
        if not field:
            raise ValueError(f"Unsupported frontmatter layout: {line!r}; use single-line scalar fields")
        indent, key, raw = field.groups()
        if indent:
            if not in_metadata or raw is None:
                raise ValueError("Only metadata supports indented scalar values")
            destination = metadata
        else:
            if key == "metadata":
                if raw is not None or key in fields:
                    raise ValueError("metadata must be one mapping")
                fields[key] = "mapping"
                in_metadata = True
                continue
            in_metadata = False
            destination = fields
        if key in destination or raw is None:
            raise ValueError(f"Missing or duplicate frontmatter value: {key}")
        value = json.loads(raw) if raw.startswith('"') else raw
        if not isinstance(value, str):
            raise ValueError(f"Frontmatter value must be a string: {key}")
        destination[key] = value
    name = fields.get("name", "")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
        raise ValueError("Invalid skill name")
    if root.name != name:
        raise ValueError("Skill name must match the enclosing directory")
    if not 1 <= len(fields.get("description", "")) <= 1024:
        raise ValueError("Description must contain 1 to 1024 characters")
    if not re.fullmatch(r"\d+\.\d+\.\d+", metadata.get("version", "")):
        raise ValueError("Expected a three-part version string in metadata")
    if len(text.splitlines()) >= 500:
        raise ValueError("The package's core instruction budget is under 500 lines")
    fields["version"] = metadata["version"]
    return fields


def without_fences(text: str) -> str:
    lines: list[str] = []
    fence_char, fence_length = "", 0
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            fence = marker.group(1)
            if not fence_char:
                fence_char, fence_length = fence[0], len(fence)
            elif fence[0] == fence_char and len(fence) >= fence_length:
                fence_char, fence_length = "", 0
            lines.append("")
        else:
            lines.append("" if fence_char else line)
    return "\n".join(lines)


def anchors(path: Path) -> set[str]:
    text = without_fences(path.read_text(encoding="utf-8"))
    found = set(re.findall(r'\bid=["\']([^"\']+)["\']', text))
    counts: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", text, flags=re.MULTILINE):
        heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
        slug = re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
        index = counts.get(slug, 0)
        counts[slug] = index + 1
        found.add(f"{slug}-{index}" if index else slug)
    return found


def check_links(root: Path, files: list[Path]) -> int:
    checked = 0
    pattern = re.compile(r"!?\[[^\]\n]+\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")
    for source in files:
        if source.suffix != ".md":
            continue
        text = without_fences(source.read_text(encoding="utf-8"))
        for target in pattern.findall(text):
            target = target.strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme or parsed.netloc:
                continue
            path = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source.resolve()
            if not path.is_relative_to(root.resolve()) or not path.exists():
                raise ValueError(f"Invalid local link in {source.relative_to(root)}: {target}")
            if parsed.fragment and path.suffix == ".md" and unquote(parsed.fragment) not in anchors(path):
                raise ValueError(f"Missing heading anchor in {source.relative_to(root)}: {target}")
            checked += 1
    return checked


def verify_manifest(root: Path, files: list[Path], version: str) -> str:
    manifest_path = root / "MANIFEST.json"
    if not manifest_path.exists():
        return "not present (development checkout)"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != 1 or manifest.get("skill_name") != "write-good-docs" or manifest.get("version") != version:
        raise ValueError("Manifest metadata does not match the package")
    expected = manifest.get("files")
    actual = {p.relative_to(root).as_posix(): p for p in files if p != manifest_path}
    if not isinstance(expected, dict) or set(expected) != set(actual):
        raise ValueError("Manifest file inventory does not match the package")
    for relative, path in actual.items():
        content = path.read_bytes()
        entry = expected[relative]
        if not isinstance(entry, dict) or entry.get("bytes") != len(content) or entry.get("sha256") != hashlib.sha256(content).hexdigest():
            raise ValueError(f"Manifest content mismatch: {relative}")
    return f"verified {len(actual)} file hashes"


def validate(root: Path = ROOT) -> dict[str, object]:
    files = package_files(root)
    frontmatter = check_frontmatter(root)
    links = check_links(root, files)
    cases = load_cases(root)
    data = json.loads((root / "evals/evals.json").read_text(encoding="utf-8"))
    if data.get("skill_version") != frontmatter["version"]:
        raise ValueError("Evaluation metadata version does not match the skill")
    declared = {relative for case in cases for relative in case["files"]}
    supplied = {p.relative_to(root).as_posix() for p in files if p.is_relative_to(root / "evals/fixtures")}
    if declared != supplied:
        raise ValueError("Orphaned or undeclared evaluation fixture")
    return dict(status="passed", version=frontmatter["version"], files=len(files),
                local_markdown_targets=links, evaluation_cases=len(cases),
                manifest=verify_manifest(root, files, frontmatter["version"]),
                limitation="Structural checks only; not a full YAML/Markdown implementation, external-link audit, or model benchmark.")


def main() -> int:
    try:
        print(json.dumps(validate(), indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, re.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
