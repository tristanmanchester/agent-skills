# Components, migrations, and reuse

## When a component is worth it
Use a Convex component when a feature:
- owns a coherent subsystem with its own tables and functions
- should be reusable across multiple apps
- benefits from an API boundary around its internal state
- would otherwise clutter the root app with tightly-coupled code

If the feature is small and app-specific, keep it in the main app first.

## Component basics
A component lives in its own folder with a `convex.config.ts`, schema, functions, and generated code. A common local layout is:

```text
convex/
  convex.config.ts
  components/
    onboarding/
      convex.config.ts
      schema.ts
      lib/
      _generated/
```

## Root app wiring
```ts
// convex/convex.config.ts
import { defineApp } from "convex/server";
import onboarding from "./components/onboarding/convex.config.js";

const app = defineApp();
app.use(onboarding);

export default app;
```

## Component definition
```ts
// convex/components/onboarding/convex.config.ts
import { defineComponent } from "convex/server";

export default defineComponent("onboarding_flow");
```

## Important caveat
Components are still a beta/unstable part of Convex. Use them deliberately and avoid forcing a component boundary onto a simple one-off feature.

## Migration guidance
When improving an existing repo:
- keep public API paths stable if the frontend already depends on them
- add indexes before moving heavy reads onto them
- prefer additive schema changes first
- use thin adapter functions when moving code to new files or components
- remove deprecated paths only after callers have switched

## Reuse rule of thumb
Start simple in the app.
Extract to a component when reuse or isolation becomes real, not speculative.
