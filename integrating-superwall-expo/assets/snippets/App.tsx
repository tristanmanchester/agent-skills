// App.tsx (snippet) — Superwall root wiring with loading/error gates
import React from "react";
import {
  SuperwallProvider,
  SuperwallLoading,
  SuperwallLoaded,
  SuperwallError,
} from "expo-superwall";
import { ActivityIndicator, Text, View } from "react-native";

export default function App() {
  return (
    <SuperwallProvider
      apiKeys={{
        ios: process.env.EXPO_PUBLIC_SUPERWALL_IOS_KEY!,
        android: process.env.EXPO_PUBLIC_SUPERWALL_ANDROID_KEY!,
      }}
      onConfigurationError={(error) => {
        console.error("Superwall configuration failed:", error);
      }}
    >
      <SuperwallLoading>
        <ActivityIndicator style={{ flex: 1 }} />
      </SuperwallLoading>

      <SuperwallError>
        {(error) => (
          <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
            <Text>Failed to initialise Superwall</Text>
            <Text>{error}</Text>
          </View>
        )}
      </SuperwallError>

      <SuperwallLoaded>
        {/* Your normal app routes/components */}
        <RootNavigator />
      </SuperwallLoaded>
    </SuperwallProvider>
  );
}

// Replace with your app root
function RootNavigator() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text>Superwall is ready ✅</Text>
    </View>
  );
}
