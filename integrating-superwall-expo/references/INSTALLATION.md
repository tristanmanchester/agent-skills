# Installation and prerequisites (Expo SDK)

## Checklist
- Expo SDK **53+** is required.
- Expo Go is **not supported** (native modules). Use a **Development Build**.
- Target platform minimums:
  - iOS deployment target **15.1+**
  - Android minSdkVersion **21+**

## Install packages
Use Expo’s installer so versions match your SDK:

```bash
npx expo install expo-superwall
```

If you’re not already using it, install the build-properties config plugin:

```bash
npx expo install expo-build-properties
```

## Set minimum platform targets (recommended)
Add `expo-build-properties` to `app.json` / `app.config.js` and set the required targets:

```jsonc
{
  "expo": {
    "plugins": [
      [
        "expo-build-properties",
        {
          "android": { "minSdkVersion": 21 },
          "ios": { "deploymentTarget": "15.1" }
        }
      ]
    ]
  }
}
```

## Build and run (Development Build)
Superwall requires native code, so you must run via a dev client:

```bash
npx expo run:ios
# or
npx expo run:android
```

If you use EAS Build, create a new development build after adding `expo-superwall`.

## Common gotcha: “Cannot find native module 'SuperwallExpo'”
This almost always means one of:
- you ran in Expo Go
- native folders are stale (added the package after prebuild)
- you haven’t rebuilt the dev client since adding the native module

Follow `references/TROUBLESHOOTING.md`.

## Sources
- https://superwall.com/docs/expo/quickstart/install
- https://superwall.com/docs/expo/guides/debugging
