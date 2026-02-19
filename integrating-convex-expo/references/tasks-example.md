# Tasks example (seed → query → UI)

This mirrors the official Expo + Convex guide and the Convex React Native quickstart.

## 1) Seed data
Create `sampleData.jsonl` in the project root:

```jsonl
{"text": "Buy groceries", "isCompleted": true}
{"text": "Go for a swim", "isCompleted": true}
{"text": "Integrate Convex", "isCompleted": false}
```

Import it (creates the `tasks` table if it doesn’t exist yet):

```bash
npx convex import --table tasks sampleData.jsonl
```

## 2) Backend query: `convex/tasks.ts`

```ts
import { query, mutation } from "./_generated/server";
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
```

## 3) (Recommended) Add a schema: `convex/schema.ts`

Convex works without a schema, but schemas provide types and safer migrations:

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

## 4) UI (expo-router): `app/index.tsx` or `src/app/index.tsx`

```tsx
import { api } from "@/convex/_generated/api";
import { useMutation, useQuery } from "convex/react";
import { Button, Text, View } from "react-native";

export default function Index() {
  const tasks = useQuery(api.tasks.get);
  const add = useMutation(api.tasks.add);

  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center", gap: 12 }}>
      {tasks?.map(({ _id, text }) => (
        <Text key={_id}>{text}</Text>
      ))}
      <Button title="Add task" onPress={() => add({ text: "New task" })} />
    </View>
  );
}
```

### Notes
- `tasks` is `undefined` on first render while the query loads. Handle loading states explicitly in real screens.
- The `@/` path alias is common in Expo templates. If your project doesn’t have it, import from a relative path:
  `import { api } from "../convex/_generated/api"` (adjust to your folder layout).

