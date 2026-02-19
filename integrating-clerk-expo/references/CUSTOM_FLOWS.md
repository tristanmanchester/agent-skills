# Custom auth flows for Expo native (no prebuilt UI)

Expo native apps require you to build your own UI using Clerk hooks/resources.

## Core rules

- Always check `isLoaded` before calling Clerk resource methods.
- Expo native does **not** support email links → prefer `email_code` verification.
- Treat Clerk resource status as a state machine; branch on `status`.

---

## Email + password sign-up with email code verification

High-level state machine:

1) Collect `emailAddress` + `password`
2) `signUp.create({ emailAddress, password })`
3) `signUp.prepareEmailAddressVerification({ strategy: 'email_code' })`
4) Collect code input
5) `signUp.attemptEmailAddressVerification({ code })`
6) If `status === 'complete'`, call `setActive({ session: createdSessionId })`
7) If `session.currentTask` exists, route to a “tasks” screen

Minimal skeleton:

```tsx
import * as React from 'react'
import { useSignUp } from '@clerk/clerk-expo'

export function SignUpScreen() {
  const { isLoaded, signUp, setActive } = useSignUp()

  const [emailAddress, setEmailAddress] = React.useState('')
  const [password, setPassword] = React.useState('')
  const [code, setCode] = React.useState('')
  const [pendingVerification, setPendingVerification] = React.useState(false)

  const onSignUpPress = async () => {
    if (!isLoaded) return
    await signUp.create({ emailAddress, password })
    await signUp.prepareEmailAddressVerification({ strategy: 'email_code' })
    setPendingVerification(true)
  }

  const onVerifyPress = async () => {
    if (!isLoaded) return
    const attempt = await signUp.attemptEmailAddressVerification({ code })
    if (attempt.status === 'complete') {
      await setActive({ session: attempt.createdSessionId })
    }
  }

  // render based on pendingVerification...
}
```

---

## Email + password sign-in

High-level flow:

1) `signIn.create({ identifier, password })`
2) If `status === 'complete'`, call `setActive({ session: createdSessionId })`
3) Otherwise, branch based on `status`:
   - `needs_first_factor`
   - `needs_second_factor`
   - `needs_identifier`
   - etc

Minimal skeleton:

```tsx
import * as React from 'react'
import { useSignIn } from '@clerk/clerk-expo'

export function SignInScreen() {
  const { isLoaded, signIn, setActive } = useSignIn()
  const [identifier, setIdentifier] = React.useState('')
  const [password, setPassword] = React.useState('')

  const onSignInPress = async () => {
    if (!isLoaded) return
    const attempt = await signIn.create({ identifier, password })
    if (attempt.status === 'complete') {
      await setActive({ session: attempt.createdSessionId })
    } else {
      // handle MFA / other requirements based on attempt.status
    }
  }
}
```

---

## Sign out

Use `useClerk()`:

```tsx
import { useClerk } from '@clerk/clerk-expo'

export function SignOutButton() {
  const { signOut } = useClerk()
  return <Button title="Sign out" onPress={() => signOut()} />
}
```

---

## Error handling

- Wrap resource calls in `try/catch`.
- Prefer displaying Clerk errors to the user (mapped to form fields).
- For offline support, specifically detect `network_error` (see `references/OFFLINE_SUPPORT.md`).

---

## Session tasks

Some sign-in/up flows may require **session tasks** after authentication. When you call `setActive()`, you can provide a `navigate` callback and route users to a custom “tasks” UI if `session.currentTask` exists.

See `references/SSO_OAUTH.md` for a concrete `setActive({ navigate })` pattern.
