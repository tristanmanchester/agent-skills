import test from 'node:test';
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { runCommand } from '../scripts/run.mjs';
const js = (source, options) => runCommand(process.execPath, ['-e', source], options);

test('success preserves both streams', async () => {
  const r = await js('process.stdout.write("out"); process.stderr.write("err")');
  assert.equal(r.ok, true); assert.equal(r.code, 0);
  assert.equal(r.stdout, 'out'); assert.equal(r.stderr, 'err');
});
test('nonzero never reports success', async () => {
  const r = await js('process.exit(7)'); assert.equal(r.ok, false); assert.equal(r.code, 7);
});
test('spawn failure is an explicit failure', async () => {
  const r = await runCommand('/missing/simulator-test-binary');
  assert.equal(r.ok, false); assert.equal(r.spawnError, 'ENOENT');
});
test('signal is not exit zero', async () => {
  const r = await js('process.kill(process.pid, "SIGTERM")');
  assert.equal(r.ok, false); assert.equal(r.signal, 'SIGTERM');
});
test('timeout is bounded and unsuccessful', async () => {
  const r = await js('setInterval(() => {}, 1000)', { timeoutMs: 100 });
  assert.equal(r.ok, false); assert.equal(r.timedOut, true);
});
test('output is bounded across streams', async () => {
  const r = await js('process.stdout.write("x".repeat(100000)); process.stderr.write("y".repeat(100000))', { maxBytes: 64 });
  assert.equal(r.ok, false); assert.equal(r.outputLimitExceeded, true);
  assert.ok(Buffer.byteLength(r.stdout + r.stderr) <= 64);
});
test('arguments are literal, not shell expanded', async () => {
  const literal = '$(echo injected); * "$HOME"';
  const r = await runCommand(process.execPath, ['-e', 'process.stdout.write(process.argv[1])', literal]);
  assert.equal(r.ok, true); assert.equal(r.stdout, literal);
});
test('invalid limits fail before launch', () => {
  for (const value of [0, -1, NaN, Infinity, 1.1, 3600001]) {
    assert.throws(() => js('', { timeoutMs: value }), RangeError);
  }
});
test('CLI exits nonzero when the child fails', () => {
  const entry = fileURLToPath(new URL('../scripts/run.mjs', import.meta.url));
  const result = spawnSync(process.execPath, [entry, '--', process.execPath, '-e', 'process.exit(9)'], { encoding: 'utf8' });
  assert.equal(result.status, 1); assert.equal(JSON.parse(result.stdout).ok, false);
});
