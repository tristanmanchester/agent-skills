# Expo + Clerk quickstart (condensed)

This is a condensed checklist based on Clerk’s Expo quickstart.

## Checklist

- [ ] In Clerk Dashboard, enable **Native API** (required for native integration).
- [ ] Install `@clerk/clerk-expo`
- [ ] Add `.env` with: `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY=...`
- [ ] Add `<ClerkProvider>` to the root of the app
- [ ] Add secure token caching via `expo-secure-store` + `tokenCache`
- [ ] Create custom auth screens (native uses **custom flows**)
- [ ] Add sign-out (`useClerk().signOut()`)
- [ ] (Recommended) enable OTA updates so Clerk fixes can ship without a store resubmission

## Root layout (Expo Router)

```tsx
import { ClerkProvider } from '@clerk/clerk-expo'
import { tokenCache } from '@clerk/clerk-expo/token-cache'
import { Stack } from 'expo-router'

export default function RootLayout() {
  return (
    <ClerkProvider tokenCache={tokenCache}>
      <Stack>
        {/* route groups like (home), (auth), etc */}
      </Stack>
    </ClerkProvider>
  )
}
```

## Auth route group layout guard

```tsx
import { Redirect, Stack } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

export default function AuthRoutesLayout() {
  const { isSignedIn } = useAuth()
  if (isSignedIn) return <Redirect href="/" />
  return <Stack />
}
```

## Sign-up outline (email + password + email code)

High-level flow:

1) `signUp.create({ emailAddress, password })`
2) `signUp.prepareEmailAddressVerification({ strategy: 'email_code' })`
3) `signUp.attemptEmailAddressVerification({ code })`
4) When `status === 'complete'`, call `setActive({ session: createdSessionId })`

## Sign-in outline (identifier + password)

High-level flow:

1) `signIn.create({ identifier, password })`
2) If `status === 'complete'`, call `setActive({ session: createdSessionId })`
3) If additional steps are required (e.g. MFA), follow the object’s `status` / `supportedFirstFactors`.

## Sign out

```tsx
import { useClerk } from '@clerk/clerk-expo'

export function SignOutButton() {
  const { signOut } = useClerk()
  return <Button title="Sign out" onPress={() => signOut()} />
}
```

## OTA updates (recommended)

Clerk recommends implementing over-the-air updates (Expo Updates) so security patches/feature updates can ship without resubmitting the app to marketplaces.
