#!/usr/bin/env python3
"""Validate an Expo + Convex project in the current working directory.

Usage:
  python scripts/validate_project.py

Exit codes:
  0 success
  1 validation issues found
  2 not an Expo project (no package.json)
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from typing import Iterable

ROOT_FILES = ("package.json", "app.json", "app.config.js", "app.config.ts")

def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="replace")

def _find_project_root(start: Path) -> Path | None:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "package.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None

def _load_package_json(root: Path) -> dict:
    return json.loads(_read_text(root / "package.json"))

def _dep_exists(pkg: dict, name: str) -> bool:
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        if isinstance(pkg.get(key), dict) and name in pkg[key]:
            return True
    return False

def _env_has_convex_url(root: Path) -> tuple[bool, list[Path]]:
    candidates = [root / ".env.local", root / ".env", root / ".env.development", root / ".env.production"]
    found_files = [p for p in candidates if p.exists()]
    pat = re.compile(r"^\s*EXPO_PUBLIC_CONVEX_URL\s*=\s*.+\S\s*$", re.M)
    for p in found_files:
        if pat.search(_read_text(p)):
            return True, found_files
    return False, found_files

def _detect_layout_files(root: Path) -> list[Path]:
    candidates = [
        root / "app" / "_layout.tsx",
        root / "app" / "_layout.jsx",
        root / "src" / "app" / "_layout.tsx",
        root / "src" / "app" / "_layout.jsx",
        root / "App.tsx",
        root / "App.jsx",
    ]
    return [p for p in candidates if p.exists()]

def _file_mentions_provider(p: Path) -> bool:
    txt = _read_text(p)
    return ("ConvexProvider" in txt) and ("ConvexReactClient" in txt)

def main() -> int:
    start = Path.cwd()
    root = _find_project_root(start)
    if root is None:
        print("✗ Could not find package.json (not a Node/Expo project root).")
        return 2

    pkg = _load_package_json(root)

    issues: list[str] = []

    # Dependency checks
    if not _dep_exists(pkg, "expo"):
        issues.append("package.json does not include 'expo' (is this an Expo app?).")
    if not _dep_exists(pkg, "convex"):
        issues.append("package.json does not include 'convex'. Run: npx expo install convex")

    # Convex folder
    convex_dir = root / "convex"
    if not convex_dir.exists():
        issues.append("Missing convex/ directory. Run: npx convex dev (from the project root).")

    # Env var
    has_url, env_files = _env_has_convex_url(root)
    if not has_url:
        if env_files:
            issues.append("Found env file(s) but none contain EXPO_PUBLIC_CONVEX_URL=...")
        else:
            issues.append("No .env.local/.env file found with EXPO_PUBLIC_CONVEX_URL. Run: npx convex dev")

    # Provider wiring
    layout_files = _detect_layout_files(root)
    if not layout_files:
        issues.append("Could not find app/_layout.* (expo-router) or App.* to check provider wiring.")
    else:
        if not any(_file_mentions_provider(p) for p in layout_files):
            msg = "None of the checked entry files mention ConvexProvider + ConvexReactClient:
"
            msg += "\n".join([f"  - {p.relative_to(root)}" for p in layout_files])
            issues.append(msg)

    if issues:
        print("Validation issues found:\n")
        for i, issue in enumerate(issues, start=1):
            print(f"{i}. {issue}")
        print("\nTips:")
        print("- Keep `npx convex dev` running in a separate terminal.")
        print("- Use process.env.EXPO_PUBLIC_CONVEX_URL in the client.")
        print("- Wrap the full app tree with <ConvexProvider client={convex}>.")
        return 1

    print("✓ Looks good: Expo + Convex appear correctly configured.")
    if layout_files:
        print("Checked entry files:")
        for p in layout_files:
            print(f"  - {p.relative_to(root)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
