# Coordinated Expo setup for NativeWind v4

These examples target NativeWind **4** and Tailwind CSS **3**. Inspect the existing app and merge changes. Do not copy the NativeWind v5/Tailwind v4 preview setup into this stack.

## Dependencies

Use the existing package manager; npm equivalents are:

```bash
npm install 'nativewind@^4'
npm install --save-dev 'tailwindcss@^3.4.17'
npx expo install react-native-reanimated react-native-safe-area-context
```

Retain the Expo-compatible `babel-preset-expo` already supplied by the app; install it with `npx expo install babel-preset-expo` only when absent. Follow the installed Reanimated version's Worklets requirements and Expo compatibility instead of installing arbitrary latest native packages. Commit the lockfile and run the project's dependency checks.

Formatting and variant libraries are optional, not prerequisites. When using `tailwind-merge` with Tailwind v3, use its compatible v2.6.0 line, not its Tailwind-v4-focused latest major.

For a new app, use the current official Expo project creation flow, then apply these explicit dependency constraints. Check generated dependencies rather than trusting a template name to imply a particular NativeWind major.

## Tailwind configuration

Adapt paths to the actual project. This CommonJS example covers both common Router locations and shared components:

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './App.{js,jsx,ts,tsx}',
    './app/**/*.{js,jsx,ts,tsx}',
    './src/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
  ],
  presets: [require('nativewind/preset')],
  theme: { extend: {} },
  plugins: [],
};
```

Follow the project's module format when choosing `.js`/`.cjs` or ESM configuration. Monorepo packages containing classes also need content coverage. Prefer literal complete class strings; adding broad filesystem globs is not a substitute for identifying the source directories.

## CSS entry

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

Save as the chosen CSS entry, commonly `global.css`. These are Tailwind **v3** directives, not the v4 CSS-first configuration.

## Babel

```js
module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ['babel-preset-expo', { jsxImportSource: 'nativewind' }],
      'nativewind/babel',
    ],
  };
};
```

`nativewind/babel` belongs in **presets**, not plugins. Merge existing required compiler/animation/plugin configuration; do not duplicate plugins the matching Expo preset already configures.

## Metro

```js
const { getDefaultConfig } = require('expo/metro-config');
const { withNativeWind } = require('nativewind/metro');
const config = getDefaultConfig(__dirname);
module.exports = withNativeWind(config, { input: './global.css' });
```

Preserve other required wrappers and resolver changes. For web targets, verify `expo.web.bundler` is `metro` in the resolved Expo config.

## Import from the real entry

For root `App.tsx`: `import './global.css'`.
For root `app/_layout.tsx`: `import '../global.css'`.
For `src/app/_layout.tsx` with CSS at project root: `import '../../global.css'`.

These are examples, not detection rules. Import once at the application root and check the actual relative path.

Add `nativewind-env.d.ts`:

```ts
/// <reference types="nativewind/types" />
```

Do not name the declaration `nativewind.d.ts` or another name that shadows an actual module/directory.

## Verification

Run the project's installed Tailwind v3 CLI against the CSS entry into a temporary output, then its TypeScript and Expo checks. Clear Metro after changing configuration. Test visible utility output on the intended native platforms and web separately. Inspect the resolved lockfile for NativeWind 4 and Tailwind 3; a successful dependency install alone is insufficient.

Primary source, reviewed 2026-09-13: [NativeWind Expo installation](https://www.nativewind.dev/docs/getting-started/installation).
