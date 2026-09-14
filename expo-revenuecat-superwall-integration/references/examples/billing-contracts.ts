/** Pure contracts: no SDK, React, store calls, or compatibility fallbacks. */
export function selectPlayOption<T extends { id: string; productId: string }>(
  options: readonly T[], productId: string, basePlanId: string, offerId?: string,
): T {
  if (!productId || !basePlanId || (offerId !== undefined && !offerId)) {
    throw new Error('An explicit product and base plan, with a non-empty offer when supplied, are required');
  }
  const id = offerId === undefined ? basePlanId : `${basePlanId}:${offerId}`;
  const matches = options.filter((option) => option.productId === productId && option.id === id);
  if (matches.length !== 1) {
    throw new Error('Selected Google Play option is unavailable or ambiguous; refresh the paywall, do not substitute a price');
  }
  return matches[0];
}

export type CustomerInfoSource<T> = {
  addCustomerInfoUpdateListener(listener: (info: T) => void): void;
  removeCustomerInfoUpdateListener(listener: (info: T) => void): boolean;
  getCustomerInfo(): Promise<T>;
};

/** Register first; an old initial response must not replace a newer event. */
export function subscribeCustomerInfo<T>(
  source: CustomerInfoSource<T>, onInfo: (info: T) => void, onError: (error: unknown) => void,
): () => void {
  let active = true;
  let receivedEvent = false;
  const deliver = (info: T) => {
    if (!active) return;
    try { onInfo(info); } catch (error) { onError(error); }
  };
  const listener = (info: T) => { receivedEvent = true; deliver(info); };
  source.addCustomerInfoUpdateListener(listener);
  void Promise.resolve().then(() => source.getCustomerInfo()).then((info) => {
    if (!receivedEvent) deliver(info);
  }).catch((error: unknown) => { if (active) onError(error); });
  return () => {
    if (!active) return;
    active = false;
    source.removeCustomerInfoUpdateListener(listener);
  };
}
