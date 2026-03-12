\
#!/usr/bin/env python3
"""Validate a Next.js + Convex project for common integration mistakes.

The script is intentionally conservative and heuristic-based: warnings mean
"review this" rather than "this is definitely broken".

Exit codes:
  0 = no errors (or warnings only when not using --strict)
  1 = errors found, or warnings found with --strict
  2 = invalid usage / unreadable root
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

ERROR = "error"
WARN = "warning"
INFO = "info"

DEFAULT_SCAN_EXTS = {".ts", ".tsx", ".js", ".jsx", ".mts", ".cts"}
IGNORE_DIRS = {
    "node_modules",
    ".git",
    ".next",
    "dist",
    "build",
    "coverage",
    ".turbo",
    ".vercel",
    ".cache",
}


@dataclass
class Issue:
    level: str
    code: str
    message: str
    path: str | None = None


def eprint(*parts: object) -> None:
    print(*parts, file=sys.stderr)


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return None
    except OSError as exc:
        eprint(f"[error] Could not read {path}: {exc}")
        return None


def read_json(path: Path) -> dict[str, Any] | None:
    text = read_text(path)
    if text is None:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        eprint(f"[error] Failed to parse JSON in {path}: {exc}")
        return None
    if not isinstance(data, dict):
        eprint(f"[error] Expected JSON object in {path}")
        return None
    return data


def file_exists_any(paths: Iterable[Path]) -> Path | None:
    for path in paths:
        if path.exists():
            return path
    return None


def find_project_files(root: Path, max_files: int) -> list[Path]:
    files: list[Path] = []
    for path in root.rglob("*"):
        if len(files) >= max_files:
            break
        if path.is_dir():
            if path.name in IGNORE_DIRS:
                # pruning via rglob isn't easy; we ignore on file stage too
                continue
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in DEFAULT_SCAN_EXTS:
            files.append(path)
    return files


def functions_dir_from_config(root: Path) -> Path:
    convex_json = root / "convex.json"
    config = read_json(convex_json) if convex_json.exists() else None
    raw = None
    if config:
        raw = config.get("functions")
    if isinstance(raw, str) and raw.strip():
        return (root / raw.strip()).resolve()
    return (root / "convex").resolve()


def normalise_rel(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except Exception:
        return str(path)


def first_nonempty_lines(text: str, limit: int = 8) -> str:
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped:
            lines.append(stripped)
        if len(lines) >= limit:
            break
    return "\n".join(lines)


def has_use_client(text: str) -> bool:
    top = first_nonempty_lines(text, limit=5)
    return '"use client"' in top or "'use client'" in top


def has_use_node(text: str) -> bool:
    top = first_nonempty_lines(text, limit=5)
    return '"use node"' in top or "'use node'" in top


def package_deps(pkg: dict[str, Any]) -> dict[str, str]:
    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = pkg.get(key)
        if isinstance(value, dict):
            for dep, version in value.items():
                if isinstance(dep, str) and isinstance(version, str):
                    deps[dep] = version
    return deps


def add_issue(issues: list[Issue], level: str, code: str, message: str, path: Path | None, root: Path) -> None:
    issues.append(Issue(level=level, code=code, message=message, path=normalise_rel(path, root) if path else None))


def check_package_json(root: Path, issues: list[Issue]) -> dict[str, Any] | None:
    pkg_path = root / "package.json"
    pkg = read_json(pkg_path)
    if pkg is None:
        add_issue(issues, ERROR, "missing-package-json", "package.json not found at the project root.", pkg_path, root)
        return None

    deps = package_deps(pkg)
    if "convex" not in deps:
        add_issue(
            issues,
            ERROR,
            "missing-convex-dependency",
            "Missing `convex` dependency. Install it with `npm install convex`.",
            pkg_path,
            root,
        )
    if "next" not in deps:
        add_issue(
            issues,
            WARN,
            "missing-next-dependency",
            "Could not find a `next` dependency. Review whether this is actually a Next.js repo.",
            pkg_path,
            root,
        )
    if "@convex-dev/eslint-plugin" not in deps:
        add_issue(
            issues,
            WARN,
            "missing-convex-eslint-plugin",
            "Add `@convex-dev/eslint-plugin` so Convex-specific lint rules catch implicit table IDs, missing validators, and query smells.",
            pkg_path,
            root,
        )
    return pkg


def check_typescript(root: Path, issues: list[Issue]) -> None:
    tsconfig = file_exists_any([root / "tsconfig.json", root / "tsconfig.base.json"])
    if tsconfig is None:
        add_issue(
            issues,
            WARN,
            "missing-tsconfig",
            "No tsconfig file found. If this repo is TypeScript-based, enable `compilerOptions.strict`.",
            None,
            root,
        )
        return

    data = read_json(tsconfig)
    if not data:
        return
    strict = (data.get("compilerOptions") or {}).get("strict")
    if strict is not True:
        add_issue(
            issues,
            WARN,
            "ts-strict-disabled",
            "`compilerOptions.strict` is not enabled. Convex code benefits from strict TypeScript.",
            tsconfig,
            root,
        )


def check_functions_dir(root: Path, issues: list[Issue]) -> Path:
    functions_dir = functions_dir_from_config(root)
    if not functions_dir.exists():
        add_issue(
            issues,
            ERROR,
            "missing-functions-dir",
            f"Functions directory not found at `{normalise_rel(functions_dir, root)}`. Run `npx convex dev` or review `convex.json`.",
            functions_dir,
            root,
        )
        return functions_dir

    if not (functions_dir / "schema.ts").exists():
        add_issue(
            issues,
            WARN,
            "missing-schema",
            f"No `schema.ts` found in `{normalise_rel(functions_dir, root)}`. That may be fine for a prototype, but most apps should define schema and indexes explicitly.",
            functions_dir,
            root,
        )

    generated_api = file_exists_any([
        functions_dir / "_generated" / "api.ts",
        functions_dir / "_generated" / "api.js",
    ])
    generated_server = file_exists_any([
        functions_dir / "_generated" / "server.ts",
        functions_dir / "_generated" / "server.js",
    ])
    if generated_api is None or generated_server is None:
        add_issue(
            issues,
            ERROR,
            "missing-generated-files",
            f"Generated Convex files are missing in `{normalise_rel(functions_dir / '_generated', root)}`. Keep `npx convex dev` running or run `npx convex codegen`.",
            functions_dir / "_generated",
            root,
        )
    return functions_dir


def env_var_present(root: Path, key: str) -> bool:
    if os.environ.get(key):
        return True
    for candidate in [root / ".env.local", root / ".env", root / ".env.development.local"]:
        text = read_text(candidate)
        if text and re.search(rf"^\s*{re.escape(key)}\s*=", text, re.MULTILINE):
            return True
    return False


def check_env(root: Path, issues: list[Issue]) -> None:
    if not env_var_present(root, "NEXT_PUBLIC_CONVEX_URL"):
        add_issue(
            issues,
            WARN,
            "missing-convex-url",
            "`NEXT_PUBLIC_CONVEX_URL` was not found in the environment or common env files. Frontend wiring and `convex/nextjs` helpers may fail.",
            None,
            root,
        )


def check_provider_wiring(root: Path, issues: list[Issue]) -> None:
    provider = file_exists_any([
        root / "app" / "ConvexClientProvider.tsx",
        root / "src" / "app" / "ConvexClientProvider.tsx",
        root / "app" / "providers.tsx",
        root / "src" / "app" / "providers.tsx",
        root / "components" / "ConvexClientProvider.tsx",
        root / "src" / "components" / "ConvexClientProvider.tsx",
    ])
    layout = file_exists_any([root / "app" / "layout.tsx", root / "src" / "app" / "layout.tsx"])
    pages_app = file_exists_any([root / "pages" / "_app.tsx", root / "src" / "pages" / "_app.tsx"])

    if provider:
        text = read_text(provider) or ""
        if not has_use_client(text):
            add_issue(
                issues,
                WARN,
                "provider-missing-use-client",
                "The provider file exists but is missing `\"use client\"` at the top.",
                provider,
                root,
            )
        if "ConvexProvider" not in text or "ConvexReactClient" not in text:
            add_issue(
                issues,
                WARN,
                "provider-incomplete",
                "The provider file does not obviously create `ConvexReactClient` and wrap `ConvexProvider`.",
                provider,
                root,
            )
        if layout:
            layout_text = read_text(layout) or ""
            if provider.stem not in layout_text and "ConvexProvider" not in layout_text and "ConvexClientProvider" not in layout_text:
                add_issue(
                    issues,
                    WARN,
                    "layout-missing-provider",
                    "App Router layout does not obviously wrap the tree in the Convex provider.",
                    layout,
                    root,
                )
    elif pages_app:
        text = read_text(pages_app) or ""
        if "ConvexProvider" not in text and "ConvexProviderWith" not in text:
            add_issue(
                issues,
                ERROR,
                "pages-app-missing-provider",
                "Pages Router `_app` exists but does not appear to wrap the app in a Convex provider.",
                pages_app,
                root,
            )
    else:
        add_issue(
            issues,
            WARN,
            "missing-provider-file",
            "Could not find an obvious Convex provider file or Pages Router `_app` wiring. Review frontend setup.",
            None,
            root,
        )


def check_hook_boundaries(root: Path, issues: list[Issue], files: list[Path]) -> None:
    hook_re = re.compile(r"\buse(Query|Mutation|Action|PaginatedQuery|PreloadedQuery)\s*\(")
    for path in files:
        text = read_text(path)
        if not text:
            continue
        if not hook_re.search(text):
            continue
        if has_use_client(text):
            continue
        rel = normalise_rel(path, root)
        if rel.startswith("convex/") or rel.startswith("src/convex/"):
            continue
        add_issue(
            issues,
            WARN,
            "hook-without-use-client",
            "This file appears to use Convex React hooks without `\"use client\"`.",
            path,
            root,
        )


def convex_source_files(functions_dir: Path) -> list[Path]:
    files: list[Path] = []
    if not functions_dir.exists():
        return files
    for path in functions_dir.rglob("*"):
        if path.is_dir():
            continue
        if "_generated" in path.parts:
            continue
        if path.suffix.lower() in DEFAULT_SCAN_EXTS:
            files.append(path)
    return files


def snippets_around_registered_functions(text: str) -> list[str]:
    starts = [m.start() for m in re.finditer(r"\b(?:internalQuery|internalMutation|internalAction|query|mutation|action)\s*\(\s*{", text)]
    snippets: list[str] = []
    for start in starts:
        snippet = text[start:start + 1400]
        snippets.append(snippet)
    return snippets


def check_convex_code(root: Path, functions_dir: Path, issues: list[Issue]) -> None:
    implicit_get = re.compile(r"ctx\.db\.get\(\s*(?!['\"])[^,()]+?\)")
    implicit_patch = re.compile(r"ctx\.db\.(?:patch|replace|delete)\(\s*(?!['\"])[^,()]+")
    schedule_public = re.compile(r"ctx\.scheduler\.(?:runAfter|runAt)\([^,]+,\s*api\.")
    filter_smell = re.compile(r"\.filter\s*\(")
    collect_smell = re.compile(r"\.collect\s*\(")

    for path in convex_source_files(functions_dir):
        text = read_text(path) or ""

        if has_use_node(text) and re.search(r"\b(?:query|mutation|internalQuery|internalMutation)\s*\(", text):
            add_issue(
                issues,
                ERROR,
                "node-file-mixed-runtimes",
                "A file marked with `\"use node\"` appears to define queries or mutations. Keep Node runtime files action-only.",
                path,
                root,
            )

        if implicit_get.search(text) or implicit_patch.search(text):
            add_issue(
                issues,
                WARN,
                "implicit-table-access",
                "Possible implicit table access detected. Prefer explicit table names in `ctx.db.get/patch/replace/delete` calls.",
                path,
                root,
            )

        if collect_smell.search(text) and re.search(r"\b(?:query|internalQuery)\s*\(", text):
            add_issue(
                issues,
                WARN,
                "collect-in-query",
                "A query file uses `.collect()`. Review whether the result set is truly bounded or should be paginated.",
                path,
                root,
            )

        if filter_smell.search(text) and "ctx.db.query(" in text:
            add_issue(
                issues,
                WARN,
                "filter-on-db-query",
                "A Convex database query uses `.filter(...)`. Review whether an index plus `.withIndex(...)` would be better.",
                path,
                root,
            )

        if schedule_public.search(text):
            add_issue(
                issues,
                WARN,
                "schedule-public-function",
                "Scheduled work appears to target a public `api.*` function. Prefer scheduling internal functions.",
                path,
                root,
            )

        for snippet in snippets_around_registered_functions(text):
            if "args:" not in snippet:
                add_issue(
                    issues,
                    WARN,
                    "missing-args-validator",
                    "A registered Convex function may be missing an `args` validator.",
                    path,
                    root,
                )
                break

        for snippet in snippets_around_registered_functions(text):
            if "returns:" not in snippet:
                add_issue(
                    issues,
                    WARN,
                    "missing-returns-validator",
                    "A registered Convex function may be missing a `returns` validator.",
                    path,
                    root,
                )
                break


def check_next_lint_config(root: Path, issues: list[Issue], functions_dir: Path, pkg: dict[str, Any] | None) -> None:
    if pkg is None:
        return

    scripts = pkg.get("scripts") if isinstance(pkg.get("scripts"), dict) else {}
    lint_cmd = scripts.get("lint") if isinstance(scripts, dict) else None
    if not isinstance(lint_cmd, str) or "next lint" not in lint_cmd:
        return

    next_config = file_exists_any([
        root / "next.config.ts",
        root / "next.config.mjs",
        root / "next.config.js",
    ])
    if not next_config:
        return

    text = read_text(next_config) or ""
    functions_name = functions_dir.name
    if "eslint" in text and functions_name not in text and "convex" not in text:
        add_issue(
            issues,
            WARN,
            "next-lint-may-skip-convex",
            "This repo appears to use `next lint`, but `next.config.*` may not include the Convex functions directory in `eslint.dirs`.",
            next_config,
            root,
        )


def render_text_report(root: Path, functions_dir: Path, issues: list[Issue]) -> str:
    errors = [issue for issue in issues if issue.level == ERROR]
    warnings = [issue for issue in issues if issue.level == WARN]

    lines = [
        f"Project root: {root}",
        f"Functions dir: {functions_dir}",
        "",
    ]
    if not issues:
        lines.append("No issues found.")
        return "\n".join(lines)

    def section(title: str, items: list[Issue]) -> None:
        if not items:
            return
        lines.append(title)
        for issue in items:
            location = f" ({issue.path})" if issue.path else ""
            lines.append(f"- [{issue.code}]{location}: {issue.message}")
        lines.append("")

    section("Errors", errors)
    section("Warnings", warnings)
    lines.append(f"Summary: {len(errors)} error(s), {len(warnings)} warning(s)")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a Next.js + Convex project for common wiring, safety, and performance issues."
    )
    parser.add_argument("--root", default=".", help="Project root to inspect (default: current directory).")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON to stdout.")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Return a non-zero exit code when warnings are found.",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=800,
        help="Maximum number of source files to scan outside the Convex functions directory.",
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists() or not root.is_dir():
        eprint(f"[error] Project root does not exist or is not a directory: {root}")
        return 2

    issues: list[Issue] = []

    pkg = check_package_json(root, issues)
    check_typescript(root, issues)
    functions_dir = check_functions_dir(root, issues)
    check_env(root, issues)
    check_provider_wiring(root, issues)

    files = find_project_files(root, args.max_files)
    check_hook_boundaries(root, issues, files)
    check_convex_code(root, functions_dir, issues)
    check_next_lint_config(root, issues, functions_dir, pkg)

    errors = sum(1 for issue in issues if issue.level == ERROR)
    warnings = sum(1 for issue in issues if issue.level == WARN)

    payload = {
        "ok": errors == 0 and (warnings == 0 or not args.strict),
        "root": str(root),
        "functions_dir": str(functions_dir),
        "summary": {"errors": errors, "warnings": warnings, "issues": len(issues)},
        "issues": [asdict(issue) for issue in issues],
    }

    if args.json:
        json.dump(payload, sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        print(render_text_report(root, functions_dir, issues))

    if errors > 0:
        return 1
    if warnings > 0 and args.strict:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
