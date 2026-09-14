#!/usr/bin/env node
// Checked execution for bounded, non-interactive commands. Not an authorisation boundary.
import { spawn } from 'node:child_process';
import { pathToFileURL } from 'node:url';
import path from 'node:path';

export function runCommand(command, args = [], options = {}) {
  const { timeoutMs = 120000, maxBytes = 1048576 } = options;
  if (typeof command !== 'string' || !command || !Array.isArray(args) || args.some(x => typeof x !== 'string')) {
    throw new TypeError('Expected a command and an array of string arguments');
  }
  for (const [name, value, max] of [['timeoutMs', timeoutMs, 3600000], ['maxBytes', maxBytes, 16777216]]) {
    if (!Number.isSafeInteger(value) || value < 1 || value > max) throw new RangeError(`Invalid ${name}`);
  }
  return new Promise(resolve => {
    let child, timer, settled = false, bytes = 0;
    let timedOut = false, outputLimitExceeded = false, spawnError = null;
    const output = { stdout: [], stderr: [] };
    const finish = (code = null, signal = null) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      resolve({
        ok: code === 0 && !signal && !timedOut && !outputLimitExceeded && !spawnError,
        code, signal, timedOut, outputLimitExceeded, spawnError,
        stdout: Buffer.concat(output.stdout).toString('utf8'),
        stderr: Buffer.concat(output.stderr).toString('utf8'),
      });
    };
    const stop = () => {
      child.kill('SIGKILL');
      // Descendants can retain pipes. Bound the reader, without killing unrelated companions.
      child.stdout.destroy();
      child.stderr.destroy();
      finish(child.exitCode, child.signalCode);
    };
    try {
      child = spawn(command, args, { shell: false, stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (error) {
      spawnError = error.code || 'SPAWN_ERROR';
      finish();
      return;
    }
    for (const channel of ['stdout', 'stderr']) {
      child[channel].on('data', chunk => {
        if (settled) return;
        const available = Math.max(0, maxBytes - bytes);
        output[channel].push(chunk.subarray(0, available));
        bytes += Math.min(chunk.length, available);
        if (chunk.length > available) {
          outputLimitExceeded = true;
          stop();
        }
      });
    }
    child.on('error', error => {
      spawnError = error.code || 'SPAWN_ERROR';
      finish();
    });
    child.on('close', finish);
    timer = setTimeout(() => { timedOut = true; stop(); }, timeoutMs);
  });
}

async function main(argv) {
  const split = argv.indexOf('--');
  if (split < 0 || !argv[split + 1]) throw new Error('Usage: run.mjs [--timeout-ms N] [--max-bytes N] -- COMMAND ARG...');
  const options = {};
  for (let i = 0; i < split; i += 2) {
    const key = { '--timeout-ms': 'timeoutMs', '--max-bytes': 'maxBytes' }[argv[i]];
    if (!key || i + 1 >= split) throw new Error('Invalid runner option');
    options[key] = Number(argv[i + 1]);
  }
  const result = await runCommand(argv[split + 1], argv.slice(split + 2), options);
  process.stdout.write(JSON.stringify(result) + '\n');
  process.exitCode = result.ok ? 0 : 1;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main(process.argv.slice(2)).catch(error => {
    process.stderr.write(JSON.stringify({ ok: false, error: error.message }) + '\n');
    process.exitCode = 2;
  });
}
