# StoreKit testing (iOS only)

## When to use
- you want to test IAP flows locally without live App Store products
- you need deterministic purchase behaviour during development

## Requirements
- Works in a **native iOS build** (dev client / `expo run:ios`).
- You need access to the generated `ios/` project (prebuild).

## Typical workflow
1. Ensure the project has an `ios/` folder:
   - `npx expo prebuild` (or `--clean` if needed)
2. Open the iOS project in Xcode.
3. Create or add a StoreKit configuration file (`.storekit`) to the project.
4. Attach the StoreKit config to the run scheme:
   - Product → Scheme → Edit Scheme… → Run → Options → StoreKit Configuration
5. Run the app from Xcode (or rebuild your dev client).

## Notes
- If your paywall products don’t resolve, confirm your StoreKit config contains the same product IDs used in Superwall.
- If you use RevenueCat, follow its StoreKit testing guidance too.

## Sources
- https://superwall.com/docs/expo/guides/storekit-testing
