---
name: expo-revenuecat-superwall-integration
description: Integrate or repair RevenueCat and Superwall together in an Expo React Native app. Use for their shared purchase ownership, Android offer selection, billing identity, entitlement sync, restore, or migration flows; not for web billing or unrelated paywall providers.
license: MIT
compatibility: Expo development builds on iOS/Android, expo-superwall's current provider API, and react-native-purchases 9.7 or newer. Resolve native platform requirements from the installed Expo and SDK versions. Offline checks need Python 3.10+, Node.js, and TypeScript.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# RevenueCat and Superwall in Expo

Choose one owner for purchase completion before writing code. Preserve the application's account and restore policy; a paywall integration is not permission to change who owns purchases.

## Inspect and choose

Read the lockfile, Expo configuration, actual application root, auth coordinator, existing billing calls, product catalogue, and entitlement checks. Resolve public SDK keys through the project's environment handling; never embed secret API keys or webhook credentials in client code.

Use `references/architecture-decision-tree.md` to choose:

- **RevenueCat owns purchase execution and entitlements:** use Superwall's `CustomPurchaseControllerProvider`, exact RevenueCat purchase APIs, and a single full-entitlement sync into Superwall. The bundled integration examples cover this path.
- **Superwall or an existing billing implementation owns completion:** RevenueCat can observe through `purchasesAreCompletedBy`. This is a current architecture, not merely a deprecated migration workaround. Set the actual StoreKit version and prove receipt/entitlement propagation. Never let both SDKs finish a transaction.

Expo Go is not the native store-test environment. Install only required packages with the project's package manager and `npx expo install`; add `expo-build-properties` only when an actual override is needed. Do not lower platform minima to an old example's Android 23/iOS 15.1 values.

## Implement the contracts

1. **Bootstrap once.** Wait for RevenueCat configuration before mounting code that calls it. Reuse an existing configuration owner instead of adding another. Handle Superwall configuration failures visibly.
2. **Match the presented product.** Resolve Android subscriptions by product, base plan, and optional offer. An explicit unavailable offer fails closed: refresh the paywall, never substitute `defaultOption`, the first option, or a generic purchase API. See `references/android-base-plans-offers-and-pending.md`.
3. **Return the actual store outcome.** Distinguish purchased, cancelled, pending, and failed. A completed charge with an inactive entitlement is a fulfilment problem, not evidence that payment failed. Gate the feature and reconcile; never charge again to repair fulfilment. A successful restore may legitimately find no active access.
4. **Subscribe and clean up correctly.** `addCustomerInfoUpdateListener` returns void. Remove the same callback with `removeCustomerInfoUpdateListener`. Register before the initial fetch and prevent a stale initial result from replacing a newer event. Map the full active entitlement set; network failure is not an inactive subscription.
5. **Gate account transitions.** Use the same opaque billing ID in both systems. Serialise native identity calls; effect cleanup cannot cancel them. Increment an identity revision when auth changes and block purchase/restore/feature actions until that revision is synchronised. Defer account switching while a store operation is in flight. Known-to-known changes use `logIn(newId)` directly; create anonymous state only when the product permits it.
6. **Restore deliberately.** Restore is user-triggered. Historical import/recovery uses an approved checkpoint and `syncPurchasesForResult`, not a mount effect or every-launch sync. Review transfer/alias behaviour before invoking it.

`references/implementation-playbook.md` connects the examples to the app shell. They are integration patterns, not a replacement auth system. `references/examples/app.example.tsx` and the simple Router shell demonstrate guest-only mounting; authenticated apps must supply the identity gate.

## Verify

Resolve `SKILL_DIR` to this skill's installation directory and pass the app separately:

```bash
python3 "$SKILL_DIR/scripts/validate_expo_setup.py" --project-root /path/to/app
python3 -m unittest discover -s "$SKILL_DIR/tests" -v
node --test "$SKILL_DIR/tests/billing-contracts.test.cjs"
```

The scanner returns a **static inventory**, not submission or billing readiness. It never executes dynamic Expo config or exports environment values. Zero exit status means the inventory completed without missing core dependencies; regex occurrences do not prove a provider is mounted or a callback runs.

Typecheck the adapted examples against the app's installed SDKs, inspect the resolved config and merged native manifests, then test real development/store-sandbox builds. Cover unavailable explicit offers, repeated mount/unmount, initial-fetch/listener races, A→B→A account changes, sign-out, purchase cancellation/pending/success, restore with no access, purchase-with-delayed-entitlement, reinstall, and backend identity. Use `references/testing-matrix.md` and `references/dashboard-checklist.md` for the broader checklist.

Report the chosen owner, changed files, exact package versions, tests actually run, manual dashboard/store steps, and unresolved ownership or fulfilment failures. Client-side UI gating does not replace server-side authorisation.

## Focused references

- `references/identity-and-restore-behaviour.md`: account/restore policy investigation.
- `references/ios-uuid-appaccounttoken-and-server-notifications.md`: server-notification identity questions; verify against installed SDK behaviour.
- `references/observability-and-entitlement-verification.md`: telemetry and verification.
- `references/troubleshooting.md`: failure investigation.

Primary contracts reviewed 2026-09-13: [RevenueCat React Native API](https://revenuecat.github.io/react-native-purchases-docs/9.7.5/classes/default.html), [Superwall purchase controller](https://superwall.com/docs/expo/sdk-reference/components/CustomPurchaseControllerProvider), [Superwall RevenueCat integration](https://superwall.com/docs/expo/guides/using-revenuecat), and [RevenueCat Expo setup](https://www.revenuecat.com/docs/getting-started/installation/expo).
