# Configuration (SuperwallProvider + options)

## Golden rule
Superwall **does not refetch its configuration during hot reloads**. If you add/edit products, paywalls, or campaigns in the dashboard, fully restart the app to see changes.

## Minimal root setup (recommended)
Wrap your app with `<SuperwallProvider />` and supply API keys:

```tsx
import { SuperwallProvider } from "expo-superwall";

export default function App() {
  return (
    <SuperwallProvider
      apiKeys={{
        ios: process.env.EXPO_PUBLIC_SUPERWALL_IOS_KEY!,
        android: process.env.EXPO_PUBLIC_SUPERWALL_ANDROID_KEY!,
      }}
    >
      {/* app routes */}
    </SuperwallProvider>
  );
}
```

### Prefer EXPO_PUBLIC_* env vars
Expo only exposes env vars to the JS bundle if they’re prefixed with `EXPO_PUBLIC_…`.

## Add loading/error UI gates
Use the helper components to avoid “blank screen” failures:

```tsx
import {
  SuperwallProvider,
  SuperwallLoading,
  SuperwallLoaded,
  SuperwallError,
} from "expo-superwall";
import { ActivityIndicator, Text, View } from "react-native";

export default function App() {
  return (
    <SuperwallProvider apiKeys={{ ios: "YOUR_KEY", android: "YOUR_KEY" }}>
      <SuperwallLoading>
        <ActivityIndicator style={{ flex: 1 }} />
      </SuperwallLoading>

      <SuperwallError>
        {(error) => (
          <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
            <Text>Superwall failed to load</Text>
            <Text>{error}</Text>
          </View>
        )}
      </SuperwallError>

      <SuperwallLoaded>
        <RootNavigator />
      </SuperwallLoaded>
    </SuperwallProvider>
  );
}
```

## Options (PartialSuperwallOptions)
You can pass `options` to `SuperwallProvider` for advanced behaviour.

### Common options used in Expo apps
Superwall exposes paywall-related options such as:
- observing purchases made by other SDKs (e.g., RevenueCat observer mode)
- passing identifiers to the Play Store on Android
- preloading paywalls
- external data collection toggles

Example (edit to your needs):

```ts
import type { PartialSuperwallOptions } from "expo-superwall";

export const options: PartialSuperwallOptions = {
  paywalls: {
    shouldObservePurchases: true,
    isExternalDataCollectionEnabled: true,
    shouldPreloadAllPaywalls: false,
    passIdentifiersToPlayStore: true, // Android only
  },
  // networkEnvironment: "sandbox", // optional for testing (if supported in your SDK version)
};
```

## Android back button rerouting (optional)
If a paywall has “Reroute back button” enabled in the dashboard, you can intercept the back action on Android:

```tsx
<SuperwallProvider
  apiKeys={{ ios: "ios_key", android: "android_key" }}
  options={{
    paywalls: {
      onBackPressed: (paywallInfo) => {
        if (paywallInfo.identifier === "survey") {
          showExitConfirmation();
          return true; // consume back press
        }
        return false; // default dismissal
      },
    },
  }}
/>
```

## Sources
- https://superwall.com/docs/expo/quickstart/configure
- https://superwall.com/docs/expo/sdk-reference/components/SuperwallProvider
- https://superwall.com/docs/expo/quickstart/configure-the-sdk
