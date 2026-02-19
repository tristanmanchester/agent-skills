# Deep links, paywall previews, and `deepLink_open`

## What you get
- Preview paywalls from the dashboard on-device (QR code viewer)
- Trigger paywalls from URLs without hardcoding routing logic
- Support web checkout return flows (iOS universal links)

## 1) Deep link setup (app side)

### Custom URL scheme
Superwall uses a custom URL scheme for paywall previews and some deep-link flows.

You can configure this in a few ways depending on your Expo workflow:

- **Expo config (preferred for managed/prebuild):** set `"scheme"` in `app.json` and rebuild your dev client.
- **Native iOS project:** add a URL type in Xcode (`Info` → `URL Types`) with your scheme.
- **Native Android project:** add an `intent-filter` for your scheme.

Keep your scheme stable (e.g. `myapp`) and rebuild after changing it.

### Wire incoming URLs to Superwall
To let Superwall drive paywall presentation via the standard placement `deepLink_open`, forward every incoming deep link URL to Superwall’s handler.

Docs show:

```ts
function handleUrl(url: string) {
  SuperwallExpoModule.handleDeepLink(url);
}
```

Implementation notes:
- The exact import path can vary by SDK version. Search your project / SDK exports for `handleDeepLink` / `SuperwallExpoModule`.
- If you can’t access the module directly, fall back to “manual routing” by parsing the URL and calling `registerPlacement("deepLink_open", params)` yourself — but you lose Superwall’s built-in URL-to-params mapping.

### Expo Linking example (practical wiring)
```ts
import * as Linking from "expo-linking";
import { useEffect } from "react";

export function DeepLinkBridge() {
  useEffect(() => {
    const sub = Linking.addEventListener("url", ({ url }) => {
      // Forward to Superwall deep-link handler
      // SuperwallExpoModule.handleDeepLink(url);
    });

    // Handle cold start link
    Linking.getInitialURL().then((url) => {
      if (url) {
        // SuperwallExpoModule.handleDeepLink(url);
      }
    });

    return () => sub.remove();
  }, []);

  return null;
}
```

## 2) Campaign-driven paywalls from deep links
Instead of hardcoding:

- `/promo` -> `"promoPlacement"`
- `/upgrade` -> `"upgradePlacement"`

…send the URL to `handleDeepLink`. Superwall fires the standard placement `deepLink_open` and exposes URL components (path, query params, host, etc.) to dashboard audience filters.

Example dashboard rule for `myapp://promo?offer=summer`:
- `params.path` is `promo`
- `params.offer` is `summer`

This lets you add/change routes and paywalls in the dashboard with no app update.

## 3) Previewing paywalls from the dashboard
Once your scheme is configured:
1. In the dashboard: Settings → General → set your **Apple Custom URL Scheme** (without slashes).
2. Open a paywall in the dashboard and click **Preview**.
3. Scan the QR code on device to open the paywall viewer inside your app.

## 4) Web checkout (iOS universal link)
If you use Superwall web checkout, add **Associated Domains** in Xcode and set:

`applinks:[your-web-checkout-url]`

Testing tips:
- Branch has an online validator you can use against your web checkout domain.
- Test a link formatted as `https://[your-web-checkout-link]/app-link/` by tapping it on device.

## Sources
- Deep link setup + previews: https://superwall.com/docs/expo/quickstart/in-app-paywall-previews
- Deep link paywalls via handleDeepLink: https://superwall.com/docs/expo/guides/handling-deep-links
- Web checkout overview: https://superwall.com/docs/expo/guides/web-checkout
