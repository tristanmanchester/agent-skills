# Routing + protection patterns (Expo Router and React Navigation)

## Terminology

- **Control components**: `<SignedIn>`, `<SignedOut>`, `<Protect>`, `<ClerkLoaded>`, `<ClerkLoading>`
- **Imperative guard**: a layout/screen that checks `useAuth()` and redirects

Keep the app consistent: pick one main pattern and apply it everywhere.

---

## Expo Router patterns

### Pattern 1 — Gate a whole route group with a layout redirect

Example: protect everything under `app/(home)/...`:

`app/(home)/_layout.tsx`

```tsx
import { Redirect, Stack } from 'expo-router'
import { useAuth } from '@clerk/clerk-expo'

export default function HomeLayout() {
  const { isLoaded, isSignedIn } = useAuth()
  if (!isLoaded) return null // or a splash component
  if (!isSignedIn) return <Redirect href="/(auth)/sign-in" />
  return <Stack />
}
```

Pros: simple mental model; works well for “signed-in areas”.

### Pattern 2 — Declarative rendering with <SignedIn> / <SignedOut>

Example: a screen that shows different content based on auth:

```tsx
import { SignedIn, SignedOut } from '@clerk/clerk-expo'

export default function Index() {
  return (
    <>
      <SignedIn>{/* signed-in UI */}</SignedIn>
      <SignedOut>{/* signed-out UI */}</SignedOut>
    </>
  )
}
```

Pros: great for landing screens that can be “both”.

### Pattern 3 — Protect a component subtree with <Protect>

```tsx
import { Protect } from '@clerk/clerk-expo'

export function BillingSection() {
  return (
    <Protect>
      {/* content that should only render for signed-in users */}
    </Protect>
  )
}
```

Pros: convenient for “small guarded areas”.

---

## React Navigation patterns (no Expo Router)

### Pattern — AuthStack vs AppStack

```tsx
import { ClerkProvider, useAuth } from '@clerk/clerk-expo'
import { tokenCache } from '@clerk/clerk-expo/token-cache'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/native-stack'

const Stack = createNativeStackNavigator()

function RootNavigator() {
  const { isLoaded, isSignedIn } = useAuth()

  if (!isLoaded) return null // splash/loading

  return (
    <Stack.Navigator>
      {isSignedIn ? (
        <>
          <Stack.Screen name="Home" component={HomeScreen} />
          {/* other signed-in screens */}
        </>
      ) : (
        <>
          <Stack.Screen name="SignIn" component={SignInScreen} />
          <Stack.Screen name="SignUp" component={SignUpScreen} />
        </>
      )}
    </Stack.Navigator>
  )
}

export default function App() {
  return (
    <ClerkProvider tokenCache={tokenCache}>
      <NavigationContainer>
        <RootNavigator />
      </NavigationContainer>
    </ClerkProvider>
  )
}
```

Notes:
- Always wait for `isLoaded` before rendering logic that depends on Clerk.
- Keep sign-in and sign-up screens “dumb” UI; centralise navigation logic in one place.
