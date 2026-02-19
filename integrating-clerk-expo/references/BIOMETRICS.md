# Biometrics / local credentials (useLocalCredentials)

`useLocalCredentials()` lets you store a user’s **password credentials** on-device and later sign them in using biometrics (Face ID / fingerprint).

## Constraints

- Native only (not supported on web).
- Requires `@clerk/clerk-expo >= 2.2.0`.
- Works only for **password** sign-in attempts.
- Credentials are removed if the device passcode is removed.

## Returned fields/methods (high level)

- `hasCredentials: boolean` — any credentials stored?
- `userOwnsCredentials: boolean` — do stored creds belong to the signed-in user?
- `biometricType: 'face-recognition' | 'fingerprint' | null`
- `setCredentials({ identifier?, password })`
- `clearCredentials()`
- `authenticate()` — reads stored creds and starts a password sign-in attempt (returns SignInResource)

## Suggested UX pattern

### After a successful password sign-in
Offer a “Enable Face ID / Touch ID” toggle:

```tsx
import { useLocalCredentials } from '@clerk/clerk-expo'

const { setCredentials } = useLocalCredentials()

await setCredentials({ identifier: email, password })
```

### On the next app launch (signed out)
Show a “Sign in with Face ID” button if `hasCredentials` is true:

```tsx
import { useLocalCredentials } from '@clerk/clerk-expo'
import { useSignIn } from '@clerk/clerk-expo'

const { authenticate, hasCredentials } = useLocalCredentials()
const { setActive } = useSignIn()

const onBiometricPress = async () => {
  const signInAttempt = await authenticate()
  if (signInAttempt.status === 'complete') {
    await setActive({ session: signInAttempt.createdSessionId })
  } else {
    // handle other states (MFA etc)
  }
}
```

### Signing out
If you want to remove local creds on sign-out, call `clearCredentials()` explicitly (this is an app decision).
