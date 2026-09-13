import { Platform } from 'react-native';
import Purchases, { PURCHASES_ARE_COMPLETED_BY_TYPE, STOREKIT_VERSION } from 'react-native-purchases';

/** Call exactly once from the application's existing bootstrap owner. */
export function configureRevenueCatObserver(apiKey: string, appUserID: string,
  storeKitVersion: STOREKIT_VERSION) {
  if (!apiKey || !appUserID) throw new Error('Public SDK key and resolved billing identity are required');
  if (Platform.OS !== 'ios' && Platform.OS !== 'android') throw new Error('Native example only');
  Purchases.configure({
    apiKey, appUserID,
    purchasesAreCompletedBy: {
      type: PURCHASES_ARE_COMPLETED_BY_TYPE.MY_APP,
      storeKitVersion, // Required by the shared type; ignored by native Android.
    },
  });
}

/**
 * Explicit recovery/import checkpoint, not an effect or every-launch operation.
 * Inspect the project's restore/transfer policy before importing store purchases.
 * The external purchase owner still finishes/acknowledges its own transactions.
 * Requires the modern RevenueCat API (syncPurchasesForResult, available since 9.7).
 */
export async function syncHistoricalPurchasesAtApprovedCheckpoint() {
  const { customerInfo } = await Purchases.syncPurchasesForResult();
  return customerInfo;
}
