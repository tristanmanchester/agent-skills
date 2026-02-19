# Placements, paywalls, and feature gating

## Mental model
A **placement** is a named event in your app (e.g. `"upgrade_button_tap"`, `"start_workout"`) that Superwall can match to **campaign rules** in the dashboard. When you “register” a placement:
- Superwall evaluates campaign/audience rules on device
- it may present a paywall, skip it, or do nothing
- if you provided a `feature` callback, Superwall can gate whether it runs

## Present a paywall (first test)
Use the `usePlacement` hook:

```tsx
import { usePlacement } from "expo-superwall";
import { Button, Text, View } from "react-native";

export default function PaywallTest() {
  const { registerPlacement, state } = usePlacement({
    onPresent: (info) => console.log("Paywall presented:", info.name),
    onDismiss: (_, result) => console.log("Paywall dismissed:", result.type),
    onSkip: (reason) => console.log("Paywall skipped:", reason.type),
    onError: (error) => console.error("Paywall error:", error),
  });

  return (
    <View>
      <Button
        title="Trigger paywall"
        onPress={() => registerPlacement({ placement: "campaign_trigger" })}
      />
      <Text>State: {state.status}</Text>
    </View>
  );
}
```

## Feature gating via `feature: () => …`
Register a placement with a `feature` callback:

```tsx
await registerPlacement({
  placement: "StartWorkout",
  feature: () => navigation.navigate("Workout"),
});
```

### How “Gated” vs “Non‑Gated” behaves
In the dashboard paywall editor you can choose a **Feature Gating** mode:
- **Non‑Gated**: `feature` runs when the paywall dismisses (whether they purchase or not)
- **Gated**: `feature` runs only if the user is already subscribed or becomes subscribed

If **no paywall** is configured for the placement, `feature` executes immediately.

## Pass parameters for targeting and analytics
Use `params` to attach context the dashboard can use in audience filters:

```ts
await registerPlacement({
  placement: "upgrade_button_tap",
  params: { screen: "settings", variant: "A" },
});
```

Keep params small and avoid PII; use user attributes for user-level properties.

## “Register everything” pattern (recommended)
Centralise placements in one module (e.g. `src/superwall/placements.ts`) so you can:
- keep names consistent
- add params consistently
- retrofit paywalls later without app updates

## Peek at results without presenting a paywall
Use `getPresentationResult` to decide how to render UI (lock icon, etc.):

```ts
import { useSuperwall } from "expo-superwall";
import {
  PresentationResultPaywall,
  PresentationResultHoldout,
  PresentationResultNoAudienceMatch,
} from "expo-superwall/compat";

const { getPresentationResult } = useSuperwall();

const result = await getPresentationResult("premium_feature", { source: "home" });

if (result instanceof PresentationResultPaywall) {
  // would show a paywall
} else if (result instanceof PresentationResultHoldout) {
  // user is in holdout group
} else if (result instanceof PresentationResultNoAudienceMatch) {
  // would not show a paywall
}
```

## Sources
- https://superwall.com/docs/expo/sdk-reference/hooks/usePlacement
- https://superwall.com/docs/expo/quickstart/feature-gating
- https://superwall.com/docs/expo/sdk-reference/getPresentationResult
- https://superwall.com/docs/expo/quickstart/present-your-first-paywall
