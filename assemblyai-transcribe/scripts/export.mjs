#!/usr/bin/env node
// Offline exports only: no credentials, uploads, inferred identities, or API calls.
import fs from 'node:fs/promises';
import { constants } from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { parseArgs } from 'node:util';
import { pathToFileURL } from 'node:url';

function object(value, label) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) throw new TypeError(`${label} must be an object`);
  return value;
}
function mapping(value) {
  object(value, 'speaker map');
  if (Object.values(value).some(x => typeof x !== 'string' || !x.trim())) throw new TypeError('Speaker names must be nonempty strings');
  return value;
}
function time(value) {
  if (value === undefined || value === null) return null;
  if (typeof value !== 'number' || !Number.isFinite(value) || value < 0) throw new TypeError('Invalid millisecond timestamp');
  return value;
}
function span(value) {
  object(value, 'timed item');
  const start = time(value.start), end = time(value.end);
  if (start !== null && end !== null && end < start) throw new TypeError('End precedes start');
  return { ...value, start, end };
}
function rows(value, label) {
  if (value === undefined || value === null) return [];
  if (!Array.isArray(value)) throw new TypeError(`${label} must be an array`);
  return value;
}
export function normalise(raw, manual = {}, provider = {}) {
  object(raw, 'transcript'); mapping(manual); mapping(provider);
  if (raw.status !== 'completed') throw new Error('A completed raw transcript is required; preserve pending/error outcomes separately');
  if (typeof raw.text !== 'string') throw new TypeError('Transcript text must be a string');
  const utterances = rows(raw.utterances, 'utterances').map(value => {
    const u = span(value);
    if (typeof u.text !== 'string') throw new TypeError('Utterance text must be a string');
    const channel = u.channel ?? null, speaker = u.speaker ?? null;
    if (![channel, speaker].every(x => x === null || typeof x === 'string' || (typeof x === 'number' && Number.isFinite(x)))) {
      throw new TypeError('Invalid channel or speaker token');
    }
    const identity = JSON.stringify([channel, speaker]);
    const source = Object.hasOwn(manual, identity) ? 'manual' : Object.hasOwn(provider, identity) ? 'provider' : 'generic';
    const display = source === 'manual' ? manual[identity] : source === 'provider' ? provider[identity]
      : [channel === null ? '' : `Channel ${channel}`, speaker === null ? '' : `Speaker ${speaker}`].filter(Boolean).join(' / ') || 'Unlabelled';
    return { ...u, words: rows(u.words, 'utterance words').map(span), identity, display, display_source: source };
  });
  return {
    schema_version: 1, provider: 'assemblyai', transcript_id: raw.id ?? null,
    status: raw.status, timestamp_unit: 'milliseconds',
    speech_model_used: raw.speech_model_used ?? null, language_code: raw.language_code ?? null,
    text: raw.text, utterances, words: rows(raw.words, 'words').map(span),
    annotation_source: 'raw.json',
  };
}
function clock(ms) {
  if (ms === null) return 'time unavailable';
  const sec = Math.floor(ms / 1000);
  return `${String(Math.floor(sec / 3600)).padStart(2, '0')}:${String(Math.floor(sec / 60) % 60).padStart(2, '0')}:${String(sec % 60).padStart(2, '0')}`;
}
// Escaping makes transcript text inert Markdown; it is still untrusted input to an agent.
function escape(text) { return text.replace(/[\\`*_{}\[\]()#+.!<>|~=\-]/g, '\\$&'); }
export function markdown(data) {
  const lines = ['# Transcript', '', 'Machine transcription; verify names, numbers, and material quotations against the recording.', '', '## Transcript', ''];
  if (!data.utterances.length) lines.push(escape(data.text));
  for (const u of data.utterances) lines.push(`**${escape(u.display)} [${clock(u.start)}]**`, '', escape(u.text), '');
  return lines.join('\n') + '\n';
}
export async function writeBundle(raw, destination, manual = {}, provider = {}) {
  const data = normalise(raw, manual, provider);
  const files = { 'raw.json': JSON.stringify(raw, null, 2) + '\n', 'agent.json': JSON.stringify(data, null, 2) + '\n',
    'transcript.md': markdown(data), 'transcript.txt': raw.text + '\n' };
  // An existing directory is never overwritten, even when it looks empty.
  await fs.mkdir(destination, { mode: 0o700 });
  const entries = [];
  for (const [name, content] of Object.entries(files)) {
    await fs.writeFile(path.join(destination, name), content, { flag: 'wx', mode: 0o600 });
    entries.push({ path: name, bytes: Buffer.byteLength(content), sha256: createHash('sha256').update(content).digest('hex') });
  }
  const manifest = { schema_version: 1, complete: true, transcript_id: data.transcript_id,
    timestamp_unit: data.timestamp_unit, files: entries };
  // Manifest is written last. A failed export can leave a private partial directory.
  await fs.writeFile(path.join(destination, 'manifest.json'), JSON.stringify(manifest, null, 2) + '\n', { flag: 'wx', mode: 0o600 });
  return manifest;
}
async function readJson(filename) {
  const handle = await fs.open(filename, constants.O_RDONLY | (constants.O_NOFOLLOW ?? 0));
  try {
    if (!(await handle.stat()).isFile()) throw new Error('Input must be a regular JSON file');
    const limit = 32 * 1024 * 1024;
    const buffer = Buffer.alloc(limit + 1);
    let total = 0;
    while (total < buffer.length) {
      const { bytesRead } = await handle.read(buffer, total, buffer.length - total, null);
      if (!bytesRead) break;
      total += bytesRead;
    }
    if (total > limit) throw new Error('Input exceeds the 32 MiB limit');
    return JSON.parse(buffer.subarray(0, total).toString('utf8'));
  } finally { await handle.close(); }
}
async function main() {
  const { values } = parseArgs({ options: { input: { type: 'string' }, output: { type: 'string' },
    'manual-map': { type: 'string' }, 'provider-map': { type: 'string' } }, strict: true, allowPositionals: false });
  if (!values.input || !values.output) throw new Error('Usage: export.mjs --input raw.json --output NEW_DIRECTORY [--manual-map file.json] [--provider-map file.json]');
  const result = await writeBundle(await readJson(values.input), path.resolve(values.output),
    values['manual-map'] ? await readJson(values['manual-map']) : {},
    values['provider-map'] ? await readJson(values['provider-map']) : {});
  process.stdout.write(JSON.stringify({ output: path.resolve(values.output), ...result }) + '\n');
}
if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  main().catch(error => { console.error(error.message); process.exitCode = 1; });
}
