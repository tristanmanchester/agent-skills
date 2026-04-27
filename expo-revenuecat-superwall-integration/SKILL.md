---
name: expo-revenuecat-superwall-integration
description: Adds, repairs, or migrates a production-grade RevenueCat plus Superwall integration in a React Native Expo app for iOS and Android. Chooses between CustomPurchaseControllerProvider and purchasesAreCompletedBy or observer-mode migration, wires Expo config and development builds, syncs identities and entitlements, handles Android base plans and offers, iOS UUID appAccountToken quirks, restore behaviour, analytics, testing, and troubleshooting. Use when the user asks to add subscriptions, paywalls, RevenueCat, Superwall, entitlements, restore flows, account switching, or monetisation migration in an Expo app. Do not use for bare React Native, RevenueCat-only UI work, or web-only billing.
license: MIT
compatibility: Designed for coding agents editing a React Native Expo repository. Best for Expo SDK 53 or newer apps using development builds, iOS deployment target 15.1 or higher, and Android min SDK 23 or higher.
metadata:
  author: OpenAI
  version: "2.0.0"
  category: mobile-monetization
  stack: react-native-expo
  platforms:
    - ios
    - android
  integrations:
    - revenuecat
    - superwall
---
# Expo RevenueCat plus Superwall Integration

Use this skill to add or repair a modern RevenueCat plus Superwall stack in a React Native Expo app.

## What this skill should do

- Choose the correct monetisation architecture before editing code.
- Integrate with the repository's existing app shell, auth layer, and state management.
- Prefer safe, production-ready defaults over the shortest possible demo.
- Leave the user with code changes plus a clear list of remaining dashboard, store, and testing steps.

## Critical rules

- Treat this as an Expo development-build integration, not an Expo Go integration.
- Target Expo SDK 53 or newer.
- Target iOS deployment target 15.1 or newer and Android min SDK 23 or newer.
- Use public SDK keys only in the client.
- Configure RevenueCat exactly once.
- Mount Superwall near the app root exactly once.
- Use the same stable, non-guessable, non-PII user identifier in RevenueCat and Superwall when the product has authentication.
- Never use email addresses as RevenueCat or Superwall user IDs.
- Do not call `syncPurchases()` on every launch. Use it only for deliberate migration or account-recovery scenarios.
- `restorePurchases()` is user-triggered. Do not hide it inside startup code.
- On Android, ensure the launch mode is `standard` or `singleTop`.
- Prefer a full app restart after Superwall dashboard changes during Expo development.

## First actions

1. Inspect the repository before editing:
   - `package.json`
   - `app.json`, `app.config.js`, or `app.config.ts`
   - `App.tsx` or `app/_layout.tsx`
   - any existing auth provider
   - any existing purchase, paywall, or entitlement code

2. Run the validator if Python is available:
   - `python3 scripts/validate_expo_setup.py`
   - or `python3 scripts/validate_expo_setup.py --project-root /path/to/app`

3. Answer these six preflight questions before choosing code:
   - Is the app login-first, login-optional, or guest-first
   - Is there existing purchase completion logic already in the repo
   - Does Google Play use multiple base plans or offers
   - Are App Store Server Notifications, Google server notifications, webhooks, or backend attribution in scope
   - Is the entitlement model single-tier or multi-tier
   - Does the product need strict account ownership, or easy restore across account confusion

4. Open only the references you need:
   - Core workflow: `references/implementation-playbook.md`
   - Architecture choice: `references/architecture-decision-tree.md`
   - Identity and restores: `references/identity-and-restore-behaviour.md`
   - Android offers: `references/android-base-plans-offers-and-pending.md`
   - iOS UUID and server notifications: `references/ios-uuid-appaccounttoken-and-server-notifications.md`
   - Observability and verification: `references/observability-and-entitlement-verification.md`
   - Test planning: `references/testing-matrix.md`
   - Dashboard alignment: `references/dashboard-checklist.md`
   - Failure modes: `references/troubleshooting.md`

## Architecture choice

### Default for most new Expo apps

Choose **Architecture A: CustomPurchaseControllerProvider** when:

- Superwall is the paywall surface.
- RevenueCat is the purchase and entitlement source of truth.
- The app does not already have its own mature purchase completion pipeline.
- You want the cleanest modern Expo integration.

Use:
- `references/architecture-decision-tree.md`
- `references/examples/monetization.shared.tsx`
- `references/examples/app.example.tsx`
- `references/examples/expo-router-layout.example.tsx`
- `references/examples/custom-purchase-controller.android-offers.tsx`

### Use the migration path when the repo already owns purchase completion

Choose **Architecture B: purchasesAreCompletedBy / observer-mode migration** when:

- The app already finishes transactions itself.
- The user explicitly wants to keep existing IAP code.
- You are layering RevenueCat analytics, entitlements, or dashboards onto an existing billing implementation.
- You must import historical purchases carefully.

