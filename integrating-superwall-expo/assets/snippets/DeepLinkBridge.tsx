// DeepLinkBridge.tsx (snippet) — forward incoming URLs to Superwall
import * as Linking from "expo-linking";
import { useEffect } from "react";

// Note: depending on your SDK version, you may need to import a handler.
// Docs show: SuperwallExpoModule.handleDeepLink(url)
// Confirm the correct export in your project before wiring.
export function DeepLinkBridge() {
  useEffect(() => {
    const sub = Linking.addEventListener("url", ({ url }) => {
      console.log("Incoming URL:", url);
      // SuperwallExpoModule.handleDeepLink(url);
    });

    Linking.getInitialURL().then((url) => {
      if (url) {
        console.log("Initial URL:", url);
        // SuperwallExpoModule.handleDeepLink(url);
      }
    });

    return () => sub.remove();
  }, []);

  return null;
}
