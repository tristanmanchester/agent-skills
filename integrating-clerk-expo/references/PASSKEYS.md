# Passkeys (high-level notes)

Clerk supports passkeys (built on the WebAuthn standard). Passkeys are intended as a more secure, user-friendly alternative to passwords.

## When to consider passkeys in an Expo app

- You want phishing-resistant authentication
- You already support “email + password” and want a stronger/less-friction option
- You need to reduce password resets and improve conversion

## Implementation approach

1) Enable/configure passkeys in Clerk (dashboard + instance settings).
2) Update your custom sign-in/sign-up flow to offer passkey registration and sign-in where supported.
3) Treat passkeys as a factor that may interact with other requirements (e.g. MFA/session tasks).
4) Ensure your testing matrix covers:
   - iOS vs Android devices
   - Expo Go vs native builds (some auth mechanisms require native builds)
   - Offline/poor connectivity behaviour

Because passkey support details can evolve quickly, always follow the latest “Configure passkeys” page in Clerk docs when implementing.
