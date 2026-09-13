const { test, after } = require('node:test');
const assert = require('node:assert/strict');
const { mkdtempSync, rmSync } = require('node:fs');
const { tmpdir } = require('node:os');
const path = require('node:path');
const { execFileSync } = require('node:child_process');
const out = mkdtempSync(path.join(tmpdir(), 'billing-contracts-'));
execFileSync('tsc', [path.join(__dirname, '../references/examples/billing-contracts.ts'),
  '--strict', '--target', 'ES2020', '--module', 'commonjs', '--outDir', out]);
const { selectPlayOption, subscribeCustomerInfo } = require(path.join(out, 'billing-contracts.js'));
after(() => rmSync(out, { recursive: true, force: true }));
const options = [{ productId: 'pro', id: 'monthly' }, { productId: 'pro', id: 'monthly:trial' }];
const tick = () => new Promise((resolve) => setImmediate(resolve));

test('selects the exact base plan and exact offer', () => {
  assert.equal(selectPlayOption(options, 'pro', 'monthly'), options[0]);
  assert.equal(selectPlayOption(options, 'pro', 'monthly', 'trial'), options[1]);
});
test('does not substitute default/first option for an unavailable offer', () => {
  assert.throws(() => selectPlayOption(options, 'pro', 'monthly', 'missing'));
  assert.throws(() => selectPlayOption(options, 'pro', 'yearly'));
});
test('rejects missing base plan, empty offer, other product, and ambiguous identities', () => {
  assert.throws(() => selectPlayOption(options, 'pro', '', 'trial'));
  assert.throws(() => selectPlayOption(options, 'pro', 'monthly', ''));
  assert.throws(() => selectPlayOption(options, 'other', 'monthly'));
  assert.throws(() => selectPlayOption([...options, options[0]], 'pro', 'monthly'));
});
function fixture() {
  let listener, resolve, reject;
  const removed = [], output = [], errors = [];
  const pending = new Promise((yes, no) => { resolve = yes; reject = no; });
  const source = {
    addCustomerInfoUpdateListener(fn) { listener = fn; },
    removeCustomerInfoUpdateListener(fn) { removed.push(fn); return fn === listener; },
    getCustomerInfo() { return pending; },
  };
  const stop = subscribeCustomerInfo(source, (info) => output.push(info), (error) => errors.push(error));
  return { stop, resolve, reject, event: (info) => listener(info), listener: () => listener, removed, output, errors };
}
test('seeds state without needing a listener event', async () => {
  const f = fixture(); f.resolve('initial'); await tick();
  assert.deepEqual(f.output, ['initial']); f.stop();
});
test('removes exactly the registered callback once and ignores late work', async () => {
  const f = fixture(); f.stop(); f.stop(); f.resolve('late'); f.event('late event'); await tick();
  assert.deepEqual(f.removed, [f.listener()]); assert.deepEqual(f.output, []);
});
test('a stale initial fetch cannot overwrite a newer update', async () => {
  const f = fixture(); f.event('new'); f.resolve('old'); await tick();
  assert.deepEqual(f.output, ['new']); f.stop();
});
test('reports initial-fetch failures without manufacturing inactive status', async () => {
  const f = fixture(); const error = new Error('synthetic'); f.reject(error); await tick();
  assert.deepEqual(f.errors, [error]); assert.deepEqual(f.output, []); f.stop();
});
