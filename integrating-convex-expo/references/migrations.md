# Migration patterns for Convex in Expo apps

Use this reference when changing schemas or gradually moving from another backend without breaking live clients.

## Migration priorities

1. keep the app working during the transition,
2. make each migration step restart-safe,
3. avoid one-shot breaking changes unless the app is still throwaway,
4. reduce public blast radius by using internal functions for migration logic.

## Preferred migration strategy: additive first

### Safe changes

These are usually straightforward:

- add a new optional field,
- add a new table,
- add a new index,
- add a new internal function,
- add a new public read path while old ones still work.

### Risky changes

These usually need a staged rollout:

- making an optional field required,
- changing field types,
- renaming a field,
- splitting one table into multiple related tables,
- merging multiple shapes into one,
- removing fields that old clients still read.

## Pattern 1: optional field -> backfill -> required field

### Step 1

Add the field as optional.

```ts
users: defineTable({
  name: v.string(),
  bio: v.optional(v.string()),
})
```

### Step 2

Backfill missing rows with an internal mutation or internal action.

```ts
import { internalMutation } from "./_generated/server";
import { v } from "convex/values";

export const backfillUserBio = internalMutation({
  args: {
    batchSize: v.optional(v.number()),
  },
  returns: v.object({
    processed: v.number(),
  }),
  handler: async (ctx, args) => {
    const batchSize = args.batchSize ?? 100;
    const users = await ctx.db.query("users").take(batchSize);

    let processed = 0;

    for (const user of users) {
      if (user.bio !== undefined) continue;
      await ctx.db.patch(user._id, { bio: "" });
      processed += 1;
    }

    return { processed };
  },
});
```

### Step 3

Run the backfill repeatedly until no rows remain.

### Step 4

Make the field required only after all data is compliant and old clients are updated.

## Pattern 2: rename a field

Suppose `name` becomes `displayName`.

### Safer rollout

1. add `displayName` as optional,
2. backfill from `name`,
3. update readers to prefer `displayName ?? name`,
4. update writers to write both fields for a period,
5. remove reads of `name`,
6. finally remove `name` from the schema.

This dual-read and dual-write period is what keeps mobile clients from breaking during staggered releases.

## Pattern 3: split nested or overloaded data into proper tables

Example:

- old `posts.tags: string[]`
- new `tags` table plus `postTags` join table

### Safer rollout

1. add the new tables and indexes,
2. keep the old field temporarily,
3. backfill relationships in batches,
4. update readers to use the new tables,
5. update writers to populate only the new shape,
6. remove the old field once all readers are migrated.

## Pattern 4: move from another backend to Convex gradually

Good strategy:

1. keep the old system for legacy features,
2. add new features in Convex first,
3. migrate one domain at a time,
4. dual-read where needed,
5. cut traffic over feature by feature.

This works well when moving from Firebase, Supabase, a REST backend, or a custom database.

## Batch processing guidance

For large tables:

- process in batches,
- make the batch idempotent,
- log enough state to know what has already been migrated,
- avoid reading the entire table into memory,
- and prefer resumable jobs over one huge mutation.

## Scheduled migration pattern

When a migration is expensive, schedule or repeatedly invoke a small internal unit of work instead of trying to finish everything in one request.

Good for:

- media metadata backfills,
- adding derived state fields,
- rebuilding search or denormalised views,
- moving historical records.

## Validation rules during migrations

While migrating:

- keep validators accurate for each active shape,
- do not expose a public function that accepts both legacy and new shapes unless you truly need it,
- and make deprecation windows deliberate rather than accidental.

## Mobile-client-specific note

Expo clients can lag behind the backend because users do not update instantly.

That means:

- avoid removing fields immediately after changing the app,
- keep old read paths alive long enough,
- and assume some users will run an older build against the new backend for a while.

## Review checklist

- [ ] The change has been decomposed into additive steps.
- [ ] Backfills are idempotent and can be resumed.
- [ ] Public clients are not forced onto a breaking schema in one step.
- [ ] Mobile release lag has been accounted for.
- [ ] Old reads and writes are removed only after the rollout is complete.
- [ ] Internal functions are used for migration mechanics where appropriate.
