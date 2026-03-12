\
#!/usr/bin/env python3
"""Scaffold a small Expo + Convex tasks example.

Default mode is dry-run. Use --write to create files.

Examples:
  python scripts/scaffold_tasks_example.py
  python scripts/scaffold_tasks_example.py --write
  python scripts/scaffold_tasks_example.py --write --ui-file app/index.tsx
  python scripts/scaffold_tasks_example.py --json

Exit codes:
  0 = success
  2 = project root not found
  3 = internal error
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from textwrap import dedent


SAMPLE_DATA = dedent("""\
{"text": "Buy groceries", "isCompleted": true}
{"text": "Go for a swim", "isCompleted": true}
{"text": "Integrate Convex", "isCompleted": false}
""")

SCHEMA_TS = dedent("""\
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  }),
});
""")

TASKS_TS = dedent("""\
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

const taskDoc = v.object({
  _id: v.id("tasks"),
  _creationTime: v.number(),
  text: v.string(),
  isCompleted: v.boolean(),
});

export const list = query({
  args: {},
  returns: v.array(taskDoc),
  handler: async (ctx) => {
    return await ctx.db.query("tasks").order("desc").take(50);
  },
});

export const add = mutation({
  args: { text: v.string() },
  returns: v.id("tasks"),
  handler: async (ctx, args) => {
    const text = args.text.trim();
    if (!text) {
      throw new Error("Task text cannot be empty");
    }

    return await ctx.db.insert("tasks", {
      text,
      isCompleted: false,
    });
  },
});

export const toggle = mutation({
  args: {
    taskId: v.id("tasks"),
    isCompleted: v.boolean(),
  },
  returns: v.null(),
  handler: async (ctx, args) => {
    await ctx.db.patch(args.taskId, {
      isCompleted: args.isCompleted,
    });
    return null;
  },
});
""")


@dataclass
class PlannedFile:
    path: str
    action: str  # create | overwrite | skip
    reason: str | None = None


def find_project_root(start: Path) -> Path | None:
    current = start.resolve()
    for _ in range(12):
        if (current / "package.json").exists():
            return current
        if current.parent == current:
            return None
        current = current.parent
    return None


def ensure_relative_import(from_file: Path, target_without_ext: Path) -> str:
    rel = os.path.relpath(target_without_ext, start=from_file.parent)
    rel = rel.replace(os.sep, "/")
    if not rel.startswith("."):
        rel = f"./{rel}"
    return rel


def build_ui_tsx(ui_file: Path, root: Path) -> str:
    api_target = root / "convex" / "_generated" / "api"
    api_import = ensure_relative_import(ui_file, api_target)
    return dedent(f"""\
import {{ api }} from "{api_import}";
import {{ useMutation, useQuery }} from "convex/react";
import {{ useState }} from "react";
import {{
  ActivityIndicator,
  FlatList,
  Pressable,
  Text,
  TextInput,
  View,
}} from "react-native";

