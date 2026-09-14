# Android product, base-plan, and offer identity

A displayed offer is part of the purchase the user selected. Never substitute another option merely because the requested one is unavailable.

## Exact selection

Fetch the requested subscription with RevenueCat's `PRODUCT_CATEGORY.SUBSCRIPTION`, inspect its `subscriptionOptions`, and match both the subscription's `productId` and the option's `id`. A base-plan option uses the base plan ID; an offer uses `basePlanId:offerId`. Require exactly one match. An empty explicit offer, an offer without a base plan, a different product, or multiple matches is an error.

Call `Purchases.purchaseSubscriptionOption(option)` with that exact object. Do not probe for old API names or fall back to `purchaseStoreProduct`, `defaultOption`, or the first array entry. Refresh the paywall and let the user choose again when availability or eligibility changed. A deliberately default-selected product is a separate product contract; it does not authorise fallback from an explicit selection.

`examples/custom-purchase-controller.android-offers.tsx` and the pure `selectPlayOption` helper implement this rule. The helper has executable cases for exact base/offer selection, missing offers, wrong products, empty identifiers, and ambiguous matches.

## Outcomes and fulfilment

Use RevenueCat's typed cancellation and payment-pending codes, not message regexes. Return Superwall's explicit `cancelled`, `pending`, `failed`, or `purchased` result. Returning void can count as a conversion under the controller contract, so do not silently fall through.

A completed purchase and an active feature entitlement are different facts. Report a completed charge as purchased, then check the specific entitlement before running the feature. An inactive entitlement after payment requires reconciliation of product mappings, identity, delayed delivery, and provider state; do not mark the store payment failed or retry it automatically. A pending purchase grants no access until entitlement evidence arrives.

## Integration checks

Verify product/base-plan/offer IDs in both dashboards and the actual store response. Check displayed price/trial against the selected option; exercise ineligible and withdrawn offers. Test pending completion after restart, cancelled purchase, account changes, restore, and delayed entitlement publication.

This example covers a direct subscription purchase, not replacement/proration of an existing subscription, personalised-pricing disclosures, promotional offers, or alternative stores. Add those supported current API arguments when required, and test their store-specific semantics rather than guessing.

Sources reviewed 2026-09-13: [RevenueCat purchase API](https://revenuecat.github.io/react-native-purchases-docs/9.7.5/classes/default.html), [SubscriptionOption contract](https://revenuecat.github.io/react-native-purchases-docs/8.2.4/interfaces/SubscriptionOption.html), [Superwall controller results](https://superwall.com/docs/expo/sdk-reference/components/CustomPurchaseControllerProvider).
