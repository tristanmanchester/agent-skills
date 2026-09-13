import { useRef, useState } from 'react';
import { Button, Text, View } from 'react-native';
import Purchases from 'react-native-purchases';
import { usePlacement } from 'expo-superwall';

/** UI gating is not server authorisation. Protect server resources on the server. */
export function ExportPdfUpsell({ billingIdentityReady, identityRevision, onExport }: {
  billingIdentityReady: boolean; identityRevision: number; onExport: () => Promise<void>;
}) {
  const [message, setMessage] = useState('');
  const current = useRef({ ready: billingIdentityReady, revision: identityRevision });
  current.current = { ready: billingIdentityReady, revision: identityRevision };
  const { registerPlacement } = usePlacement({
    onError: () => setMessage('The paywall is unavailable. Please try again later.'),
  });
  const exportWhenEntitled = async (revision: number) => {
    try {
      if (!current.current.ready || current.current.revision !== revision) return;
      const info = await Purchases.getCustomerInfo();
      if (!current.current.ready || current.current.revision !== revision) return;
      if (!info.entitlements.active.pro) {
        setMessage('Pro access is not active yet. A completed purchase should be checked, not purchased again.');
        return;
      }
      await onExport();
    } catch {
      setMessage('Access or export could not be verified. No further purchase was attempted.');
    }
  };
  return (
    <View>
      <Button title="Export PDF" disabled={!billingIdentityReady} onPress={() => {
        const revision = current.current.revision;
        void registerPlacement({ placement: 'export_pdf', feature: () => { void exportWhenEntitled(revision); } })
          .catch(() => setMessage('The paywall could not be opened.'));
      }} />
      {message ? <Text accessibilityLiveRegion="polite">{message}</Text> : null}
    </View>
  );
}
