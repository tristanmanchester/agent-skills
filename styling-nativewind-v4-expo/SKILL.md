---
name: styling-nativewind-v4-expo
description: Set up, repair, and build components with NativeWind v4 and Tailwind CSS v3 in Expo React Native apps. Use for an explicitly v4 project, v4 configuration failures, className interoperability, or v4 theming; not for NativeWind v5 or generic web Tailwind setup.
compatibility: An Expo project using nativewind major 4 and tailwindcss major 3. Native peer versions must match the project's Expo SDK.
metadata:
  version: "2.0.0"
  reviewed: "2026-09-13"
---

# NativeWind v4 in Expo

This is deliberately a **v4** skill. On the review date, the official site labels v5 a prerelease; v5/Tailwind v4 configuration is a separate stack, not a drop-in refresh of these files. Inspect the lockfile before editing and keep this skill's dependency majors explicit.

## Establish the configuration

Read package.json and the lockfile, the actual app entry, Expo config, Babel config, Metro config, Tailwind config, and the CSS entry. Identify Expo Router versus a classic entry and account for `src/app`, monorepos, or a custom project root.

Use `references/expo-setup.md` for the coordinated v4 setup. The invariant is:

- `nativewind@^4` with `tailwindcss@^3.4.17`; native peers resolved through the app's Expo SDK.
- `nativewind/preset` and content globs covering every source of complete utility strings.
- One CSS entry using the Tailwind v3 directives, connected to both Metro's `withNativeWind` input and the real application entry.
- `nativewind/babel` in Babel **presets**, with `jsxImportSource: "nativewind"` on `babel-preset-expo`.
- `nativewind-env.d.ts` referencing `nativewind/types`, without shadowing the package/module name.

Preserve unrelated Metro wrappers, Babel plugins, config plugins, and project module format. Do not replace a working app's configuration wholesale or install a second incompatible Reanimated/Worklets stack.

## Debug in a useful order

1. Verify resolved dependency majors and the first actual error; a cache reset does not repair a Tailwind v4/v3 mismatch.
2. Compile the CSS entry with the project's installed Tailwind v3 CLI. Check content globs, static class strings, and the NativeWind preset.
3. Verify the CSS file, Metro input, and application import refer to the same file. Calculate paths from their real locations, including `src/app/_layout.tsx`.
4. Merge the required Babel/Metro integration, then restart Metro with `npx expo start --clear`.
5. Test an obvious layout/text/colour change on each target platform, then the failing component. A successful web render alone does not prove native interop.

Use `references/troubleshooting.md` for further diagnosis. Resolve bundled reference paths from this skill's directory, not the app's directory.

## Build components

Use literal variant maps rather than dynamically constructing class names the scanner cannot see. `references/patterns.md` covers typed components, explicit override semantics, and accessible Pressable content. Concatenating class strings does not guarantee that the last conflicting utility wins.

Use `references/third-party-components.md` only when a component needs `remapProps` or `cssInterop`; configure interop once, not during every render. Use `references/theming-dark-mode.md` for the v4 colour-scheme and CSS-variable APIs.

Inspect the existing safe-area provider before adding another. Expo Router normally supplies the root integration; separate native roots or modal boundaries may need their own provider. Verify actual insets, nested navigation, and rotation rather than treating provider count as a universal rule.

## Verify and report

Run the project's typecheck and Expo dependency checks, compile/bundle its actual targets, and inspect native/web rendering where those environments are available. Check dark mode, disabled/pressed states, font scaling, safe areas, and third-party components affected by the change. Report the resolved dependency versions, files changed, and platforms actually tested; static configuration inspection is not a device test.

## Sources

Reviewed 2026-09-13 against [NativeWind installation](https://www.nativewind.dev/docs/getting-started/installation) and [custom components](https://www.nativewind.dev/docs/guides/custom-components). For optional conflict merging, [tailwind-merge](https://github.com/dcastil/tailwind-merge) explicitly directs Tailwind v3 users to its v2.6.0 line.
