import { useEffect } from 'react';
import Purchases from 'react-native-purchases';
import { useUser } from 'expo-superwall';

import { billingCoordinator } from './billing-coordination';

type Props = {
  isAuthResolved: boolean;
  userId: string | null;
  allowAnonymousState: boolean;
  identityRevision: number;
  onSynchronized: (revision: number, ready: boolean) => void;
};

/**
 * Mount inside loaded providers, after RevenueCat configuration.
 * Increment identityRevision in the same auth-state update that changes userId.
 * Gate purchases/features until the acknowledged revision equals the current one.
 * Keep onSynchronized stable. Auth and store operations share billingCoordinator:
 * native identity changes wait for a running purchase/restore to settle. UI auth
 * may change earlier, but keep premium actions gated until the new revision is ready.
 * Effect cleanup never cancels an in-flight store transaction or releases its lock.
 */
export function AuthIdentitySync({ isAuthResolved, userId, allowAnonymousState,
  identityRevision, onSynchronized }: Props) {
  const { identify, signOut, setSubscriptionStatus } = useUser();
  useEffect(() => {
    let cancelled = false;
    onSynchronized(identityRevision, false);
    if (!isAuthResolved) return;
    void billingCoordinator.synchronizeIdentity(async () => {
      if (cancelled) return;
      if (userId) {
        await Purchases.logIn(userId);
        if (cancelled) return;
        await identify(userId);
      } else {
        if (allowAnonymousState && !(await Purchases.isAnonymous())) await Purchases.logOut();
        if (cancelled) return;
        await signOut();
        if (!allowAnonymousState) {
          if (!cancelled) onSynchronized(identityRevision, false);
          return; // Never expose the previous user's cached entitlement while signed out.
        }
      }
      if (cancelled) return;
      const info = await Purchases.getCustomerInfo();
      if (cancelled) return;
      const ids = Object.keys(info.entitlements.active);
      await setSubscriptionStatus({ status: ids.length ? 'ACTIVE' : 'INACTIVE',
        entitlements: ids.map((id) => ({ id, type: 'SERVICE_LEVEL' as const })) });
      if (!cancelled) onSynchronized(identityRevision, true);
    }).catch(() => {
      if (!cancelled) onSynchronized(identityRevision, false);
      console.warn('Billing identity could not be synchronised; keep billing gated');
    });
    return () => { cancelled = true; };
  }, [isAuthResolved, userId, allowAnonymousState, identityRevision, identify, signOut, setSubscriptionStatus, onSynchronized]);
  return null;
}
