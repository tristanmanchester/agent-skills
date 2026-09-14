# Setup and compatibility

Read the app's lockfile, Expo SDK, React Native version, architecture, and native
build configuration first. Resolve exact Reanimated/Worklets compatibility from
upstream tables and the installed package's compatibility.json: minor-version
tables assume the latest patch, which can differ from the app's actual patch.

For an authorised current Expo installation:

```bash
npx expo install react-native-reanimated react-native-worklets react-native-gesture-handler
```

This chooses packages for that SDK, not necessarily the newest versions. Verify
that Gesture Handler resolves to the API generation used in the implementation.
Do not copy RNGH 3 hooks into a v2 binary or force a mismatched dependency just to
make imports resolve. A supported stack upgrade includes the native build.

Current Expo's babel-preset-expo configures the worklets integration; inspect
existing configuration before adding another plugin. Bare Reanimated 4 uses
react-native-worklets/plugin, ordered as upstream requires. Do not call redundant
or mixed plugins harmless. Rebuild the development client/native app after native
package changes; clearing Metro cache cannot repair a binary/JS version mismatch.

Reanimated 4 requires New Architecture. Reanimated 3 is not actively maintained
and cannot simply be combined with react-native-worklets. This skill does not ship
a legacy path; select an explicit compatible project strategy.

Inspect GestureHandlerRootView around the real native root, including Android
modal roots as required. Keep flex/layout sizing correct. Relations must share the
appropriate gesture root. Do not add redundant roots mechanically or confuse a
root view with the v3 hook/builder interoperability boundary.

Use Hermes-compatible inspector tooling. A package-tree read, TypeScript build,
Jest mock, and a successful native interaction are distinct checks.

Reviewed 2026-09-13:
- https://docs.swmansion.com/react-native-reanimated/docs/guides/compatibility/
- https://docs.expo.dev/versions/latest/sdk/reanimated/
- https://docs.swmansion.com/react-native-gesture-handler/docs/guides/upgrading-to-3/
