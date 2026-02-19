#!/usr/bin/env python3
"""Scaffold the canonical Convex 'tasks' example for an Expo project.

By default this is a DRY RUN and prints what it would create.
Use --write to actually write files.

Usage:
  python scripts/scaffold_tasks_example.py            # dry-run
  python scripts/scaffold_tasks_example.py --write    # write files

This script will create/overwrite ONLY if you pass --overwrite.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SAMPLE_DATA = """{"text": "Buy groceries", "isCompleted": true}
{"text": "Go for a swim", "isCompleted": true}
{"text": "Integrate Convex", "isCompleted": false}
"""

TASKS_TS = """import { query, mutation } from "./_generated/server";
import { v } from "convex/values";

export const get = query({
  args: {},
  handler: async (ctx) => {
    return await ctx.db.query("tasks").collect();
  },
});

export const add = mutation({
  args: { text: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", { text: args.text, isCompleted: false });
  },
});
"""

SCHEMA_TS = """import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  }),
});
"""

def find_root(start: Path) -> Path:
    cur = start.resolve()
    for _ in range(10):
        if (cur / "package.json").exists():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    raise SystemExit("Could not find package.json - run from inside your Expo project")

def would_write(path: Path, overwrite: bool) -> bool:
    return overwrite or not path.exists()

def plan(root: Path, overwrite: bool) -> list[tuple[Path, str]]:
    files: list[tuple[Path, str]] = []
    files.append((root / "sampleData.jsonl", SAMPLE_DATA))
    files.append((root / "convex" / "tasks.ts", TASKS_TS))
    files.append((root / "convex" / "schema.ts", SCHEMA_TS))
    # Filter out files we would not overwrite (unless overwrite=True)
    out: list[tuple[Path, str]] = []
    for p, content in files:
        if would_write(p, overwrite):
            out.append((p, content))
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true", help="Actually write the files.")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite existing files.")
    args = ap.parse_args()

    root = find_root(Path.cwd())
    (root / "convex").mkdir(exist_ok=True)

    planned = plan(root, args.overwrite)

    if not planned:
        print("Nothing to do (files already exist). Use --overwrite to force regeneration.")
        return 0

    print("Planned files:")
    for p, _ in planned:
        rel = p.relative_to(root)
        exists = "(will overwrite)" if p.exists() else "(new)"
        print(f"  - {rel} {exists}")

    if not args.write:
        print("\nDry-run only. Re-run with --write to create the files.")
        print("\nNext steps after writing:")
        print("  1) Run: npx convex dev")
        print("  2) Run: npx convex import --table tasks sampleData.jsonl")
        print("  3) In your Expo UI, call: useQuery(api.tasks.get)")
        return 0

    for p, content in planned:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
    print("\n✓ Wrote files.")
    print("\nNext steps:")
    print("  1) Run: npx convex dev")
    print("  2) Run: npx convex import --table tasks sampleData.jsonl")
    print("  3) Wire up ConvexProvider + ConvexReactClient in your entry file")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
