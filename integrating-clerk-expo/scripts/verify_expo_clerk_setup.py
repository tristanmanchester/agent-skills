#!/usr/bin/env python3
"""verify_expo_clerk_setup.py

Static checks for integrating Clerk into a React Native Expo project.

Usage:
  python scripts/verify_expo_clerk_setup.py <project_root>

Exit codes:
  0  All required checks passed (or only minor warnings).
  1  One or more required checks failed.
  2  Invalid arguments.
  3  Project files not found (e.g. package.json missing).
"""

from __future__ import annotations

import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Tuple


EXCLUDE_DIRS = {
    "node_modules",
    ".git",
    ".expo",
    "dist",
    "build",
    "ios",
    "android",
    ".turbo",
    ".next",
    ".cache",
    ".yarn",
}


@dataclass
class CheckResult:
    name: str
    ok: bool
    details: str
    required: bool = True


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def _load_package_json(project_root: Path) -> Tuple[Optional[dict], Optional[str]]:
    pkg_path = project_root / "package.json"
    if not pkg_path.exists():
        return None, f"Missing {pkg_path}"
    try:
        return json.loads(_read_text(pkg_path)), None
    except Exception as e:
        return None, f"Failed to parse package.json: {e}"


def _deps(pkg: dict) -> dict:
    deps: dict = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        val = pkg.get(key, {})
        if isinstance(val, dict):
            deps.update(val)
    return deps


def _walk_source_files(project_root: Path) -> Iterable[Path]:
    for root, dirs, files in os.walk(project_root):
        # prune dirs
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith(".")]
        for fn in files:
            if fn.endswith((".ts", ".tsx", ".js", ".jsx")):
                yield Path(root) / fn


def _find_in_files(project_root: Path, pattern: re.Pattern, max_hits: int = 20) -> List[Tuple[Path, int, str]]:
    hits: List[Tuple[Path, int, str]] = []
    for p in _walk_source_files(project_root):
        try:
            text = _read_text(p)
        except Exception:
            continue
        for idx, line in enumerate(text.splitlines(), start=1):
            if pattern.search(line):
                hits.append((p, idx, line.strip()))
                if len(hits) >= max_hits:
                    return hits
    return hits


def _env_has_publishable_key(project_root: Path) -> Tuple[bool, str]:
    env_path = project_root / ".env"
    if not env_path.exists():
        return False, "No .env file found"
    text = _read_text(env_path)
    # Match key=value and allow whitespace
    if re.search(r"^\s*EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY\s*=\s*\S+", text, flags=re.M):
        return True, "EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY found"
    return False, "EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY not found in .env"


def main(argv: List[str]) -> int:
    if len(argv) != 2:
        print(__doc__.strip())
        return 2

    project_root = Path(argv[1]).resolve()
    if not project_root.exists():
        print(f"Project root does not exist: {project_root}")
        return 3

    pkg, err = _load_package_json(project_root)
    if err:
        print(err)
        return 3

    deps = _deps(pkg)
    uses_expo_router = "expo-router" in deps

    results: List[CheckResult] = []

    # Dependency checks
    results.append(
        CheckResult(
            name="Dependency: @clerk/clerk-expo",
            ok="@clerk/clerk-expo" in deps,
            details=deps.get("@clerk/clerk-expo", "missing"),
            required=True,
        )
    )
    results.append(
        CheckResult(
            name="Dependency: expo-secure-store",
            ok="expo-secure-store" in deps,
            details=deps.get("expo-secure-store", "missing"),
            required=True,
        )
    )

    # .env
    has_env_key, env_details = _env_has_publishable_key(project_root)
    results.append(
        CheckResult(
            name="Env: EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY",
            ok=has_env_key,
            details=env_details,
            required=True,
        )
    )

    # File layout hints (warning only)
    if uses_expo_router:
        layout_path = project_root / "app" / "_layout.tsx"
        results.append(
            CheckResult(
                name="Expo Router: app/_layout.tsx exists",
                ok=layout_path.exists(),
                details=str(layout_path) if layout_path.exists() else f"missing {layout_path}",
                required=False,
            )
        )
    else:
        app_tsx = project_root / "App.tsx"
        results.append(
            CheckResult(
                name="React Navigation: App.tsx exists",
                ok=app_tsx.exists(),
                details=str(app_tsx) if app_tsx.exists() else f"missing {app_tsx}",
                required=False,
            )
        )

    # Search for ClerkProvider usage (required)
    clerk_provider_hits = _find_in_files(project_root, re.compile(r"\bClerkProvider\b"))
    has_clerk_provider = len(clerk_provider_hits) > 0
    results.append(
        CheckResult(
            name="Code: ClerkProvider referenced",
            ok=has_clerk_provider,
            details=f"{len(clerk_provider_hits)} hits" if has_clerk_provider else "not found in .ts/.tsx/.js/.jsx",
            required=True,
        )
    )

    # Search for tokenCache usage (required for recommended native persistence)
    token_cache_hits = _find_in_files(project_root, re.compile(r"@clerk/clerk-expo/token-cache|\btokenCache\b"))
    has_token_cache = any("@clerk/clerk-expo/token-cache" in h[2] or "tokenCache" in h[2] for h in token_cache_hits)
    results.append(
        CheckResult(
            name="Code: tokenCache referenced",
            ok=has_token_cache,
            details=f"{len(token_cache_hits)} hits" if has_token_cache else "not found",
            required=True,
        )
    )

    # Print summary
    print(f"Project: {project_root}")
    print(f"Detected router: {'expo-router' if uses_expo_router else 'react-navigation / unknown'}")
    print()

    failed_required = False
    for r in results:
        status = "✓" if r.ok else ("✗" if r.required else "⚠")
        req = "required" if r.required else "optional"
        print(f"{status} {r.name} ({req}) — {r.details}")
        if r.required and not r.ok:
            failed_required = True

    # Helpful context for debugging
    if clerk_provider_hits:
        print("\nClerkProvider hits (first few):")
        for p, line_no, line in clerk_provider_hits[:5]:
            rel = p.relative_to(project_root)
            print(f"  - {rel}:{line_no}: {line}")

    if token_cache_hits:
        print("\nToken cache hits (first few):")
        for p, line_no, line in token_cache_hits[:5]:
            rel = p.relative_to(project_root)
            print(f"  - {rel}:{line_no}: {line}")

    if failed_required:
        print(
            """\nOne or more REQUIRED checks failed.

Common fixes:
- Install missing deps:
    npm i @clerk/clerk-expo expo-secure-store
- Add EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY to .env
- Wrap your root in <ClerkProvider tokenCache={tokenCache}> (Expo Router: app/_layout.tsx)
"""
        )
        return 1

    print("\nAll required checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
