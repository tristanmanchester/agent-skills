# OAuth + Enterprise SSO in Expo (useSSO)

## Prefer useSSO (useOAuth is deprecated)

If you see older code using `useOAuth()`, migrate to `useSSO()`.

## Required Expo packages (typical)

- `expo-auth-session`
- `expo-web-browser`

## Universal setup: complete pending sessions and warm up Android browser

Put this in a module that is imported by the sign-in screen, or in the screen file itself:

```tsx
import { Platform } from 'react-native'
import * as WebBrowser from 'expo-web-browser'
import { useEffect } from 'react'

// Handle any pending authentication sessions
WebBrowser.maybeCompleteAuthSession()

export const useWarmUpBrowser = () => {
  useEffect(() => {
    if (Platform.OS !== 'android') return
    void WebBrowser.warmUpAsync()
    return () => {
      void WebBrowser.coolDownAsync()
    }
  }, [])
}
```

## OAuth connection example (e.g. Google)

```tsx
import { useSSO } from '@clerk/clerk-expo'
import * as AuthSession from 'expo-auth-session'
import { useRouter } from 'expo-router'
import { useCallback } from 'react'

export function GoogleButton() {
  const router = useRouter()
  const { startSSOFlow } = useSSO()

  const onPress = useCallback(async () => {
    const { createdSessionId, setActive, signIn, signUp } = await startSSOFlow({
      strategy: 'oauth_google',
      // On native you must pass a redirectUrl (scheme-based).
      redirectUrl: AuthSession.makeRedirectUri(),
    })

    if (createdSessionId) {
      await setActive?.({
        session: createdSessionId,
        navigate: async ({ session }) => {
          if (session?.currentTask) {
            router.push('/sign-in/tasks')
            return
          }
          router.push('/')
        },
      })
    } else {
      // Missing requirements (e.g. MFA) — use signIn/signUp returned from startSSOFlow
      // and branch on their status.
    }
  }, [])

  return <Pressable onPress={onPress}><Text>Continue with Google</Text></Pressable>
}
```

Notes:
- `startSSOFlow()` can return `signIn` or `signUp` objects when requirements remain (MFA, missing fields).
- Centralise this into a reusable helper if you support multiple providers.

## Enterprise SSO example

Same pattern, but pass:
- `strategy: 'enterprise_sso'`
- `identifier: userEmail` (the email the user typed)

## Production allowlisting + redirect URLs

In production, Clerk requires allowlisted redirect URLs for mobile SSO completion.

- Acquire a domain for the production Clerk instance (required even for Expo apps).
- Allowlist your mobile SSO redirect URLs in Clerk Dashboard (Native applications).
- Clerk’s default redirect URL is typically `{bundleIdentifier}://callback`.

See: `references/DEPLOYMENT.md`.
