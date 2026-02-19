# RevenueCat integration (recommended hooks-based approach)

## Goal
Let **Superwall** handle paywalls/experiments while **RevenueCat** handles purchasing, receipts, and entitlement state.

## High-level architecture
1. Your paywall is presented by Superwall via placements.
2. When the user taps “Purchase” on a paywall, Superwall calls your `onPurchase` callback.
3. Your callback executes the RevenueCat purchase flow.
4. You **sync RevenueCat entitlements into Superwall** via `setSubscriptionStatus()` so Superwall’s audience filters and gating logic stay correct.

## Install RevenueCat (react-native-purchases)
Follow RevenueCat’s React Native setup, then ensure the package is installed:

```bash
npm i react-native-purchases
# or pnpm/yarn/bun
```

## Wrap the app with `CustomPurchaseControllerProvider`
Place this provider *outside* `SuperwallProvider`:

```tsx
import Purchases from "react-native-purchases";
import { Platform } from "react-native";
import {
  CustomPurchaseControllerProvider,
  SuperwallProvider,
} from "expo-superwall";

const RC_IOS_KEY = process.env.EXPO_PUBLIC_REVENUECAT_IOS_KEY!;
const RC_ANDROID_KEY = process.env.EXPO_PUBLIC_REVENUECAT_ANDROID_KEY!;

function configureRevenueCat() {
  Purchases.configure({
    apiKey: Platform.OS === "ios" ? RC_IOS_KEY : RC_ANDROID_KEY,
  });
}

export default function App() {
  configureRevenueCat();

  return (
    <CustomPurchaseControllerProvider
      controller={{
        onPurchase: async ({ platform, productId }) => {
          try {
            // Fetch products (subscription + non-subscription) and purchase the matching productId.
            // Exact RevenueCat calls depend on your catalogue and product category.
            // On success: return void.
            // On cancelled/failed: return a PurchaseResult or throw so Superwall records the right outcome.
          } catch (e: any) {
            return { type: "failed", error: String(e?.message ?? e) };
          }
        },
        onPurchaseRestore: async () => {
          try {
            await Purchases.restorePurchases();
          } catch (e: any) {
            return { type: "failed", error: String(e?.message ?? e) };
          }
        },
      }}
    >
      <SuperwallProvider
        apiKeys={{
          ios: process.env.EXPO_PUBLIC_SUPERWALL_IOS_KEY!,
          android: process.env.EXPO_PUBLIC_SUPERWALL_ANDROID_KEY!,
        }}
      >
        <RootNavigator />
        <SubscriptionSync />
      </SuperwallProvider>
    </CustomPurchaseControllerProvider>
  );
}
```

### Important: signal failures correctly
Superwall treats “resolved without failure” as a successful purchase.  
So if your purchase flow is cancelled or errors, **return a failure/cancelled result or throw**.

## Sync subscription status from RevenueCat to Superwall
Use a background component that:
- listens for `CustomerInfo` updates
- maps active entitlements to Superwall entitlements
- sets `"ACTIVE"` or `"INACTIVE"`

```tsx
import { useEffect } from "react";
import Purchases from "react-native-purchases";
import { useUser } from "expo-superwall";

export function SubscriptionSync() {
  const { setSubscriptionStatus } = useUser();

  useEffect(() => {
    const listener = Purchases.addCustomerInfoUpdateListener((customerInfo) => {
      const entitlementIds = Object.keys(customerInfo.entitlements.active);
      setSubscriptionStatus({
        status: entitlementIds.length === 0 ? "INACTIVE" : "ACTIVE",
        entitlements: entitlementIds.map((id) => ({ id, type: "SERVICE_LEVEL" })),
      });
    });

    // Initial sync
    (async () => {
      try {
        const customerInfo = await Purchases.getCustomerInfo();
        const entitlementIds = Object.keys(customerInfo.entitlements.active);
        setSubscriptionStatus({
          status: entitlementIds.length === 0 ? "INACTIVE" : "ACTIVE",
          entitlements: entitlementIds.map((id) => ({ id, type: "SERVICE_LEVEL" })),
        });
      } catch (err) {
        console.error("Failed to sync initial subscription status:", err);
      }
    })();

    return () => listener?.remove();
  }, [setSubscriptionStatus]);

  return null;
}
```

## Legacy (compat) approach: PurchaseController
If your codebase still uses `expo-superwall/compat`, Superwall documents a `PurchaseController` integration pattern. Prefer migrating to the hooks-based provider above for new work.

See `references/MIGRATION_COMPAT.md` and the source doc below.

## Sources
- https://superwall.com/docs/expo/guides/using-revenuecat
- https://superwall.com/docs/expo/sdk-reference/components/CustomPurchaseControllerProvider
