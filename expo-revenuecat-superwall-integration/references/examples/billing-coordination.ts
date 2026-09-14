/** One shared queue for RevenueCat identity changes and store operations. */
export type BillingIdentity = Readonly<{ ready: boolean; revision: number }>;

export class BillingCoordinator {
  private tail: Promise<void> = Promise.resolve();
  private identityTransitions = 0;
  private storePending = false;

  private serial<T>(work: () => Promise<T>): Promise<T> {
    const result = this.tail.then(work);
    // A failed operation must not poison subsequent recovery or identity changes.
    this.tail = result.then(() => undefined, () => undefined);
    return result;
  }

  private matches(readIdentity: () => BillingIdentity, revision: number): boolean {
    const current = readIdentity();
    return current.ready && Number.isSafeInteger(current.revision) && current.revision === revision;
  }

  synchronizeIdentity<T>(work: () => Promise<T>): Promise<T> {
    // Close admission immediately, even before the queued native transition starts.
    this.identityTransitions += 1;
    return this.serial(async () => {
      try { return await work(); }
      finally { this.identityTransitions -= 1; }
    });
  }

  runStoreOperation<T>(readIdentity: () => BillingIdentity, work: (revision: number) => Promise<T>): Promise<T> {
    const accepted = readIdentity();
    if (!accepted.ready || !Number.isSafeInteger(accepted.revision) || this.identityTransitions || this.storePending) {
      return Promise.reject(new Error('Billing identity is unavailable or another operation is pending'));
    }
    // Copy the revision; never retain a mutable caller-owned snapshot object.
    const revision = accepted.revision;
    this.storePending = true;
    return this.serial(async () => {
      try {
        if (this.identityTransitions || !this.matches(readIdentity, revision)) {
          throw new Error('Billing identity changed before the store operation started');
        }
        // Once started, keep the native identity stable until settlement. A UI auth
        // change must not cancel this lock or reclassify a completed charge as failed.
        return await work(revision);
      } finally { this.storePending = false; }
    });
  }

  publishForIdentity(readIdentity: () => BillingIdentity, revision: number,
    work: () => Promise<void>): Promise<void> {
    return this.serial(async () => {
      if (this.identityTransitions || !this.matches(readIdentity, revision)) return;
      await work();
    });
  }
}

// All examples in this integration import this instance. Do not create a separate
// coordinator for auth, purchase, restore, or subscription-status publishing.
export const billingCoordinator = new BillingCoordinator();
