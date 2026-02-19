# Migration / compat API (`expo-superwall/compat`)

## When to use
- the repo already uses the legacy `react-native-superwall` API style
- you need minimal-diff migration while adopting the Expo SDK
- you need delegate / class-based patterns for older integrations

For new work, prefer the hooks-based API (`SuperwallProvider`, `usePlacement`, `useUser`, etc.).

## Install
```bash
npx expo install expo-superwall
```

## Configure (compat)
```ts
import Superwall from "expo-superwall/compat";
import { Platform } from "react-native";

await Superwall.configure({
  apiKey: Platform.OS === "ios" ? IOS_KEY : ANDROID_KEY,
});
```

### Android identifiers (compat)
```ts
await Superwall.configure({
  apiKey: Platform.OS === "ios" ? IOS_KEY : ANDROID_KEY,
  options: Platform.OS === "android" ? { passIdentifiersToPlayStore: true } : undefined,
});
```

## Identify + attributes
```ts
await Superwall.shared.identify({ userId });
await Superwall.shared.setUserAttributes({
  someCustomVal: "abc",
  platform: Platform.OS,
  timestamp: new Date().toISOString(),
});
```

## Register a placement (present paywall / gate feature)
```ts
Superwall.shared.register({
  placement: "yourPlacementName",
  feature() {
    console.log("Feature called!");
  },
});
```

## Listen to events via delegate
```ts
import {
  EventType,
  SuperwallDelegate,
  type SuperwallEventInfo,
} from "expo-superwall/compat";

export class MyDelegate extends SuperwallDelegate {
  handleSuperwallEvent(eventInfo: SuperwallEventInfo) {
    switch (eventInfo.event.type) {
      case EventType.paywallOpen:
        console.log("Paywall opened");
        break;
      case EventType.paywallClose:
        console.log("Paywall closed");
        break;
    }
  }
}

// set delegate
const delegate = new MyDelegate();
await Superwall.shared.setDelegate(delegate);
```

## Sources
- https://superwall.com/docs/expo/guides/migrating-react-native
- https://superwall.com/docs/expo/sdk-reference/getPresentationResult
