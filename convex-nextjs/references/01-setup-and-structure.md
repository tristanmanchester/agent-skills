# Setup & project structure (Next.js + Convex)

## What `npx convex dev` does
- Prompts login / project selection
- Creates `convex/` (backend functions live here)
- Generates `convex/_generated/*` (typed API + server helpers)
- Writes `NEXT_PUBLIC_CONVEX_URL` for the frontend in `.env.local` (typical dev flow)

## Recommended file layout (App Router)
```
app/
  layout.tsx
  ConvexClientProvider.tsx
  (routes)...
convex/
  schema.ts
  tasks.ts
  auth.ts (optional)
  _generated/
    api.ts
    server.ts
```

## Pages Router notes
- Provider typically lives under `pages/_app.tsx`
- Same Convex client setup; hooks still require React components.
- See the official Pages Router quickstart if needed:
  https://docs.convex.dev/client/nextjs/pages-router/quickstart

## Common setup pitfalls
- `useQuery` in a Server Component: add `"use client"` at the top.
- `NEXT_PUBLIC_CONVEX_URL` missing: re-run `npx convex dev` or set it explicitly.
- `convex/_generated` missing or stale: keep `npx convex dev` running or run `npx convex codegen`.
