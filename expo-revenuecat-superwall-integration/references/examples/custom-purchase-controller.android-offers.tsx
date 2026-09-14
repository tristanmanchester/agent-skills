import Purchases, { PRODUCT_CATEGORY } from 'react-native-purchases';
import { selectPlayOption } from './billing-contracts';

/** Subscription-only path. Never substitute an unavailable paywall offer. */
export async function purchaseFromSuperwallParams({ productId, basePlanId, offerId }: {
  productId: string; basePlanId: string; offerId?: string;
}) {
  const products = await Purchases.getProducts([productId], PRODUCT_CATEGORY.SUBSCRIPTION);
  const options = products.flatMap((product) => product.subscriptionOptions ?? []);
  const option = selectPlayOption(options, productId, basePlanId, offerId);
  return Purchases.purchaseSubscriptionOption(option);
}
