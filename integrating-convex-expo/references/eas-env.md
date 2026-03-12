# Expo environment handling for Convex

## Core rule

The Expo client should read the Convex deployment URL from:

```ts
process.env.EXPO_PUBLIC_CONVEX_URL
```

Anything else causes avoidable breakage.

## What `npx convex dev` is expected to do

Running:

```bash
npx convex dev
```

should:

- create or connect a Convex project,
- create the `convex/` backend directory if it does not exist,
- keep a sync process running,
- and write the current deployment URL into `.env.local` as `EXPO_PUBLIC_CONVEX_URL=...`.

Treat `.env.local` as the local-development source of truth.

## Recommended deployment URL policy

Use separate Convex deployments for each environment whenever the product has meaningful preview and production stages.

- **development**: the local or shared dev deployment used by `npx convex dev`
- **preview**: a preview deployment used by EAS preview builds
- **production**: the production Convex deployment used by store releases

Do not casually point preview or production builds at a development deployment.

## Local development checklist

1. Run `npx convex dev`.
2. Confirm `.env.local` exists.
3. Confirm it contains:

   ```bash
   EXPO_PUBLIC_CONVEX_URL=https://your-deployment.convex.cloud
   ```

4. Restart Metro if the value was added or changed after the dev server started.
5. If using multiple local `.env*` files, make sure they do not override or shadow the value unintentionally.

## EAS builds

EAS cloud builds do not read your local `.env.local` file. Copy the value into EAS environment variables.

Example:

```bash
eas env:create   --name EXPO_PUBLIC_CONVEX_URL   --value https://YOUR_DEPLOYMENT_URL.convex.cloud   --visibility plaintext   --environment development   --environment preview   --environment production
```

Replace the value with the deployment URL from the correct Convex environment.

## Safer operational pattern

When you create or rotate a deployment URL:

1. update the local `.env.local`,
2. update the EAS environment value for the matching build environments,
3. rebuild any preview or production apps that should pick up the new value,
4. verify the app points to the intended Convex deployment.

## Provider snippet

```tsx
import { ConvexProvider, ConvexReactClient } from "convex/react";
import { Stack } from "expo-router";

const convex = new ConvexReactClient(process.env.EXPO_PUBLIC_CONVEX_URL!, {
  unsavedChangesWarning: false,
});

export default function RootLayout() {
  return (
    <ConvexProvider client={convex}>
      <Stack />
    </ConvexProvider>
  );
}
```

## Common failure modes

### `process.env.EXPO_PUBLIC_CONVEX_URL` is `undefined`

Likely causes:

- `npx convex dev` has never been run in this project.
- `.env.local` was not created where Expo expects it.
- Metro was not restarted after the env file changed.
- The code uses `CONVEX_URL` or another variable name without the `EXPO_PUBLIC_` prefix.

### Local development works but EAS build fails

Likely causes:

- the value exists only in `.env.local`,
- preview or production EAS environments were not updated,
- or the wrong deployment URL was copied into EAS.

### Preview build is hitting production data

Likely causes:

- preview and production share the same `EXPO_PUBLIC_CONVEX_URL`,
- or the build profile uses the wrong EAS environment.

## Validation tips

- Run `python scripts/validate_project.py`.
- Grep the repo for `EXPO_PUBLIC_CONVEX_URL`.
- Keep a short note in the repository or internal docs describing which Convex deployment maps to each build profile.