Use:
- `references/architecture-decision-tree.md`
- `references/examples/observer-mode-migration.tsx`
- `references/identity-and-restore-behaviour.md`

## Shared implementation workflow

### 1. Audit the repo

Collect these facts before changing code:

- Expo SDK version
- package manager
- router style: Expo Router or plain `App.tsx`
- whether `expo-superwall`, `react-native-purchases`, and `expo-build-properties` are already installed
- current iOS deployment target and Android min SDK
- whether the app has auth
- whether the repo already has RevenueCat, Superwall, StoreKit, Google Play Billing, or `react-native-iap` code
- whether the project already ships one-time products in addition to subscriptions

### 2. Align dashboards before deep code edits

Confirm the conceptual setup first:

- RevenueCat project exists for iOS and Android
- store products exist
- entitlements exist
- offerings exist where needed
- Superwall project exists
- Superwall public keys exist for both platforms
- placements and campaigns exist
- product IDs and entitlement IDs match the intended runtime mapping

Use `references/dashboard-checklist.md`.

### 3. Install only the packages you actually need

Base stack:

- `npx expo install expo-superwall react-native-purchases expo-build-properties`

Optional only if the user explicitly wants RevenueCat UI screens such as a customer center:

- `npx expo install react-native-purchases-ui`

Do not add `react-native-purchases-ui` just because RevenueCat is installed.

### 4. Update Expo config

Add or repair `expo-build-properties` and set platform minimums. Preserve the repository's config style and existing plugins.

### 5. Configure RevenueCat once

- Use the correct public key for the current platform.
- Configure once on startup.
- If the app always requires a known user ID, prefer configuring with that ID instead of creating an anonymous state first.
- If the app allows guests, configure without an App User ID and later call `logIn()` when auth resolves.

### 6. Mount providers once near the root

For Architecture A, the normal order is:

1. configure RevenueCat
2. mount `CustomPurchaseControllerProvider`
3. mount `SuperwallProvider`
4. show `SuperwallLoading`
5. render the app inside `SuperwallLoaded`
6. mount one subscription sync component inside the loaded tree

### 7. Sync RevenueCat entitlements into Superwall

When Superwall is not directly owning purchase state, map RevenueCat entitlements into `setSubscriptionStatus`.

- Fetch `CustomerInfo` on launch or when premium UI opens.
- Subscribe to `addCustomerInfoUpdateListener`.
- Map active entitlement IDs into Superwall entitlements.
- Prefer syncing the full entitlement set, not just a boolean.

### 8. Sync identities deliberately

- Reuse the app's real auth state.
- For login-first apps, prefer configuring RevenueCat with a custom App User ID from the start.
- For guest-first apps, configure anonymously, then on login call `Purchases.logIn(userId)` and `identify(userId)`.
- If switching from one known account to another, call `logIn(newUserId)` directly. Do not force a pointless logout first.
- Only call `logOut()` if the product truly supports an anonymous post-logout state.

See `references/identity-and-restore-behaviour.md` and `references/examples/auth-sync.example.tsx`.

### 9. Register placements from premium entry points

- Use business-action placement names such as `upgrade_pro`, `remove_limits`, or `export_pdf`.
- Prefer placement-driven gating and dashboard audiences over hard-coded paywall branching.
- Use `getPresentationResult()` only when you need to inspect what Superwall would do before presenting.

### 10. Add observability

- Forward Superwall events into the app's analytics pipeline.
- Keep debug logs enabled in development only.
- Consider checking RevenueCat trusted entitlement verification in high-risk apps.

See `references/observability-and-entitlement-verification.md`.

### 11. Test with a matrix, not one happy path

Always verify:

- cold start on iOS and Android
- purchase success
- cancel flow
- pending flow where relevant
- restore
- guest to logged-in transition
- account switch
- reinstall
- dashboard changes after a full restart
- entitlement unlock in UI
- webhook or server-notification identity consistency when relevant

Use `references/testing-matrix.md`.

## What to avoid

- Do not use `expo-superwall/compat` for new work.
- Do not promise real Superwall support inside Expo Go.
- Do not call `restorePurchases()` automatically during startup.
- Do not call `syncPurchases()` on every launch.
- Do not use emails, IDFA, device IDs, or hardcoded strings as billing IDs.
- Do not leave duplicate purchase flows in place.
- Do not ship Android API 21 just because Superwall alone supports it; the combined stack needs Android 23 or newer.

## Final answer expectations

When you finish editing a repo, your response should include:

- the files changed
- the chosen architecture and why
- any manual RevenueCat, Superwall, App Store Connect, or Play Console steps still required
- any assumptions about entitlements, product IDs, placements, restore behaviour, or account model
- any migration debt intentionally left in place
- how to run and test the development build

## Authsome (optional)

Optional: [authsome](https://github.com/manojbajaj95/authsome) with the authsome skill handles credential injection for agent runs; you do not need to manually export the RevenueCat and Superwall `EXPO_PUBLIC_*` API keys (and related keys) your app config uses, on that path, for example.

