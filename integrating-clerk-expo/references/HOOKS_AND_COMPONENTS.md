# Hooks + components you can rely on (Expo SDK)

## Expo-specific hooks

- `useSSO()` — OAuth + enterprise SSO flows via `startSSOFlow()`.
- `useSignInWithApple()` — native Sign in with Apple on iOS (native build).
- `useLocalCredentials()` — store password creds locally and use biometrics to sign in later.

## Common hooks inherited from Clerk React SDK

These work in Expo because the Expo SDK is built on top of Clerk’s React SDK:

- `useAuth()` — auth state + `getToken()` for calling your backend
- `useUser()` — current user object (profile data, unsafe metadata, etc)
- `useClerk()` — access Clerk methods like `signOut()`
- `useSignIn()` — sign-in resource for custom sign-in flows
- `useSignUp()` — sign-up resource for custom sign-up flows
- `useSession()` / `useSessionList()` — session info
- `useOrganization()` / `useOrganizationList()` — organisations (B2B)

## Control components (native-safe)

Use these for gating render based on auth/load state:

- `<ClerkLoaded>` / `<ClerkLoading>` — render based on SDK load state
- `<SignedIn>` / `<SignedOut>` — render based on auth state
- `<Protect>` — protect a subtree that requires auth

Note: Prebuilt auth UI components (e.g. “SignIn”, “SignUp” screens) are web-only. For native, build your own screens.
