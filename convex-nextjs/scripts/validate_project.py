#!/usr/bin/env python3
"""Validate a Next.js + Convex project has the usual wiring.

Exit codes:
  0 = OK (no errors)
  1 = Errors found
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

ERROR = "ERROR"
WARN = "WARN"
OK = "OK"


def _print(level: str, msg: str) -> None:
    print(f"[{level}] {msg}")


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception as e:  # noqa: BLE001
        _print(ERROR, f"Failed to parse {path}: {e}")
        return None


def file_contains(path: Path, pattern: str) -> bool:
    try:
        txt = path.read_text(encoding="utf-8", errors="ignore")
    except FileNotFoundError:
        return False
    return re.search(pattern, txt) is not None


def find_any(root: Path, rel_paths: list[str]) -> Path | None:
    for rp in rel_paths:
        p = root / rp
        if p.exists():
            return p
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".", help="Project root (default: .)")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    errors = 0
    warnings = 0

    _print(OK, f"Validating project at: {root}")

    pkg = read_json(root / "package.json")
    if pkg is None:
        _print(ERROR, "package.json not found (are you pointing at the repo root?)")
        return 1

    deps = {}
    deps.update(pkg.get("dependencies", {}) or {})
    deps.update(pkg.get("devDependencies", {}) or {})
    if "convex" not in deps:
        _print(ERROR, "Missing 'convex' dependency. Run: npm install convex")
        errors += 1
    else:
        _print(OK, f"Found convex dependency: {deps['convex']}")
    if "next" not in deps:
        _print(WARN, "Could not find 'next' dependency (is this a Next.js app?)")
        warnings += 1

    convex_dir = root / "convex"
    if not convex_dir.exists():
        _print(ERROR, "Missing convex/ directory. Run: npx convex dev (it creates convex/)")
        errors += 1
    else:
        _print(OK, "Found convex/ directory")

    generated_api = find_any(root, ["convex/_generated/api.ts", "convex/_generated/api.js"])
    if generated_api is None:
        _print(
            ERROR,
            "Missing convex/_generated/api.(ts|js). Keep `npx convex dev` running or run `npx convex codegen`.",
        )
        errors += 1
    else:
        _print(OK, f"Found generated api: {generated_api.relative_to(root)}")

    env_local = root / ".env.local"
    env_has = False
    if os.environ.get("NEXT_PUBLIC_CONVEX_URL"):
        env_has = True
    if env_local.exists():
        txt = env_local.read_text(encoding="utf-8", errors="ignore")
        if re.search(r"^\s*NEXT_PUBLIC_CONVEX_URL\s*=", txt, re.MULTILINE):
            env_has = True
    if not env_has:
        _print(
            WARN,
            "NEXT_PUBLIC_CONVEX_URL not found in environment or .env.local. Frontend and convex/nextjs SSR helpers may fail.",
        )
        warnings += 1
    else:
        _print(OK, "NEXT_PUBLIC_CONVEX_URL appears to be set")

    # App Router: provider + layout wiring.
    provider = find_any(
        root,
        [
            "app/ConvexClientProvider.tsx",
            "src/app/ConvexClientProvider.tsx",
            "app/providers.tsx",
            "src/app/providers.tsx",
        ],
    )
    layout = find_any(root, ["app/layout.tsx", "src/app/layout.tsx"])
    pages_app = find_any(root, ["pages/_app.tsx", "src/pages/_app.tsx"])

    if provider:
        _print(OK, f"Found provider file: {provider.relative_to(root)}")
        if not file_contains(provider, r"\"use client\""):
            _print(WARN, "Provider file is missing \"use client\". ConvexProvider wiring should be a Client Component.")
            warnings += 1
        if not file_contains(provider, r"ConvexReactClient") or not file_contains(provider, r"ConvexProvider"):
            _print(WARN, "Provider file does not appear to create ConvexReactClient + wrap ConvexProvider.")
            warnings += 1
    elif pages_app:
        _print(WARN, "No App Router provider found; pages/_app.tsx exists, assuming Pages Router.")
        warnings += 1
        if not file_contains(pages_app, r"ConvexProvider") and not file_contains(pages_app, r"ConvexProviderWith"):
            _print(ERROR, "pages/_app.tsx does not appear to wrap Convex provider.")
            errors += 1
    else:
        _print(
            WARN,
            "Could not find Convex client provider (expected app/ConvexClientProvider.tsx or pages/_app.tsx wiring).",
        )
        warnings += 1

    if layout and provider:
        if not file_contains(layout, r"ConvexClientProvider"):
            _print(WARN, "app/layout.tsx does not reference ConvexClientProvider. Ensure the provider wraps the app.")
            warnings += 1
        else:
            _print(OK, "app/layout.tsx references ConvexClientProvider")

    if errors == 0:
        _print(OK, f"Validation passed with {warnings} warning(s).")
        return 0

    _print(ERROR, f"Validation failed with {errors} error(s) and {warnings} warning(s).")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
