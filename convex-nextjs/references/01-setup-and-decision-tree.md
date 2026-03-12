# Setup and decision tree

## Pick the correct entry point
- **New project**: prefer `npm create convex@latest`.
- **Existing Next.js repo**: `npm install convex` then `npx convex dev`.
- **Remote/background agent with no login**: use Agent Mode.
- **Need local-only backend isolation**: use `npx convex dev --local`.

## What `npx convex dev` should give you
- a Convex deployment connection for development
- a functions directory (`convex/` by default, or the path from `convex.json`)
- generated files under `_generated/`
- a frontend URL such as `NEXT_PUBLIC_CONVEX_URL`

## Honour `convex.json` if it exists
Do not assume the functions directory is always `convex/`. Some repos move it to `src/convex/` or another location via:
```json
{
  "functions": "src/convex/"
}
```

## Recommended App Router layout
```text
app/
  layout.tsx
  ConvexClientProvider.tsx
  page.tsx
convex/
  convex.config.ts      # optional, especially for components
  schema.ts
  tasks.ts
  users.ts
  lib/
    auth.ts
  _generated/
    api.ts
    server.ts
```

## Provider baseline
Create a singleton client in a Client Component:

```tsx
"use client";

import { ConvexProvider, ConvexReactClient } from "convex/react";
import type { ReactNode } from "react";

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!);

export function ConvexClientProvider({ children }: { children: ReactNode }) {
  return <ConvexProvider client={convex}>{children}</ConvexProvider>;
}
```

Wrap it near the top of your tree:

```tsx
import { ConvexClientProvider } from "./ConvexClientProvider";

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <ConvexClientProvider>{children}</ConvexClientProvider>
      </body>
    </html>
  );
}
```

## Pages Router note
Use the same client and provider pattern in `pages/_app.tsx`. The React hook rules do not change.

## First smoke test
1. Keep `npx convex dev` running.
2. Create one tiny query.
3. Render it from a Client Component.
4. Confirm the generated `api` import resolves and data appears.

If any of those steps fail, go straight to the troubleshooting reference.
