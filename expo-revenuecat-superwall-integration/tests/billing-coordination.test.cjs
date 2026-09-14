const { test, after } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, rmSync, readFileSync } = require('node:fs');
const { tmpdir } = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const out = mkdtempSync(path.join(tmpdir(), 'billing-coordination-'));
const examples = path.join(__dirname, '../references/examples');
execFileSync('tsc', [path.join(examples, 'billing-coordination.ts'), '--strict', '--target', 'ES2020', '--module', 'commonjs', '--outDir', out]);
const { BillingCoordinator } = require(path.join(out, 'billing-coordination.js'));
after(() => rmSync(out, { recursive: true, force: true }));
const deferred = () => {
  let resolve, reject;
  const promise = new Promise((yes, no) => { resolve = yes; reject = no; });
  return { promise, resolve, reject };
};
const tick = () => new Promise(resolve => setImmediate(resolve));

test('identity change waits for an already-started purchase and preserves its outcome', async () => {
  const c = new BillingCoordinator(), gate = deferred(), started = deferred();
  let identity = { ready: true, revision: 1 }, native = 'A';
  const events = [];
  const purchase = c.runStoreOperation(() => identity, async revision => {
    started.resolve(); await gate.promise;
    events.push(`paid:${native}:${revision}`); return 'purchased';
  });
  await started.promise;
  identity = { ready: false, revision: 2 };
  const change = c.synchronizeIdentity(async () => { native = 'B'; events.push('login:B'); identity = { ready: true, revision: 2 }; });
  await tick(); assert.equal(native, 'A'); assert.deepEqual(events, []);
  gate.resolve(); assert.equal(await purchase, 'purchased'); await change;
  assert.deepEqual(events, ['paid:A:1', 'login:B']);
});
test('queued purchase rechecks the accepted revision before any provider call', async () => {
  const c = new BillingCoordinator(), gate = deferred(), started = deferred();
  let identity = { ready: true, revision: 1 }, called = false;
  const publishing = c.publishForIdentity(() => identity, 1, async () => { started.resolve(); await gate.promise; });
  await started.promise;
  const purchase = c.runStoreOperation(() => identity, async () => { called = true; });
  const rejected = assert.rejects(purchase, /identity changed/);
  identity = { ready: true, revision: 2 }; gate.resolve(); await publishing; await rejected;
  assert.equal(called, false);
});
test('pending identity transition blocks admission even before React updates readiness', async () => {
  const c = new BillingCoordinator(), gate = deferred();
  const change = c.synchronizeIdentity(() => gate.promise);
  await assert.rejects(c.runStoreOperation(() => ({ ready: true, revision: 1 }), async () => {}), /unavailable/);
  gate.resolve(); await change;
});
test('restore shares the same lock and concurrent duplicate store requests are rejected', async () => {
  const c = new BillingCoordinator(), gate = deferred(), started = deferred(), read = () => ({ ready: true, revision: 1 });
  const restore = c.runStoreOperation(read, async () => { started.resolve(); await gate.promise; return 'restored'; });
  await started.promise;
  await assert.rejects(c.runStoreOperation(read, async () => 'duplicate'), /pending/);
  let loggedOut = false;
  const change = c.synchronizeIdentity(async () => { loggedOut = true; });
  await tick(); assert.equal(loggedOut, false); gate.resolve(); assert.equal(await restore, 'restored');
  await change; assert.equal(loggedOut, true);
});
test('failed work releases the queue without converting a failure into success', async () => {
  const c = new BillingCoordinator(), read = () => ({ ready: true, revision: 1 });
  await assert.rejects(c.runStoreOperation(read, async () => { throw Error('store failed'); }), /store failed/);
  await assert.rejects(c.synchronizeIdentity(async () => { throw Error('login failed'); }), /login failed/);
  await c.synchronizeIdentity(async () => {});
  assert.equal(await c.runStoreOperation(read, async () => 'next'), 'next');
});
test('stale status publication cannot run across a queued identity transition', async () => {
  const c = new BillingCoordinator(), gate = deferred(), started = deferred();
  let identity = { ready: true, revision: 1 }, published = false;
  const store = c.runStoreOperation(() => identity, async () => { started.resolve(); await gate.promise; });
  await started.promise;
  const oldStatus = c.publishForIdentity(() => identity, 1, async () => { published = true; });
  identity = { ready: false, revision: 2 };
  const change = c.synchronizeIdentity(async () => { identity = { ready: true, revision: 2 }; });
  gate.resolve(); await Promise.all([store, oldStatus, change]); assert.equal(published, false);
});
test('mutable snapshot references cannot change an admitted operation revision', async () => {
  const c = new BillingCoordinator(), gate = deferred(), started = deferred();
  const identity = { ready: true, revision: 1 };
  const publication = c.publishForIdentity(() => identity, 1, async () => { started.resolve(); await gate.promise; });
  await started.promise;
  let called = false;
  const store = c.runStoreOperation(() => identity, async () => { called = true; });
  const rejected = assert.rejects(store, /identity changed/); identity.revision = 2;
  gate.resolve(); await publication; await rejected; assert.equal(called, false);
});
test('actual auth and store examples import the same owner', () => {
  const auth = readFileSync(path.join(examples, 'auth-sync.example.tsx'), 'utf8');
  const store = readFileSync(path.join(examples, 'monetization.shared.tsx'), 'utf8');
  assert.ok(auth.includes("from './billing-coordination'"));
  assert.ok(store.includes("from './billing-coordination'"));
  assert.ok(auth.includes('billingCoordinator.synchronizeIdentity'));
  assert.equal((store.match(/billingCoordinator.runStoreOperation/g) || []).length, 2);
  assert.ok(store.includes('billingCoordinator.publishForIdentity'));
  assert.ok(!auth.includes('identityQueue'));
});
