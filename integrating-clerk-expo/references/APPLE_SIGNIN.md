# Sign in with Apple (Expo) — useSignInWithApple()

## Requirements

- iOS only.
- Requires a **native build** (won’t work in Expo Go).
- You must add native Sign in with Apple support for Expo (including `expo-apple-authentication`).

## Hook API

`useSignInWithApple()` returns `startAppleAuthenticationFlow(params?)`.

Returned value includes:
- `createdSessionId` (string | null)
- `setActive(params)` (to activate session)
- optional `signIn` / `signUp` resources (for remaining requirements)

## Minimal button component

```tsx
import { useSignInWithApple } from '@clerk/clerk-expo'
import { useRouter } from 'expo-router'
import { Alert, Platform, TouchableOpacity, Text } from 'react-native'

export function AppleSignInButton() {
  const { startAppleAuthenticationFlow } = useSignInWithApple()
  const router = useRouter()

  if (Platform.OS !== 'ios') return null

  const onPress = async () => {
    try {
      const { createdSessionId, setActive } = await startAppleAuthenticationFlow()
      if (createdSessionId && setActive) {
        await setActive({ session: createdSessionId })
        router.replace('/')
      }
    } catch (err: any) {
      // User cancelled the system prompt
      if (err.code === 'ERR_REQUEST_CANCELED') return
      Alert.alert('Apple Sign-In failed', err.message ?? 'Unknown error')
    }
  }

  return (
    <TouchableOpacity onPress={onPress}>
      <Text>Sign in with Apple</Text>
    </TouchableOpacity>
  )
}
```

## Unsafe metadata during sign-up

You can pass `unsafeMetadata` to `startAppleAuthenticationFlow({ unsafeMetadata: ... })`.
It’s copied to the created user’s `User.unsafeMetadata` after completion.

## Error handling must-dos

- Always wrap `startAppleAuthenticationFlow()` in `try/catch`.
- Handle `ERR_REQUEST_CANCELED` separately (don’t show an error UI).
- If you see “missing package” errors, ensure `expo-apple-authentication` is installed and you’re on a native build.
