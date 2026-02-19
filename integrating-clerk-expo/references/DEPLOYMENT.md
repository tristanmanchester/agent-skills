# Deploying an Expo app with Clerk (production notes)

## 1) You still need a domain

Even if your product is “mobile-only”, Clerk production instances require a domain.

## 2) Allowlist redirect URLs for mobile SSO

Clerk ensures security-critical nonces are only passed to **allowlisted** URLs when SSO completes in native browsers/webviews. For production you should allowlist your mobile redirect URLs.

Where:
- Clerk Dashboard → **Native applications**
- Section: “Allowlist for mobile SSO redirect”

Default:
- Clerk typically uses `{bundleIdentifier}://callback` as the redirect URL.

## 3) Build and release

After domain + allowlists are configured, proceed with your normal Expo release pipeline (EAS builds / store submission).

## 4) OTA updates (recommended)

Expo over-the-air updates make it easier to ship Clerk SDK updates (security patches, behaviour changes) without resubmitting binaries.
