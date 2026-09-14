# Choose the purchase owner

## RevenueCat is the billing and entitlement authority

Use `CustomPurchaseControllerProvider` around `SuperwallProvider`. RevenueCat executes the store purchase; the controller returns its outcome and a separate subscription sync mirrors active entitlements. Superwall supplies presentation, placements, campaigns, and the selected product/offer.

This is the default **for the bundled examples**, not a universal requirement that every greenfield Superwall app must replace Superwall's purchasing. Its costs are explicit offer selection, outcome mapping, identity coordination, and ongoing entitlement sync.

## Superwall or an existing implementation completes purchases

Use RevenueCat's current `purchasesAreCompletedBy` configuration when RevenueCat is observing an external purchase owner. Superwall recommends its default purchasing when custom control is unnecessary. An existing native billing integration can also remain the completion owner during a deliberate migration.

Confirm the actual StoreKit version, restore owner, receipt-forwarding/recording behaviour, and RevenueCat entitlement updates. Do not configure observer mode and then silently call RevenueCat purchase methods as a second owner. Historical import is a deliberate `syncPurchasesForResult` checkpoint; it can affect receipt association under the project's restore/transfer policy.

See `examples/observer-mode-migration.tsx` for configuration and an explicit import helper. The filename identifies the example's use case, not a claim that observation is obsolete.

## Decisions independent of the owner

Determine login-first versus guest-first, strict account ownership versus transfer-friendly restore, single versus multiple entitlement tiers, Android base-plan/offer selection, and server-notification identity. These are product contracts, not library defaults to infer from a demo.

Reuse stable opaque backend IDs across the two systems. Check iOS appAccountToken/UUID handling and Android account identifiers against the installed SDKs when server reconciliation depends on them. Protect backend access using server evidence, not a client paywall callback.

## Source

Reviewed 2026-09-13: [Superwall RevenueCat guide](https://superwall.com/docs/expo/guides/using-revenuecat), [custom purchase controller](https://superwall.com/docs/expo/sdk-reference/components/CustomPurchaseControllerProvider), [RevenueCat configuration and sync API](https://revenuecat.github.io/react-native-purchases-docs/9.7.5/classes/default.html).
