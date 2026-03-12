# File uploads from Expo to Convex storage

Expo gives you local `file://` URIs from packages such as:

- `expo-image-picker`
- `expo-document-picker`
- `expo-av`
- custom camera or recorder flows

The most reliable Convex pattern is:

1. request an upload URL from a mutation,
2. load the local URI with `fetch(uri)`,
3. convert it to a `Blob`,
4. `POST` the blob to the upload URL,
5. store the returned `storageId` plus your own metadata in a second mutation.

## Why use upload URLs?

Benefits:

- avoids squeezing file bytes through normal function arguments,
- works well for mobile file sources,
- separates transport from your domain metadata,
- and lets you attach later processing steps cleanly.

## Schema example

```ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  files: defineTable({
    ownerId: v.id("users"),
    storageId: v.id("_storage"),
    originalName: v.string(),
    mimeType: v.string(),
    sizeBytes: v.optional(v.number()),
    kind: v.union(
      v.literal("image"),
      v.literal("document"),
      v.literal("audio"),
      v.literal("other"),
    ),
    createdAt: v.number(),
  })
    .index("by_owner", ["ownerId"])
    .index("by_storage", ["storageId"]),
});
```

## Backend functions

`convex/files.ts`

```ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  args: {},
  returns: v.string(),
  handler: async (ctx) => {
    // Add auth checks here if uploads are protected.
    return await ctx.storage.generateUploadUrl();
  },
});

export const saveUploadedFile = mutation({
  args: {
    ownerId: v.id("users"),
    storageId: v.id("_storage"),
    originalName: v.string(),
    mimeType: v.string(),
    sizeBytes: v.optional(v.number()),
    kind: v.union(
      v.literal("image"),
      v.literal("document"),
      v.literal("audio"),
      v.literal("other"),
    ),
  },
  returns: v.id("files"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("files", {
      ownerId: args.ownerId,
      storageId: args.storageId,
      originalName: args.originalName,
      mimeType: args.mimeType,
      sizeBytes: args.sizeBytes,
      kind: args.kind,
      createdAt: Date.now(),
    });
  },
});

export const getFileMetadata = query({
  args: {
    fileId: v.id("files"),
  },
  returns: v.union(
    v.object({
      _id: v.id("files"),
      _creationTime: v.number(),
      ownerId: v.id("users"),
      storageId: v.id("_storage"),
      originalName: v.string(),
      mimeType: v.string(),
      sizeBytes: v.optional(v.number()),
      kind: v.union(
        v.literal("image"),
        v.literal("document"),
        v.literal("audio"),
        v.literal("other"),
      ),
      createdAt: v.number(),
    }),
    v.null(),
  ),
  handler: async (ctx, args) => {
    return await ctx.db.get(args.fileId);
  },
});
```

### If uploads are protected

Do not accept `ownerId` blindly from the client in a real app. Resolve the current user from auth and write that verified owner ID instead.

## Expo client example

```tsx
import { api } from "../convex/_generated/api";
import { useMutation } from "convex/react";

const generateUploadUrl = useMutation(api.files.generateUploadUrl);
const saveUploadedFile = useMutation(api.files.saveUploadedFile);

export async function uploadFromUri(params: {
  uri: string;
  ownerId: string;
  originalName: string;
  mimeType: string;
  sizeBytes?: number;
  kind: "image" | "document" | "audio" | "other";
}) {
  const postUrl = await generateUploadUrl();

  const fileResponse = await fetch(params.uri);
  if (!fileResponse.ok) {
    throw new Error("Failed to read the local file URI");
  }

  const blob = await fileResponse.blob();

  const uploadResponse = await fetch(postUrl, {
    method: "POST",
    headers: {
      "Content-Type": params.mimeType,
    },
    body: blob,
  });

  if (!uploadResponse.ok) {
    throw new Error("Failed to upload file bytes to Convex");
  }

  const { storageId } = await uploadResponse.json();

  return await saveUploadedFile({
    ownerId: params.ownerId,
    storageId,
    originalName: params.originalName,
    mimeType: params.mimeType,
    sizeBytes: params.sizeBytes,
    kind: params.kind,
  });
}
```

## Optional post-processing

Common follow-up jobs:

- image resizing,
- audio transcription,
- virus scanning,
- metadata extraction,
- PDF text extraction,
- thumbnail creation.

Good pattern:

1. the metadata mutation inserts the file record,
2. it schedules or triggers an internal action,
3. the action calls the external service or heavy processor,
4. an internal mutation stores the result.

## Serving files back to the app

Typical options:

- store the `storageId` and request a serving URL when needed,
- or return URLs from a query alongside your domain metadata.

Keep privacy in mind. If the file is protected, do not hand out URLs in a query that lacks authorization checks.

## Gotchas

### Wrong MIME type

Mobile uploads often fail quietly or behave strangely when the `Content-Type` header is missing or incorrect.

### Upload succeeds but metadata is missing

This usually means the second mutation failed or was never awaited.

### Metadata saved but post-processing never ran

Check:

- scheduler calls are awaited,
- the scheduled function is internal and callable,
- and the action file is in the correct runtime if it uses Node-only packages.

### Huge feeds of uploaded assets

Do not `.collect()` every file document. Paginate user libraries and media lists.

## Review checklist

- [ ] Upload URL comes from a mutation.
- [ ] Local URI is converted to a `Blob` before upload.
- [ ] The upload `fetch` call sets the correct `Content-Type`.
- [ ] The returned `storageId` is persisted with domain metadata.
- [ ] Protected uploads derive ownership from auth on the backend.
- [ ] Follow-up processing happens in actions or internal functions.
- [ ] Large media libraries use pagination.
