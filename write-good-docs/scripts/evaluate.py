#!/usr/bin/env python3
"""Export closed writing cases and check mechanical constraints; never call a model.

Python 3.10+, standard library only. A mechanical pass always requires semantic
review. Commands appearing in source fixtures are never executed by this tool.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MAX_OUTPUT_BYTES = 10_000_000
CHECK_FIELDS: dict[str, set[str]] = {
    "contains": {"type", "value"},
    "count": {"type", "value", "count"},
    "in_order": {"type", "values"},
    "equals_fixture": {"type", "file"},
    "unchanged_outside": {"type", "file", "start", "end"},
    "not_regex": {"type", "value"},
    "max_words": {"type", "count"},
}


def package_path(root: Path, relative: str) -> Path:
    """Resolve a package file without permitting absolute paths or escapes."""
    if not isinstance(relative, str) or not relative or "\\" in relative:
        raise ValueError(f"Invalid relative package path: {relative!r}")
    p = Path(relative)
    if p.is_absolute() or ".." in p.parts:
        raise ValueError(f"Unsafe package path: {relative!r}")
    resolved = (root / p).resolve()
    if not resolved.is_relative_to(root.resolve()):
        raise ValueError(f"Package path escapes the root: {relative!r}")
    if not resolved.is_file():
        raise ValueError(f"Package file not found: {relative}")
    return resolved


def normalized(text: str) -> str:
    """Ignore platform line endings and trailing newlines, not internal edits."""
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


def validate_check(check: dict[str, Any], case: dict[str, Any], root: Path) -> None:
    if not isinstance(check, dict):
        raise ValueError("A check must be an object")
    kind = check.get("type")
    if not isinstance(kind, str) or kind not in CHECK_FIELDS:
        raise ValueError(f"Unknown check type: {kind!r}")
    if set(check) != CHECK_FIELDS[kind]:
        raise ValueError(f"Unexpected or missing fields for {kind}: {sorted(check)}")
    for key in ("value", "start", "end"):
        if key in check and (not isinstance(check[key], str) or not check[key]):
            raise ValueError(f"{kind}.{key} must be a nonempty string")
    if "count" in check and (type(check["count"]) is not int or check["count"] < 1):
        raise ValueError(f"{kind}.count must be a positive integer")
    if kind == "in_order":
        values = check["values"]
        if not isinstance(values, list) or not values or any(not isinstance(x, str) or not x for x in values):
            raise ValueError("in_order.values must be nonempty strings")
    if kind == "not_regex":
        re.compile(check["value"])
    if "file" in check:
        if check["file"] not in case["files"]:
            raise ValueError("A file-based check must use a declared fixture")
        source = normalized(package_path(root, check["file"]).read_text(encoding="utf-8"))
        if kind == "unchanged_outside":
            start, end = check["start"], check["end"]
            if source.count(start) != 1 or source.count(end) != 1:
                raise ValueError("Edit-boundary markers must occur exactly once in the fixture")
            if source.index(end) < source.index(start) + len(start):
                raise ValueError("Edit-boundary markers are not in source order")


def load_cases(root: Path = ROOT) -> list[dict[str, Any]]:
    data = json.loads((root / "evals/evals.json").read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("Expected evaluation schema_version 1")
    if data.get("skill_name") != "write-good-docs":
        raise ValueError("Incorrect evaluation skill_name")
    cases = data.get("evals")
    if not isinstance(cases, list) or not cases:
        raise ValueError("evals must be a nonempty array")
    ids: set[str] = set()
    for case in cases:
        if not isinstance(case, dict):
            raise ValueError("Each case must be an object")
        for key in ("id", "name", "prompt", "expected_output"):
            if not isinstance(case.get(key), str) or not case[key].strip():
                raise ValueError(f"Missing or invalid case field: {key}")
        if not re.fullmatch(r"Q[0-9]{2}", case["id"]) or case["id"] in ids:
            raise ValueError(f"Invalid or duplicate case id: {case['id']}")
        ids.add(case["id"])
        for key in ("files", "hard_gates", "assertions"):
            items = case.get(key)
            if not isinstance(items, list) or not items or any(not isinstance(x, str) or not x.strip() for x in items):
                raise ValueError(f"{case['id']}.{key} must be nonempty strings")
        if len(set(case["files"])) != len(case["files"]):
            raise ValueError(f"Duplicate input file in {case['id']}")
        for relative in case["files"]:
            if not package_path(root, relative).read_text(encoding="utf-8").strip():
                raise ValueError(f"Empty fixture: {relative}")
        if not isinstance(case.get("checks"), list):
            raise ValueError(f"{case['id']}.checks must be an array")
        for check in case["checks"]:
            validate_check(check, case, root)
    return cases


def get_case(identifier: str, root: Path = ROOT) -> dict[str, Any]:
    for case in load_cases(root):
        if case["id"] == identifier:
            return case
    raise ValueError(f"Unknown case {identifier!r}; use the list command")


def render_task(case: dict[str, Any], root: Path = ROOT) -> str:
    """Export only writer-facing input; grading material must stay separate."""
    parts = [case["prompt"].strip(), "All supplied product facts are fictional test material. Use only this material; do not browse for additional facts."]
    for relative in case["files"]:
        content = package_path(root, relative).read_text(encoding="utf-8").rstrip("\n")
        parts.append(f'<source name="{Path(relative).name}">\n{content}\n</source>')
    return "\n\n".join(parts) + "\n"


def prepare_case(case: dict[str, Any], out: Path, root: Path = ROOT) -> Path:
    destination = out.resolve()
    if destination.is_relative_to(root.resolve()):
        raise ValueError("Keep evaluation outputs outside the installed skill directory")
    task = render_task(case, root)
    destination.mkdir(parents=True, exist_ok=False)
    target = destination / "task.md"
    target.write_text(task, encoding="utf-8")
    return target


def check_output(case: dict[str, Any], output: str, root: Path = ROOT) -> dict[str, Any]:
    text = normalized(output)
    results: list[dict[str, Any]] = [dict(check="nonempty", passed=bool(text.strip()))]
    for check in case["checks"]:
        validate_check(check, case, root)
        kind = check["type"]
        detail: dict[str, Any] = {}
        if kind == "contains":
            passed = check["value"] in text
        elif kind == "count":
            actual = text.count(check["value"])
            passed = actual == check["count"]
            detail["actual_count"] = actual
        elif kind == "in_order":
            cursor, passed = 0, True
            for value in check["values"]:
                index = text.find(value, cursor)
                if index < 0:
                    passed = False
                    detail["first_missing_or_out_of_order"] = value
                    break
                cursor = index + len(value)
        elif kind == "equals_fixture":
            original = package_path(root, check["file"]).read_text(encoding="utf-8")
            passed = text == normalized(original)
        elif kind == "unchanged_outside":
            original = normalized(package_path(root, check["file"]).read_text(encoding="utf-8"))
            prefix = original[:original.index(check["start"]) + len(check["start"])]
            suffix = original[original.index(check["end"]):]
            passed = len(text) >= len(prefix) + len(suffix) and text.startswith(prefix) and text.endswith(suffix)
        elif kind == "not_regex":
            passed = re.search(check["value"], text, flags=re.MULTILINE) is None
        elif kind == "max_words":
            actual = len(text.split())
            passed = actual <= check["count"]
            detail["actual_words"] = actual
        else:  # validate_check rejects this path; keep failure explicit.
            raise ValueError(f"Unhandled check type: {kind}")
        results.append(dict(check=check, passed=passed, **detail))
    passed = all(item["passed"] for item in results)
    return dict(case_id=case["id"], status="mechanical_pass" if passed else "mechanical_fail",
                semantic_review_required=True, checks=results,
                note="Apply all semantic and safety gates and inspect relevant tool traces. This is not an overall quality grade.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="List available case identifiers")
    prepare = sub.add_parser("prepare", help="Export prompt and fixtures without grading material")
    prepare.add_argument("--case", required=True)
    prepare.add_argument("--out", required=True, type=Path)
    check = sub.add_parser("check", help="Check mechanical constraints; semantic review is still required")
    check.add_argument("--case", required=True)
    check.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.command == "list":
            for case in load_cases():
                print(f"{case['id']}\t{case['name']}")
            return 0
        case = get_case(args.case)
        if args.command == "prepare":
            print(prepare_case(case, args.out))
            return 0
        if args.output.stat().st_size > MAX_OUTPUT_BYTES:
            raise ValueError(f"Output exceeds the {MAX_OUTPUT_BYTES}-byte input limit")
        report = check_output(case, args.output.read_text(encoding="utf-8"))
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["status"] == "mechanical_pass" else 1
    except (OSError, ValueError, TypeError, re.error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
