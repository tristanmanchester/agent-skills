import { useEffect, useMemo, useRef, useState, type ComponentProps, type ReactNode } from 'react';
import { ActivityIndicator, Platform, Text } from 'react-native';
import Purchases, { PRODUCT_CATEGORY, PURCHASES_ERROR_CODE, type CustomerInfo } from 'react-native-purchases';
import { CustomPurchaseControllerProvider, SuperwallLoaded, SuperwallLoading, SuperwallProvider, useUser } from 'expo-superwall';
import { subscribeCustomerInfo } from './billing-contracts';
import { billingCoordinator, type BillingIdentity } from './billing-coordination';
import { purchaseFromSuperwallParams } from './custom-purchase-controller.android-offers';

const revenueCatApiKeys = {
  ios: process.env.EXPO_PUBLIC_REVENUECAT_IOS_API_KEY ?? '',
  android: process.env.EXPO_PUBLIC_REVENUECAT_ANDROID_API_KEY ?? '',
};
const superwallApiKeys = {
  ios: process.env.EXPO_PUBLIC_SUPERWALL_IOS_API_KEY ?? '',
  android: process.env.EXPO_PUBLIC_SUPERWALL_ANDROID_API_KEY ?? '',
};
let configuration: Promise<void> | undefined;

function configureOnce(initialAppUserId?: string) {
  if (!configuration) {
    configuration = (async () => {
      if (Platform.OS !== 'ios' && Platform.OS !== 'android') throw new Error('Native billing requires iOS or Android');
      const apiKey = revenueCatApiKeys[Platform.OS];
      if (!apiKey || !superwallApiKeys[Platform.OS]) throw new Error('Missing platform public SDK keys');
      // This example owns configuration. In an existing app, reuse its single owner.
      if (!(await Purchases.isConfigured())) {
        Purchases.configure({ apiKey, ...(initialAppUserId ? { appUserID: initialAppUserId } : {}) });
      }
      if (!(await Purchases.isConfigured())) throw new Error('RevenueCat configuration did not complete');
    })();
  }
  return configuration;
}

function errorCode(error: unknown): unknown {
  return error !== null && typeof error === 'object' && 'code' in error ? error.code : undefined;
}

function SubscriptionSync({ readIdentity }: { readIdentity: () => BillingIdentity }) {
  const { setSubscriptionStatus } = useUser();
  useEffect(() => {
    let active = true;
    const revision = readIdentity().revision;
    const onInfo = (info: CustomerInfo) => {
      void billingCoordinator.publishForIdentity(readIdentity, revision, async () => {
        if (!active) return;
        const ids = Object.keys(info.entitlements.active);
        await setSubscriptionStatus({
          status: ids.length ? 'ACTIVE' : 'INACTIVE',
          entitlements: ids.map((id) => ({ id, type: 'SERVICE_LEVEL' as const })),
        });
      }).catch(() => { if (active) console.warn('Subscription status could not be synchronised'); });
    };
    const stop = subscribeCustomerInfo<CustomerInfo>(Purchases, onInfo,
      () => console.warn('Customer info unavailable; do not infer an inactive subscription'));
    return () => { active = false; stop(); };
  }, [setSubscriptionStatus, readIdentity]);
  return null;
}

type Props = {
  children: ReactNode;
  /** For login-first apps, resolve auth before mounting and provide the stable ID. */
  initialAppUserId?: string;
  /** False during auth resolution/account changes. Also gate premium actions in the app. */
  billingIdentityReady?: boolean;
  /** Update with auth state; must match AuthIdentitySync's acknowledged revision. */
  billingIdentityRevision?: number;
};

export function MonetizationProviders({ children, initialAppUserId, billingIdentityReady = true, billingIdentityRevision = 0 }: Props) {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState(false);
  const identity = useRef<BillingIdentity>({ ready: billingIdentityReady, revision: billingIdentityRevision });
  identity.current = { ready: billingIdentityReady, revision: billingIdentityRevision };
  const readIdentity = useMemo(() => () => identity.current, []);

  useEffect(() => {
    let active = true;
    void configureOnce(initialAppUserId).then(() => { if (active) setReady(true); })
      .catch(() => { if (active) setError(true); });
    return () => { active = false; };
  }, [initialAppUserId]);

  const controller = useMemo<ComponentProps<typeof CustomPurchaseControllerProvider>['controller']>(() => ({
    onPurchase: async (params) => {
      if (!readIdentity().ready) return { type: 'failed', error: 'Billing identity is not ready' };
      try {
        await billingCoordinator.runStoreOperation(readIdentity, async () => {
          if (params.platform === 'ios' && params.store && params.store !== 'APP_STORE') {
            throw new Error('This example handles native App Store products only');
          }
          if (params.platform === 'android' && params.basePlanId) {
            await purchaseFromSuperwallParams({ productId: params.productId, basePlanId: params.basePlanId, offerId: params.offerId ?? undefined });
          } else {
            if (params.platform === 'android' && params.offerId) throw new Error('Offer requires a base plan');
            const [subscriptions, oneTimeProducts] = await Promise.all([
              Purchases.getProducts([params.productId], PRODUCT_CATEGORY.SUBSCRIPTION),
              params.platform === 'android'
                ? Purchases.getProducts([params.productId], PRODUCT_CATEGORY.NON_SUBSCRIPTION)
                : Promise.resolve([]),
            ]);
            if (params.platform === 'android' && subscriptions.length) {
              throw new Error('Android subscription purchase requires an explicit base plan');
            }
            const matches = [...subscriptions, ...oneTimeProducts].filter((product) => product.identifier === params.productId);
            if (matches.length !== 1) throw new Error('Requested store product is unavailable or ambiguous');
            await Purchases.purchaseStoreProduct(matches[0]);
          }
        });
        // A completed payment and feature entitlement are separate outcomes.
        // The premium gate checks the specific entitlement; never repurchase to fix fulfilment.
        return { type: 'purchased' };
      } catch (error) {
        const code = errorCode(error);
        if (code === PURCHASES_ERROR_CODE.PURCHASE_CANCELLED_ERROR) return { type: 'cancelled' };
        if (code === PURCHASES_ERROR_CODE.PAYMENT_PENDING_ERROR) return { type: 'pending' };
        return { type: 'failed', error: 'Purchase could not be completed. Refresh the product or check store status before retrying.' };
      }
    },
    onPurchaseRestore: async () => {
      if (!readIdentity().ready) return { type: 'failed', error: 'Billing identity is not ready' };
      try {
        await billingCoordinator.runStoreOperation(readIdentity, () => Purchases.restorePurchases());
        // A successful restore can legitimately return no active entitlements.
        return { type: 'restored' };
      } catch {
        return { type: 'failed', error: 'Restore could not be completed' };
      }
    },
  }), [readIdentity]);

  if (error) return <Text>Billing could not be initialised. Check configuration and restart.</Text>;
  if (!ready) return <ActivityIndicator accessibilityLabel="Initialising billing" />;
  return (
    <CustomPurchaseControllerProvider controller={controller}>
      <SuperwallProvider apiKeys={superwallApiKeys} onConfigurationError={() => setError(true)}>
        <SuperwallLoading><ActivityIndicator accessibilityLabel="Loading paywalls" /></SuperwallLoading>
        <SuperwallLoaded>
          {billingIdentityReady ? <SubscriptionSync key={billingIdentityRevision} readIdentity={readIdentity} /> : null}
          {children}
        </SuperwallLoaded>
      </SuperwallProvider>
    </CustomPurchaseControllerProvider>
  );
}
