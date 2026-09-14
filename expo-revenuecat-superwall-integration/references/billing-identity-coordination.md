# Identity and transaction ownership

Use the same `billingCoordinator` instance from `examples/billing-coordination.ts`
for auth synchronisation, purchase, restore, and subscription-status publishing.
A separate auth-only queue does not protect a store transaction. Never call native
`logIn`/`logOut`, purchase, or restore outside this owner in the same integration.

Update the app's desired user and `identityRevision` together. Set
`billingIdentityReady` only when the revision acknowledged by `AuthIdentitySync`
equals that desired revision, and pass the revision to `MonetizationProviders`
as `billingIdentityRevision`. This bool/revision pair is also the app's premium
feature gate; the local queue does not authorise backend access.

The queue rejects admission while identity changes or another store operation are
pending, rechecks identity before queued work starts, and holds native identity
stable through the entire product lookup and transaction. Identity transitions
wait for settlement. Already-started purchases are not cancelled when UI auth
changes, and a completed payment is not relabelled as failed: fulfilment belongs
to the captured identity, while the new UI remains gated until resynchronised.
An SDK promise that never settles keeps the queue blocked. Do not release it with
a timeout race; reconcile the store outcome first. A pending-payment SDK result
is not final entitlement fulfilment; retain the application's transaction identity
and reconcile later provider events with the documented store/RevenueCat contract.

Subscription-status updates use the same queue and revision check. A callback
from an unmounted/superseded listener cannot overwrite a new identity's status.
One mounted configuration/auth owner is still required; these examples are not
an authentication framework, a cross-process lock, or a durable transaction log.

Tests in `tests/billing-coordination.test.cjs` exercise deterministic deferred
operations and compile the pure module with strict TypeScript. They do not replace
native purchase/restore testing in the application's real SDK and store sandbox.