export default function TasksScreen() {{
  const tasks = useQuery(api.tasks.list);
  const addTask = useMutation(api.tasks.add);
  const toggleTask = useMutation(api.tasks.toggle);
  const [text, setText] = useState("");

  if (tasks === undefined) {{
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }}

  return (
    <View style={{ flex: 1, padding: 24, gap: 16 }}>
      <View style={{ gap: 8 }}>
        <Text style={{ fontSize: 28, fontWeight: "700" }}>Tasks</Text>
        <Text style={{ color: "#666" }}>
          If this renders, the Expo and Convex wiring is working.
        </Text>
      </View>

      <View style={{ flexDirection: "row", gap: 8 }}>
        <TextInput
          value={{text}}
          onChangeText={{setText}}
          placeholder="Add a task"
          style={{
            flex: 1,
            borderWidth: 1,
            borderColor: "#ddd",
            borderRadius: 10,
            paddingHorizontal: 12,
            paddingVertical: 10,
          }}
        />
        <Pressable
          onPress={{async () => {{
            const trimmed = text.trim();
            if (!trimmed) return;
            await addTask({{ text: trimmed }});
            setText("");
          }}}}
          style={{
            justifyContent: "center",
            borderRadius: 10,
            paddingHorizontal: 14,
            paddingVertical: 10,
            backgroundColor: "#111",
          }}
        >
          <Text style={{ color: "white", fontWeight: "600" }}>Add</Text>
        </Pressable>
      </View>

      <FlatList
        data={{tasks}}
        keyExtractor={{(task) => task._id}}
        renderItem={{({{ item }}) => (
          <Pressable
            onPress={{() =>
              toggleTask({{
                taskId: item._id,
                isCompleted: !item.isCompleted,
              }})
            }}
            style={{
              borderWidth: 1,
              borderColor: "#eee",
              borderRadius: 12,
              padding: 14,
              marginBottom: 10,
            }}
          >
            <Text
              style={{
                fontSize: 16,
                textDecorationLine: item.isCompleted ? "line-through" : "none",
              }}
            >
              {{item.text}}
            </Text>
          </Pressable>
        )}}
      />
    </View>
  );
}}
""")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a minimal Expo + Convex tasks example. Dry-run by default."
    )
    parser.add_argument(
        "--root",
        type=Path,
        help="Project root. Defaults to the nearest parent containing package.json.",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="Actually write files instead of printing the plan.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing files. Without this flag, existing files are left untouched.",
    )
    parser.add_argument(
        "--ui-file",
        type=Path,
        help="Optional screen file to scaffold, e.g. app/index.tsx or src/app/index.tsx.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON plan/result instead of human-readable text.",
    )
    return parser.parse_args(argv)


def decide_action(path: Path, overwrite: bool) -> str:
    if not path.exists():
        return "create"
    if overwrite:
        return "overwrite"
    return "skip"


def plan_files(root: Path, overwrite: bool, ui_file: Path | None) -> tuple[list[PlannedFile], dict[Path, str]]:
    file_map: dict[Path, str] = {
        root / "sampleData.jsonl": SAMPLE_DATA,
        root / "convex" / "schema.ts": SCHEMA_TS,
        root / "convex" / "tasks.ts": TASKS_TS,
    }
    if ui_file is not None:
        file_map[ui_file] = build_ui_tsx(ui_file, root)

    plan: list[PlannedFile] = []
    for path in sorted(file_map.keys()):
        action = decide_action(path, overwrite)
        reason = None
        if action == "skip":
            reason = "File already exists; rerun with --overwrite to replace it."
        plan.append(PlannedFile(path=str(path), action=action, reason=reason))
    return plan, file_map


def write_files(plan: list[PlannedFile], file_map: dict[Path, str]) -> list[str]:
    written: list[str] = []
    for item in plan:
        path = Path(item.path)
        if item.action == "skip":
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(file_map[path], encoding="utf-8")
        written.append(str(path))
    return written


def render_human(root: Path, plan: list[PlannedFile], write: bool) -> str:
    lines: list[str] = []
    lines.append(f"Project root: {root}")
    lines.append("")
    lines.append("Plan:")
    for item in plan:
        rel = Path(item.path).relative_to(root)
        label = item.action.upper()
        lines.append(f"- [{label}] {rel}")
        if item.reason:
            lines.append(f"    {item.reason}")

    lines.append("")
    if write:
        wrote_any = any(item.action in {"create", "overwrite"} for item in plan)
        if wrote_any:
            lines.append("Files were written.")
        else:
            lines.append("Nothing was written because every target file already exists.")
    else:
        lines.append("Dry-run only. Re-run with --write to create files.")

    lines.append("")
    lines.append("Next steps:")
    lines.append("1. Run `npx convex dev` if it is not already running.")
    lines.append("2. Run `npx convex import --table tasks sampleData.jsonl`.")
    lines.append("3. Make sure your root provider is mounted with `ConvexProvider` and `ConvexReactClient`.")
    lines.append("4. Run `python scripts/validate_project.py`.")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        if args.root:
            root = args.root.resolve()
            if not (root / "package.json").exists():
                if args.json:
                    print(json.dumps({
                        "ok": False,
                        "fatal": "Provided --root does not contain package.json.",
                        "root": str(root),
                    }, indent=2))
                else:
                    print("Provided --root does not contain package.json.", file=sys.stderr)
                return 2
        else:
            found = find_project_root(Path.cwd())
            if found is None:
                if args.json:
                    print(json.dumps({
                        "ok": False,
                        "fatal": "Could not find package.json by walking up from the current directory.",
                        "cwd": str(Path.cwd()),
                    }, indent=2))
                else:
                    print("Could not find package.json by walking up from the current directory.", file=sys.stderr)
                return 2
            root = found

        ui_file = None
        if args.ui_file is not None:
            ui_file = args.ui_file if args.ui_file.is_absolute() else (root / args.ui_file)
            ui_file = ui_file.resolve()

        plan, file_map = plan_files(root, args.overwrite, ui_file)

        written: list[str] = []
        if args.write:
            written = write_files(plan, file_map)

        payload = {
            "ok": True,
            "root": str(root),
            "write": args.write,
            "overwrite": args.overwrite,
            "planned_files": [asdict(item) for item in plan],
            "written_files": written,
            "next_steps": [
                "Run `npx convex dev` if it is not already running.",
                "Run `npx convex import --table tasks sampleData.jsonl`.",
                "Ensure the root provider uses ConvexProvider + ConvexReactClient.",
                "Run `python scripts/validate_project.py`.",
            ],
        }

        if args.json:
            print(json.dumps(payload, indent=2))
        else:
            print(render_human(root, plan, args.write), end="")
        return 0
    except KeyboardInterrupt:
        if args.json:
            print(json.dumps({"ok": False, "fatal": "Interrupted."}, indent=2))
        else:
            print("Interrupted.", file=sys.stderr)
        return 3
    except Exception as exc:
        if args.json:
            print(json.dumps({"ok": False, "fatal": f"Internal scaffold error: {exc}"}, indent=2))
        else:
            print(f"Internal scaffold error: {exc}", file=sys.stderr)
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
