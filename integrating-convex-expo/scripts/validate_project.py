\
#!/usr/bin/env python3
"""Validate an Expo + Convex project.

This script is designed for agentic use:
- non-interactive
- helpful text output by default
- optional JSON output for automation
- conservative heuristics with clear warnings when a check is approximate

Examples:
  python scripts/validate_project.py
  python scripts/validate_project.py --json
  python scripts/validate_project.py --root /path/to/project
  python scripts/validate_project.py --fail-on-warning

Exit codes:
  0 = no errors (warnings allowed unless --fail-on-warning is set)
  1 = validation issues found
  2 = project root not found or not a Node/Expo project
  3 = internal error while validating
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator

ENTRY_CANDIDATES = (
    "app/_layout.tsx",
    "app/_layout.jsx",
    "app/_layout.js",
    "src/app/_layout.tsx",
    "src/app/_layout.jsx",
    "src/app/_layout.js",
    "App.tsx",
    "App.jsx",
    "App.js",
)

ENV_CANDIDATES = (
    ".env.local",
    ".env",
    ".env.development",
    ".env.production",
    ".env.development.local",
    ".env.production.local",
)

PROVIDER_MARKERS = (
    "ConvexProvider",
    "ConvexProviderWithClerk",
    "ConvexProviderWithAuth",
)

BACKEND_EXTENSIONS = {".ts", ".tsx", ".js", ".jsx"}
IGNORED_DIRS = {
    "node_modules",
    ".git",
    ".next",
    ".expo",
    "dist",
    "build",
    "coverage",
    "ios",
    "android",
}

FUNC_START_RE = re.compile(
    r"export\s+const\s+(?P<name>[A-Za-z0-9_]+)\s*=\s*"
    r"(?P<kind>query|mutation|action|internalQuery|internalMutation|internalAction)\s*\(",
    re.M,
)

OLD_SYNTAX_RE = re.compile(
    r"export\s+const\s+(?P<name>[A-Za-z0-9_]+)\s*=\s*"
    r"(?P<kind>query|mutation|action|internalQuery|internalMutation|internalAction)\s*\(\s*async\b",
    re.M,
)

PACKAGE_MANAGER_HINT = "Install missing packages from the Expo project root and rerun the validator."


@dataclass
class Issue:
    severity: str  # "error" | "warning" | "info"
    code: str
    message: str
    path: str | None = None
    hint: str | None = None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def iter_code_files(root: Path) -> Iterator[Path]:
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in BACKEND_EXTENSIONS:
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        yield path


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(12):
        if (current / "package.json").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent
    return None


def load_package_json(root: Path) -> dict:
    return json.loads(read_text(root / "package.json"))


def dep_exists(pkg: dict, name: str) -> bool:
    for key in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
        value = pkg.get(key)
        if isinstance(value, dict) and name in value:
            return True
    return False


def relative_to_root(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def env_files(root: Path) -> list[Path]:
    return [root / candidate for candidate in ENV_CANDIDATES if (root / candidate).exists()]


def has_convex_url(root: Path) -> tuple[bool, list[Path]]:
    files = env_files(root)
    pattern = re.compile(r"^\s*EXPO_PUBLIC_CONVEX_URL\s*=\s*.+\S\s*$", re.M)
    for file in files:
        if pattern.search(read_text(file)):
            return True, files
    return False, files


def detect_entry_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for candidate in ENTRY_CANDIDATES:
        path = root / candidate
        if path.exists():
            files.append(path)
    return files


def project_mentions_provider(root: Path, entry_files: list[Path]) -> tuple[bool, list[str]]:
    checked: list[str] = []
    for file in entry_files:
        text = read_text(file)
        checked.append(relative_to_root(file, root))
        if any(marker in text for marker in PROVIDER_MARKERS):
            return True, checked
    return False, checked


def count_convex_clients(root: Path) -> tuple[int, list[str]]:
    matches: list[str] = []
    for file in iter_code_files(root):
        if "ConvexReactClient" not in read_text(file):
            continue
        count = read_text(file).count("new ConvexReactClient(")
        if count:
            for _ in range(count):
                matches.append(relative_to_root(file, root))
    return len(matches), matches


def find_backend_files(root: Path) -> list[Path]:
    convex_dir = root / "convex"
    if not convex_dir.exists():
        return []
    files: list[Path] = []
    for path in convex_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.suffix not in BACKEND_EXTENSIONS:
            continue
        if "_generated" in path.parts:
            continue
        files.append(path)
    return files


def first_directive(text: str) -> str | None:
    # Return the first non-empty, non-comment string directive if present.
    in_block_comment = False
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if in_block_comment:
            if "*/" in line:
                in_block_comment = False
            continue
        if line.startswith("/*"):
            in_block_comment = "*/" not in line
            continue
        if line.startswith("//"):
            continue
        if line in ('"use node";', "'use node';", '"use node"', "'use node'"):
            return "use node"
        return None
    return None


def extract_object_literal(source: str, brace_index: int) -> str | None:
    """Extract a JS/TS object literal beginning at source[brace_index] == '{'."""
    if brace_index >= len(source) or source[brace_index] != "{":
        return None

    i = brace_index
    depth = 0
    in_string: str | None = None
    escape = False
    in_line_comment = False
    in_block_comment = False

    while i < len(source):
        ch = source[i]
        nxt = source[i + 1] if i + 1 < len(source) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
            i += 1
            continue

        if in_block_comment:
            if ch == "*" and nxt == "/":
                in_block_comment = False
                i += 2
                continue
            i += 1
            continue

        if in_string is not None:
            if escape:
                escape = False
                i += 1
                continue
            if ch == "\\":
                escape = True
                i += 1
                continue
            if ch == in_string:
                in_string = None
                i += 1
                continue
            i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            i += 2
            continue
        if ch == "/" and nxt == "*":
            in_block_comment = True
            i += 2
            continue
        if ch in ("'", '"', "`"):
            in_string = ch
            i += 1
            continue
        if ch == "{":
            depth += 1
            i += 1
            continue
        if ch == "}":
            depth -= 1
            i += 1
            if depth == 0:
                return source[brace_index:i]
            continue
        i += 1

    return None


def iter_registered_functions(text: str) -> Iterator[dict]:
    for match in FUNC_START_RE.finditer(text):
        name = match.group("name")
        kind = match.group("kind")
        open_paren_index = match.end() - 1  # points to '('
        index = open_paren_index + 1
        while index < len(text) and text[index].isspace():
            index += 1
        if index >= len(text):
            continue
        if text[index] != "{":
            yield {
                "name": name,
                "kind": kind,
                "object_text": None,
                "start": match.start(),
                "end": match.end(),
            }
            continue
        object_text = extract_object_literal(text, index)
        yield {
            "name": name,
            "kind": kind,
            "object_text": object_text,
            "start": match.start(),
            "end": match.end(),
        }


def header_before_handler(object_text: str) -> str:
    handler_index = object_text.find("handler")
    if handler_index == -1:
        return object_text
    return object_text[:handler_index]


def add_issue(
    issues: list[Issue],
    severity: str,
    code: str,
    message: str,
    path: Path | None,
    root: Path,
    hint: str | None = None,
) -> None:
    issues.append(
        Issue(
            severity=severity,
            code=code,
            message=message,
            path=relative_to_root(path, root) if path else None,
            hint=hint,
        )
    )


def scan_backend_file(path: Path, root: Path, issues: list[Issue]) -> None:
    text = read_text(path)
    directive = first_directive(text)
    use_node = directive == "use node"

    if OLD_SYNTAX_RE.search(text):
        add_issue(
            issues,
            "warning",
            "old-registered-syntax",
            "Uses the older registered function syntax. Prefer object syntax with explicit args and returns.",
            path,
            root,
            "Rewrite functions as query({ args, returns, handler }) or mutation({ args, returns, handler }).",
        )

    registered_any = False
    for item in iter_registered_functions(text):
        registered_any = True
        name = item["name"]
        kind = item["kind"]
        object_text = item["object_text"]

        if use_node and kind not in {"action", "internalAction"}:
            add_issue(
                issues,
                "error",
                "use-node-mixed-runtime",
                f'`{name}` is a `{kind}` inside a `"use node"` file. Keep `"use node"` files action-only.',
                path,
                root,
                "Move queries and mutations into a normal runtime file, and keep only actions/internalAction in the Node runtime file.",
            )

        if object_text is None:
            # Probably old shorthand syntax; the old-syntax warning above will explain.
            continue

        header = header_before_handler(object_text)

        if kind in {"query", "mutation", "action"} and "args:" not in header:
            add_issue(
                issues,
                "error",
                "missing-args-validator",
                f"Public function `{name}` is missing an `args` validator.",
                path,
                root,
                "Add `args: { ... }` even when the function takes no arguments (`args: {}`).",
            )

        if kind in {"query", "mutation", "action"} and "returns:" not in header:
            add_issue(
                issues,
                "warning",
                "missing-returns-validator",
                f"Public function `{name}` does not declare a `returns` validator.",
                path,
                root,
                "Prefer explicit `returns: ...`; for no value use `returns: v.null()` and `return null`.",
            )

        if kind in {"query", "internalQuery"}:
            if "Date.now(" in object_text or "new Date(" in object_text:
                add_issue(
                    issues,
                    "warning",
                    "query-uses-time",
                    f"Query `{name}` appears to depend on wall-clock time.",
                    path,
                    root,
                    "Pass time as an argument or store a derived status field instead of using Date.now() in queries.",
                )
            if ".filter(" in object_text:
                add_issue(
                    issues,
                    "warning",
                    "query-uses-filter",
                    f"Query `{name}` uses `.filter()`. This is often a full scan.",
                    path,
                    root,
                    "Prefer `.withIndex(...)` or filter only after narrowing to a small bounded result set.",
                )
            if ".collect(" in object_text:
                add_issue(
                    issues,
                    "warning",
                    "query-uses-collect",
                    f"Query `{name}` uses `.collect()`. This may be unsafe for growing result sets.",
                    path,
                    root,
                    "Use `.take(...)`, `.first()`, or paginated queries for unbounded lists.",
                )

        if kind in {"query", "mutation", "internalQuery", "internalMutation"} and "fetch(" in object_text:
            add_issue(
                issues,
                "warning",
                "fetch-outside-action",
                f"`{name}` appears to call `fetch()` outside an action.",
                path,
                root,
                "Move external API calls into an action or internalAction; keep queries and mutations deterministic.",
            )

    if use_node and not registered_any:
        add_issue(
            issues,
            "info",
            "use-node-no-registered-functions",
            'This file uses `"use node"` but no registered functions were detected. That is fine if it only exports helpers.',
            path,
            root,
        )


def scan_project(root: Path) -> dict:
    issues: list[Issue] = []
    package_json_path = root / "package.json"
    if not package_json_path.exists():
        return {"ok": False, "fatal": "Missing package.json", "issues": issues}

    try:
        pkg = load_package_json(root)
    except json.JSONDecodeError as exc:
        add_issue(
            issues,
            "error",
            "package-json-invalid",
            f"Could not parse package.json: {exc}",
            package_json_path,
            root,
        )
        return {"ok": False, "issues": issues}

    if not dep_exists(pkg, "expo"):
        add_issue(
            issues,
            "error",
            "missing-expo-dependency",
            "package.json does not include `expo`.",
            package_json_path,
            root,
            PACKAGE_MANAGER_HINT,
        )

    if not dep_exists(pkg, "convex"):
        add_issue(
            issues,
            "error",
            "missing-convex-dependency",
            "package.json does not include `convex`.",
            package_json_path,
            root,
            "Run `npx expo install convex` from the project root.",
        )

    convex_dir = root / "convex"
    if not convex_dir.exists():
        add_issue(
            issues,
            "error",
            "missing-convex-directory",
            "Missing `convex/` directory.",
            None,
            root,
            "Run `npx convex dev` from the project root to create the backend directory and generated code.",
        )

    generated_dir = root / "convex" / "_generated"
    if convex_dir.exists() and not generated_dir.exists():
        add_issue(
            issues,
            "warning",
            "missing-generated-code",
            "Missing `convex/_generated/` directory.",
            generated_dir,
            root,
            "Keep `npx convex dev` running and fix any backend compile errors.",
        )

    url_found, env_paths = has_convex_url(root)
    if not url_found:
        if env_paths:
            env_list = ", ".join(relative_to_root(path, root) for path in env_paths)
            add_issue(
                issues,
                "error",
                "missing-convex-url",
                f"Found env files but none define `EXPO_PUBLIC_CONVEX_URL`: {env_list}",
                None,
                root,
                "Run `npx convex dev` or add the variable manually, then restart Metro.",
            )
        else:
            add_issue(
                issues,
                "error",
                "missing-env-files",
                "No env file was found with `EXPO_PUBLIC_CONVEX_URL`.",
                None,
                root,
                "Run `npx convex dev` to generate `.env.local`, then copy the value to EAS environments as needed.",
            )

    entry_files = detect_entry_files(root)
    if not entry_files:
        add_issue(
            issues,
            "warning",
            "entrypoint-not-found",
            "Could not find `app/_layout.*`, `src/app/_layout.*`, or `App.*` to verify provider wiring.",
            None,
            root,
            "If this project uses a custom entry structure, verify the Convex provider is mounted at the real root.",
        )
    else:
        provider_found, checked_files = project_mentions_provider(root, entry_files)
        if not provider_found:
            add_issue(
                issues,
                "error",
                "provider-missing",
                "No known Convex provider marker was found in the main entry files.",
                None,
                root,
                f"Checked: {', '.join(checked_files)}. Add `ConvexProvider`, `ConvexProviderWithClerk`, or `ConvexProviderWithAuth` at the root.",
            )

    client_count, client_files = count_convex_clients(root)
    if client_count == 0:
        add_issue(
            issues,
            "error",
            "convex-client-missing",
            "No `new ConvexReactClient(...)` call was found in the project.",
            None,
            root,
            "Create one root-level client and pass it into the provider.",
        )
    elif client_count > 1:
        add_issue(
            issues,
            "warning",
            "multiple-convex-clients",
            f"Found {client_count} `ConvexReactClient` constructions.",
            None,
            root,
            f"Keep only one app-wide client. Found in: {', '.join(client_files)}",
        )

    backend_files = find_backend_files(root)
    if not backend_files and convex_dir.exists():
        add_issue(
            issues,
            "warning",
            "no-backend-files",
            "The `convex/` directory exists but no backend source files were found outside `_generated`.",
            convex_dir,
            root,
            "Add at least one function file such as `convex/tasks.ts` or run the scaffold script.",
        )

    for file in backend_files:
        scan_backend_file(file, root, issues)

    # ESLint guidance
    if not dep_exists(pkg, "@convex-dev/eslint-plugin"):
        add_issue(
            issues,
            "warning",
            "convex-eslint-plugin-missing",
            "The official Convex ESLint plugin is not listed in package.json.",
            package_json_path,
            root,
            "Install `@convex-dev/eslint-plugin` and enable its recommended rules.",
        )

    # TypeScript strict mode guidance
    tsconfig = root / "tsconfig.json"
    if tsconfig.exists():
        try:
            tsconfig_text = read_text(tsconfig)
            strict_enabled = re.search(r'"strict"\s*:\s*true', tsconfig_text) is not None
            if not strict_enabled:
                add_issue(
                    issues,
                    "warning",
                    "ts-strict-disabled",
                    "tsconfig.json does not appear to enable `strict: true`.",
                    tsconfig,
                    root,
                    "Prefer TypeScript strict mode for Convex projects.",
                )
        except Exception:
            add_issue(
                issues,
                "warning",
                "tsconfig-unreadable",
                "Could not read tsconfig.json to verify strict mode.",
                tsconfig,
                root,
            )

    error_count = sum(1 for issue in issues if issue.severity == "error")
    warning_count = sum(1 for issue in issues if issue.severity == "warning")

    summary = {
        "root": str(root),
        "error_count": error_count,
        "warning_count": warning_count,
        "checked_entry_files": [relative_to_root(path, root) for path in entry_files],
        "checked_backend_files": [relative_to_root(path, root) for path in backend_files],
        "issues": [asdict(issue) for issue in issues],
    }
    summary["ok"] = error_count == 0
    return summary


def render_human(summary: dict) -> str:
    lines: list[str] = []
    lines.append(f"Project root: {summary['root']}")
    lines.append(
        f"Summary: {summary['error_count']} error(s), {summary['warning_count']} warning(s)"
    )
    lines.append("")

    if not summary["issues"]:
        lines.append("✓ No validation issues found.")
        return "\n".join(lines)

    grouped = {"error": [], "warning": [], "info": []}
    for issue in summary["issues"]:
        grouped.setdefault(issue["severity"], []).append(issue)

    for severity in ("error", "warning", "info"):
        bucket = grouped.get(severity, [])
        if not bucket:
            continue
        label = severity.upper()
        lines.append(label)
        lines.append("-" * len(label))
        for issue in bucket:
            where = f" [{issue['path']}]" if issue.get("path") else ""
            lines.append(f"- ({issue['code']}){where} {issue['message']}")
            if issue.get("hint"):
                lines.append(f"    hint: {issue['hint']}")
        lines.append("")

    if summary["issues"]:
        lines.append("Suggested next steps:")
        lines.append("1. Fix the errors first.")
        lines.append("2. Re-run `python scripts/validate_project.py`.")
        lines.append("3. For repeated Convex warnings, add linting with `@convex-dev/eslint-plugin`.")
    return "\n".join(lines).rstrip() + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate an Expo + Convex project for common setup and backend issues."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Project root to validate. Defaults to the nearest parent containing package.json.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit structured JSON instead of human-readable text.",
    )
    parser.add_argument(
        "--fail-on-warning",
        action="store_true",
        help="Return exit code 1 when warnings are present.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        if args.root:
            root = args.root.resolve()
            if not (root / "package.json").exists():
                if args.json:
                    print(json.dumps(
                        {
                            "ok": False,
                            "fatal": "Provided --root does not look like a Node/Expo project (missing package.json).",
                            "root": str(root),
                        },
                        indent=2,
                    ))
                else:
                    print("Could not validate: provided --root is missing package.json.", file=sys.stderr)
                return 2
        else:
            found = find_project_root(Path.cwd())
            if found is None:
                if args.json:
                    print(json.dumps(
                        {
                            "ok": False,
                            "fatal": "Could not find package.json by walking up from the current directory.",
                            "cwd": str(Path.cwd()),
                        },
                        indent=2,
                    ))
                else:
                    print("Could not find package.json by walking up from the current directory.", file=sys.stderr)
                return 2
            root = found

        summary = scan_project(root)

        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(render_human(summary), end="")

        has_errors = summary["error_count"] > 0
        has_warnings = summary["warning_count"] > 0

        if has_errors:
            return 1
        if args.fail_on_warning and has_warnings:
            return 1
        return 0
    except KeyboardInterrupt:
        if args.json:
            print(json.dumps({"ok": False, "fatal": "Validation interrupted."}, indent=2))
        else:
            print("Validation interrupted.", file=sys.stderr)
        return 3
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "fatal": f"Internal validator error: {exc}"}, indent=2))
        else:
            print(f"Internal validator error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
