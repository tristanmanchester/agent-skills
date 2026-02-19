# Troubleshooting / debugging

## Symptom: `Cannot find native module 'SuperwallExpo'`
### Likely causes
- Running in **Expo Go** (Superwall is a native module)
- Added `expo-superwall` after the last prebuild/dev-client build, so native code isn’t in the app
- Using Expo SDK < 53

### Fix sequence (fastest → slowest)
1. Confirm you’re using a **Development Build**:
   - local: `npx expo run:ios` / `npx expo run:android`
   - EAS: rebuild the dev client
2. Confirm Expo SDK is 53+ (check `package.json` dependency `expo`)
3. Regenerate native projects if needed:
   - `npx expo prebuild --clean`
4. Reinstall deps + pods (iOS):
   - delete `node_modules`, reinstall
   - `cd ios && pod install` (if you have an `ios/` folder)
5. Clear Metro / Expo caches:
   - `npx expo start -c`

## Symptom: paywall never shows / changes don’t appear
- Ensure the placement name matches exactly what’s in the dashboard campaign.
- Superwall doesn’t refetch config during hot reload: **fully restart the app** after dashboard edits.
- Confirm your placement is in a campaign and has a paywall attached to an audience that matches the device/user.

## Symptom: Android-specific issues
- Ensure Android `minSdkVersion` is 21+ via `expo-build-properties`.
- If you need Play Store identifiers passed through, enable `passIdentifiersToPlayStore` in options (Android only).

## Symptom: Deep link previews don’t open the viewer
- Ensure your custom scheme is configured in the app and in Superwall dashboard settings.
- Rebuild the dev client after changing URL schemes.
- Confirm your app receives the URL (log with Expo Linking) and (if applicable) forwards to Superwall deep link handler.

## Symptom: Purchases handled externally but Superwall gating is wrong
If RevenueCat/custom billing is used:
- you must **sync subscription status** into Superwall via `setSubscriptionStatus()`
- verify your entitlements IDs match what your Superwall campaigns expect

See `references/REVENUECAT.md` and `references/SUBSCRIPTION_STATUS.md`.

## Sources
- https://superwall.com/docs/expo/guides/debugging
- https://superwall.com/docs/expo/quickstart/install
