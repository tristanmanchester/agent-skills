# File uploads from Expo / React Native to Convex

## Recommended approach: upload URLs (works for large files)
Convex File Storage supports a 3-step upload flow:
1. mutation calls `ctx.storage.generateUploadUrl()` and returns a short-lived URL
2. client uploads bytes to that URL with `fetch(...)`
3. client calls another mutation to store the returned `storageId` in a table

## Backend: generate upload URL + save metadata

`convex/files.ts`:

```ts
import { mutation, query } from "./_generated/server";
import { v } from "convex/values";

export const generateUploadUrl = mutation({
  args: {},
  handler: async (ctx) => {
    // Add auth checks here if needed:
    // if (!ctx.auth.getUserIdentity()) throw new Error("Not authenticated");
    return await ctx.storage.generateUploadUrl();
  },
});

export const saveFile = mutation({
  args: {
    storageId: v.id("_storage"),
    mimeType: v.string(),
    originalName: v.string(),
  },
  handler: async (ctx, args) => {
    return await ctx.db.insert("files", {
      storageId: args.storageId,
      mimeType: args.mimeType,
      originalName: args.originalName,
    });
  },
});
```

## Client (Expo): upload from a file URI
In Expo you often have a `uri` from `expo-image-picker`, `expo-document-picker`, etc.

```ts
import { api } from "@/convex/_generated/api";
import { useMutation } from "convex/react";

const generateUploadUrl = useMutation(api.files.generateUploadUrl);
const saveFile = useMutation(api.files.saveFile);

async function uploadFromUri(uri: string, mimeType: string, originalName: string) {
  // 1) Get upload URL
  const postUrl = await generateUploadUrl();

  // 2) Turn local file into a Blob (fetch works with file:// URIs in Expo)
  const fileResponse = await fetch(uri);
  if (!fileResponse.ok) throw new Error("Failed to read file from URI");
  const blob = await fileResponse.blob();

  // 3) POST bytes to Convex
  const uploadResponse = await fetch(postUrl, {
    method: "POST",
    headers: { "Content-Type": mimeType },
    body: blob,
  });
  if (!uploadResponse.ok) throw new Error("Upload failed");
  const { storageId } = await uploadResponse.json();

  // 4) Store metadata in your table
  await saveFile({ storageId, mimeType, originalName });
}
```

## Serving the file back to the app
- store `storageId` on a document
- generate a URL (see Convex File Storage docs) and render it in the client

## Gotchas
- Prefer upload URLs for files > 20MB (HTTP actions have request size limits).
- Make sure you set `Content-Type` properly during upload.
- If uploads work on device but fail on web, confirm CORS and URI handling.

