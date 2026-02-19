# Events and analytics (useSuperwallEvents)

## When to use
- forward paywall lifecycle events into your analytics stack (Segment, Amplitude, PostHog, etc.)
- debug issues via Superwall logs
- listen to custom paywall actions (e.g. button taps inside paywalls)

## Low-level event hook: `useSuperwallEvents()`
This hook subscribes to native Superwall events and auto-cleans listeners on unmount.

Common callbacks include:
- `onPaywallPresent(paywallInfo)`
- `onPaywallDismiss(paywallInfo, result)`
- `onPaywallSkip(reason)`
- `onPaywallError(error)`
- `onSubscriptionStatusChange(status)`
- `onUserAttributesChange(newAttrs)`
- `onCustomPaywallAction(name)`
- `onLog({ level, scope, message, info, error })`
- plus `onSuperwallEvent(eventInfo)` for raw/typed events

```ts
import { useSuperwallEvents } from "expo-superwall";

export function SuperwallAnalyticsBridge() {
  useSuperwallEvents({
    onPaywallPresent: (info) => analytics.track("paywall_present", { name: info.name }),
    onPaywallDismiss: (info, result) =>
      analytics.track("paywall_dismiss", { name: info.name, result: result.type }),
    onPurchase: (params) =>
      analytics.track("purchase_attempt", { productId: params.productId, platform: params.platform }),
    onLog: ({ level, scope, message, error }) => {
      if (level === "error") console.error("[Superwall]", scope, message, error);
    },
  });

  return null;
}
```

## Custom paywall analytics
If your paywall triggers a custom action (configured in the paywall editor), listen via `onCustomPaywallAction(name)` and forward it.

## Sources
- https://superwall.com/docs/expo/sdk-reference/hooks/useSuperwallEvents
- https://superwall.com/docs/expo/guides/3rd-party-analytics
