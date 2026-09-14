# Implement the chosen contract

## Preflight

Record resolved Expo, React Native, RevenueCat, and Superwall versions; actual native minima; bundle/package IDs; product/entitlement mapping; auth policy; restore/transfer policy; and transaction owner. Read existing code before introducing providers or configuration. SDK version ranges in package.json do not prove the resolved lockfile or native binary version.

Install `expo-superwall` and `react-native-purchases` through the existing Expo package workflow. RevenueCat UI is optional when Superwall supplies the paywall. `expo-build-properties` is optional when existing Expo defaults already meet all native requirements. Never lower the app's deployment targets to copied values.

Only the providers' public client SDK keys belong in `EXPO_PUBLIC_*` variables. Secret management and webhook verification remain server-side. Inspect the trusted project's resolved Expo config and merged Android manifest; the source manifest alone cannot establish all merged billing entries or the launch activity's effective configuration.

## Custom controller path

`examples/monetization.shared.tsx` demonstrates configuration-before-use, a current typed purchase controller, and RevenueCat-to-Superwall subscription sync. Adapt its single bootstrap owner to the app; do not add it alongside an existing configure call. Its default mounting is guest-oriented. For login-first apps, resolve the user ID first and pass `initialAppUserId` before mounting. Changing that prop is not a substitute for a proper identity transition.

The Android helper delegates to `selectPlayOption` in `examples/billing-contracts.ts`, which rejects unavailable, ambiguous, or mismatched options. It then calls `purchaseSubscriptionOption` directly. There are no API-generation fallbacks or substitutions for an explicit offer. This baseline does not implement upgrades/downgrades, promotional/win-back offers, Amazon billing, or web checkout; add the relevant current store contract deliberately when the product requires it.

The store callback reports payment truthfully. Entitlement unlock is checked separately against the feature's actual entitlement. Keep a paid-but-unfulfilled state visible and reconcile configuration, store, and RevenueCat evidence rather than inviting another charge. Pending is not success; restore success does not necessarily mean an active subscription exists.

## CustomerInfo lifecycle

`subscribeCustomerInfo` registers one callback, seeds from `getCustomerInfo`, prevents a late initial seed overwriting a newer event, and removes that exact callback. Mount one entitlement sync per billing owner. Dispose it on identity transitions and read fresh information after the new identity is established. Preserve unknown/unavailable states during failures instead of declaring the user inactive.

The pure helper tests cover listener identity, repeated disposal, delayed responses, fetch failure, and offer selection. They do not establish native SDK callback ordering, React lifecycle integration, or store availability; those need application tests.

## Identity and feature gating

`examples/auth-sync.example.tsx` illustrates serialised native identity calls. The parent auth coordinator owns a monotonically increasing `identityRevision`; update it synchronously with every auth resolution/change. Track the revision acknowledged by `onSynchronized` and derive `billingIdentityReady` by comparing it with the current revision. Keep the callback stable. Never show a previous account's entitlement while signed out or while a revision is unresolved.

Pass the gate into `MonetizationProviders` and pass both the gate and revision to premium actions. `examples/premium-gate.example.tsx` rejects delayed paywall/CustomerInfo callbacks from earlier revisions. Use the current user's server session to authorise server resources independently. Gate or defer account switching while purchase/restore is in progress; no React cleanup can cancel a store transaction already launched.

Known account A→B uses `Purchases.logIn(B)` and Superwall `identify(B)` without manufacturing an anonymous step. On sign-out, reset Superwall; call RevenueCat `logOut` only for real guest mode and not when it is already anonymous. Login-required apps remain blocked until another identified account is ready.

## Observer path and historical import

Use the separate observer configuration example, not both examples together. The external owner remains responsible for finishing transactions. Choose its actual StoreKit version rather than assuming it from a snippet. Verify that completed purchases reach RevenueCat.

Use `syncPurchasesForResult` only at a deliberate, policy-approved recovery or migration checkpoint. Restore remains a user action. Do not trigger import from an effect that reruns on every mount or login.

## Verification and delivery

Typecheck against installed package declarations. Test native iOS and Android builds using configured store test products. Include explicit unavailable offers, all store outcomes, empty restore, delayed fulfilment, repeated mount/unmount, account switches during delayed callbacks, signed-out premium gating, reinstall, and backend identity. Recheck after relevant dashboard/product changes.

Record static checks, mocked tests, SDK integration checks, and real store tests separately. Report manual dashboard/console requirements and unresolved failures without presenting a source inventory as production readiness.

Sources reviewed 2026-09-13: [RevenueCat React Native API](https://revenuecat.github.io/react-native-purchases-docs/9.7.5/classes/default.html), [Superwall controller contract](https://superwall.com/docs/expo/sdk-reference/components/CustomPurchaseControllerProvider), [RevenueCat Expo setup](https://www.revenuecat.com/docs/getting-started/installation/expo).
