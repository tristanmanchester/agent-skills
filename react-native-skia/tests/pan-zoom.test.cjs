const test = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');
const { makeBounds, constrain, moveBy, zoomBetween } = require(path.resolve(process.env.SKIA_GEOMETRY_BUILD || '.test-build', 'pan-zoom-math.js'));
const centre = { x: 0, y: 0 };
const b = makeBounds(320, 220, 320, 220);
const start = { scale: 1, x: 0, y: 0 };
const close = (a, v) => assert.ok(Math.abs(a - v) < 1e-9, `${a} != ${v}`);

test('fit preserves aspect ratio without device density', () => {
  const fit = makeBounds(800, 400, 320, 220);
  assert.equal(fit.contentWidth, 320); assert.equal(fit.contentHeight, 160);
});
test('invalid dimensions and scale ranges fail before rendering', () => {
  for (const n of [0, -1, NaN, Infinity]) assert.throws(() => makeBounds(n, 100, 320, 220));
  assert.throws(() => makeBounds(100, 100, 320, 220, 2, 1));
  assert.throws(() => makeBounds(100, 100, 320, 220, 0.5, 4));
});
test('unrepresentable ranges fail', () => {
  assert.throws(() => makeBounds(1, 1, Number.MAX_VALUE, Number.MAX_VALUE, 1, 4));
});
test('unzoomed fitted content stays centred', () => {
  assert.deepEqual(moveBy(start, 100, -100, b), start);
});
test('zoom limits use the actual clamped ratio', () => {
  const r = zoomBetween({ scale: 3, x: 0, y: 0 }, 2, { x: 30, y: 20 }, { x: 30, y: 20 }, b);
  assert.equal(r.scale, 4); close(r.x, -10); close(r.y, -20 / 3);
});
test('zoom preserves the focal image point away from clamps', () => {
  const pose = { scale: 2, x: 20, y: -10 };
  const a = { x: 35, y: 20 }, z = { x: 40, y: 25 };
  const r = zoomBetween(pose, 1.25, a, z, b);
  close((a.x - pose.x) / pose.scale, (z.x - r.x) / r.scale);
  close((a.y - pose.y) / pose.scale, (z.y - r.y) / r.scale);
});
test('successive pinches accumulate without a base-scale reset', () => {
  const a = zoomBetween(start, 2, centre, centre, b);
  const c = zoomBetween(a, 1.5, centre, centre, b);
  assert.equal(c.scale, 3);
});
test('two-finger movement translates once at constant scale', () => {
  const r = zoomBetween({ scale: 2, x: 0, y: 0 }, 1, centre, { x: 12, y: -9 }, b);
  assert.deepEqual(r, { scale: 2, x: 12, y: -9 });
});
test('pan and zoom clamp both image edges', () => {
  const r = moveBy({ scale: 2, x: 0, y: 0 }, 10000, -10000, b);
  assert.deepEqual(r, { scale: 2, x: 160, y: -110 });
  assert.deepEqual(zoomBetween(r, 0.01, centre, centre, b), start);
});
test('invalid gesture values leave the last valid pose intact', () => {
  for (const n of [0, -1, NaN, Infinity]) assert.equal(zoomBetween(start, n, centre, centre, b), start);
  assert.equal(moveBy(start, NaN, 0, b), start);
  assert.equal(zoomBetween(start, 2, { x: NaN, y: 0 }, centre, b), start);
});
test('helpers do not mutate source state', () => {
  const p = Object.freeze({ scale: 2, x: 0, y: 0 });
  moveBy(p, 3, 4, b); zoomBetween(p, 1.1, centre, centre, b);
  assert.deepEqual(p, { scale: 2, x: 0, y: 0 });
});
test('bounded poses stay bounded across a deterministic gesture sequence', () => {
  let p = start;
  for (let i = 0; i < 500; i++) {
    p = zoomBetween(p, 0.9 + (i % 7) / 20, { x: 10, y: 15 }, { x: 12, y: 16 }, b);
    p = moveBy(p, Math.sin(i) * 50, Math.cos(i) * 40, b);
    assert.deepEqual(p, constrain(p, b));
    assert.ok([p.x, p.y, p.scale].every(Number.isFinite));
  }
});
