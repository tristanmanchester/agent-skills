# Setting a locale (override)

## When to use
- you want Superwall localisation/currency to follow an in-app language picker
- you need deterministic locale for QA/testing

## Approach
Pass a locale identifier via `options.localeIdentifier` when configuring Superwall.

```tsx
<SuperwallProvider
  apiKeys={{ ios: "ios_key", android: "android_key" }}
  options={{
    localeIdentifier: "en_GB",
  }}
>
  <App />
</SuperwallProvider>
```

## Verify
You can inspect device attributes (including locale) using `useSuperwall().getDeviceAttributes()`.

## Sources
- https://superwall.com/docs/expo/guides/setting-a-locale
- https://superwall.com/docs/expo/sdk-reference/hooks/useSuperwall
