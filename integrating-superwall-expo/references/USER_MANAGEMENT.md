# User management (identify, sign out, attributes)

## When to use
- you have login/logout
- you want campaigns/audiences based on user properties
- you want to show user info on paywalls (text variables)

## Core API: `useUser()`
The `useUser` hook provides:
- `identify(userId, options?)`
- `signOut()`
- `update(attrs | updaterFn)` (merge semantics)
- access to `user` and `subscriptionStatus`

```tsx
import { useUser } from "expo-superwall";
import { Button, Text, View } from "react-native";

export function UserManagementScreen() {
  const { identify, signOut, update, user, subscriptionStatus } = useUser();

  return (
    <View style={{ padding: 16 }}>
      <Text>Subscription: {subscriptionStatus?.status ?? "unknown"}</Text>
      <Text>User: {user?.appUserId ?? "anonymous"}</Text>

      <Button title="Identify" onPress={() => identify(`user_${Date.now()}`)} />
      <Button title="Sign out" onPress={() => signOut()} />

      <Button
        title="Set attributes"
        onPress={() =>
          update({
            plan: "free",
            locale: "en_GB",
          })
        }
      />
    </View>
  );
}
```

## Identify options
`identify` supports options such as:

- `restorePaywallAssignments?: boolean`

Use this when you need to restore a user’s prior experiment/paywall assignments after re-identifying.

## Setting user attributes
Attributes are merged with existing attributes:
- existing keys are overwritten
- other keys stay untouched
- pass `null` to unset/delete a value

```ts
await update({
  email: user.email,
  username: user.username,
  profilePic: user.profilePicUrl,
  stripe_customer_id: user.stripeCustomerId, // optional (web checkout prefill)
});

// Update based on previous attrs:
await update((old) => ({
  ...old,
  counter: (old.counter || 0) + 1,
}));

// Unset a value:
await update({ profilePic: null });
```

## Integration attributes
Use `setIntegrationAttributes()` and `getIntegrationAttributes()` to attach identifiers that other systems may need (depending on your stack).

## Sources
- https://superwall.com/docs/expo/sdk-reference/hooks/useUser
- https://superwall.com/docs/expo/quickstart/setting-user-properties
- https://superwall.com/docs/expo/guides/managing-users
