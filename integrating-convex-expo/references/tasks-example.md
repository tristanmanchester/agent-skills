# Tasks example for Expo + Convex

Use this as the smallest end-to-end proof that the stack is wired correctly.

## What this proves

A successful run confirms all of the following:

- `npx convex dev` is running,
- `convex/_generated/` exists,
- the Expo app can reach the deployment URL,
- the root provider is mounted correctly,
- and frontend imports are pointing at generated API references.

## 1. Seed data

Create `sampleData.jsonl` in the project root:

```jsonl
{"text": "Buy groceries", "isCompleted": true}
{"text": "Go for a swim", "isCompleted": true}
{"text": "Integrate Convex", "isCompleted": false}
```

Import it:

```bash
npx convex import --table tasks sampleData.jsonl
```

## 2. Add a schema

`convex/schema.ts`

```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  tasks: defineTable({
    text: v.string(),
    isCompleted: v.boolean(),
  }),
});
```

This table is small enough for a starter example. Add indexes later if you query by owner, status, or team.

## 3. Add functions

`convex/tasks.ts`

```ts
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
```

### Why `take(50)` instead of `.collect()`?

For a starter example, `take(50)` keeps the query bounded. If the list can grow without limit, switch to a paginated query and `usePaginatedQuery`.

## 4. Add a screen

Use a relative import that matches the screen location.

### If the screen file is `app/index.tsx`

```tsx
import { api } from "../convex/_generated/api";
import { useMutation, useQuery } from "convex/react";
import { useState } from "react";
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  Text,
  TextInput,
  View,
} from "react-native";

export default function IndexScreen() {
  const tasks = useQuery(api.tasks.list);
  const addTask = useMutation(api.tasks.add);
  const toggleTask = useMutation(api.tasks.toggle);
  const [text, setText] = useState("");

  if (tasks === undefined) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator />
      </View>
    );
  }

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
          value={text}
          onChangeText={setText}
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
          onPress={async () => {
            const trimmed = text.trim();
            if (!trimmed) return;
            await addTask({ text: trimmed });
            setText("");
          }}
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
        data={tasks}
        keyExtractor={(task) => task._id}
        renderItem={({ item }) => (
          <Pressable
            onPress={() =>
              toggleTask({
                taskId: item._id,
                isCompleted: !item.isCompleted,
              })
            }
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
              {item.text}
            </Text>
          </Pressable>
        )}
      />
    </View>
  );
}
```

If the screen lives under `src/app`, change the generated API import accordingly.

## 5. Expected behaviour

- `tasks` is `undefined` on the first render.
- It then resolves to an array.
- Pressing **Add** creates a task and the list updates reactively.
- Pressing a task toggles completion and the UI updates without manual refetching.

## 6. Quick debug checklist

If it fails:

1. confirm `npx convex dev` is running,
2. confirm `convex/_generated/api` exists,
3. confirm the provider is mounted at the app root,
4. confirm the screen imports from the generated API,
5. confirm the client sees `EXPO_PUBLIC_CONVEX_URL`,
6. run `python scripts/validate_project.py --root <project-root>`.

## Optional helper script

You can scaffold the files above with:

```bash
python scripts/scaffold_tasks_example.py --root <project-root>
python scripts/scaffold_tasks_example.py --root <project-root> --write
```

Add `--ui-file app/index.tsx` or another target path if you also want a screen scaffolded.
