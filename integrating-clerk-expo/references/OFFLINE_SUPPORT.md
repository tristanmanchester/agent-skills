# Offline support (experimental) for Expo Clerk SDK

This is based on Clerk’s experimental offline support for Expo.

## What it does (conceptually)

- Lets the Clerk SDK **bootstrap offline** using cached resources.
- Makes `isLoaded` resolve more reliably when offline (one fetch attempt, then fallback).
- Allows `useAuth().getToken()` to return cached tokens when offline.
- Surfaces network errors (so you can handle them in custom flows).

## Enable: tokenCache + __experimental_resourceCache

```tsx
import { ClerkProvider } from '@clerk/clerk-expo'
import { tokenCache } from '@clerk/clerk-expo/token-cache'
import { resourceCache } from '@clerk/clerk-expo/resource-cache'
import { Slot } from 'expo-router'

export default function RootLayout() {
  return (
    <ClerkProvider
      tokenCache={tokenCache}
      __experimental_resourceCache={resourceCache}
    >
      <Slot />
    </ClerkProvider>
  )
}
```

Notes:
- Requires `expo-secure-store`.
- Treat as experimental: test thoroughly and watch Clerk changelogs.

## Handle network errors in custom flows

When offline, calls like `signIn.create()` can throw a Clerk runtime error with `code === 'network_error'`.

```tsx
import { useSignIn, isClerkRuntimeError } from '@clerk/clerk-expo'

try {
  await signIn.create({ identifier, password })
} catch (err) {
  if (isClerkRuntimeError(err) && err.code === 'network_error') {
    // Show “You appear to be offline” UI
  }
  // Log / show other errors
}
```
