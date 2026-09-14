import { Text, View } from 'react-native';
import { SafeAreaProvider, SafeAreaView } from 'react-native-safe-area-context';
import { MonetizationProviders } from './monetization.shared';

/** Guest-only demonstration. Authenticated apps must wire identity revision gating. */
export default function App() {
  return (
    <SafeAreaProvider>
      <MonetizationProviders>
        <SafeAreaView style={{ flex: 1 }}>
          <View style={{ padding: 24 }}><Text>Replace with the actual navigator.</Text></View>
        </SafeAreaView>
      </MonetizationProviders>
    </SafeAreaProvider>
  );
}
