# Subscription status (tracking, listening, manual sync)

## Built-in state
Superwall maintains a `subscriptionStatus` object you can read via `useUser()`:

- `status`: `"ACTIVE" | "INACTIVE" | "UNKNOWN"`
- `entitlements`: list of active entitlements (present when status is `"ACTIVE"`)

```tsx
import { useUser } from "expo-superwall";

export function ProBadge() {
  const { subscriptionStatus } = useUser();
  const isPro = subscriptionStatus?.status === "ACTIVE";
  return <Text>{isPro ? "Pro" : "Free"}</Text>;
}
```

## Listen for changes (real time)
Use `useSuperwallEvents` for reactive UI updates:

```ts
import { useSuperwallEvents } from "expo-superwall";

useSuperwallEvents({
  onSubscriptionStatusChange: (status) => {
    console.log("New status:", status.status);
  },
});
```

## Check for a specific entitlement
Useful for multi-tier products:

```ts
const hasGold = subscriptionStatus?.entitlements?.some((e) => e.id === "gold");
```

## When you must set subscription status manually
If purchases are handled externally (RevenueCat, custom billing, web checkout redemption flows), sync the state into Superwall:

```ts
import { useUser } from "expo-superwall";

const { setSubscriptionStatus } = useUser();

setSubscriptionStatus({
  status: "ACTIVE",
  entitlements: [{ id: "gold", type: "SERVICE_LEVEL" }],
});
```

### RevenueCat mapping (common pattern)
Map active RevenueCat entitlements to Superwall entitlements:

```ts
const entitlementIds = Object.keys(customerInfo.entitlements.active);

setSubscriptionStatus({
  status: entitlementIds.length === 0 ? "INACTIVE" : "ACTIVE",
  entitlements: entitlementIds.map((id) => ({ id, type: "SERVICE_LEVEL" })),
});
```

## Sources
- https://superwall.com/docs/expo/quickstart/tracking-subscription-state
- https://superwall.com/docs/expo/sdk-reference/hooks/useSuperwallEvents
- https://superwall.com/docs/expo/sdk-reference/hooks/useUser
