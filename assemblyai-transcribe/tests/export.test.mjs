import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { createHash } from 'node:crypto';
import { normalise, markdown, writeBundle } from '../scripts/export.mjs';
const raw = () => ({ id: '../../not-a-filename', status: 'completed', text: 'Hello', speech_model_used: 'universal-3-5-pro', utterances: [{ speaker: 'A', start: 0, end: 1000, text: 'Hello' }], words: [{ text: 'Hello', start: 0, end: 1000 }] });
test('zero timestamps and source model retained', () => {
  const d = normalise(raw()); assert.equal(d.words[0].start, 0); assert.equal(d.speech_model_used, 'universal-3-5-pro');
});
test('missing timestamps are not invented', () => {
  const r = raw(); delete r.utterances[0].start; assert.equal(normalise(r).utterances[0].start, null);
});
test('invalid and reversed spans fail', () => {
  for (const value of [-1, NaN, Infinity, '0']) { const r=raw(); r.words[0].start=value; assert.throws(()=>normalise(r)); }
  const r=raw(); r.words[0].end=-1; assert.throws(()=>normalise(r));
  r.words[0].start=2000; r.words[0].end=1000; assert.throws(()=>normalise(r));
});
test('completed is distinct from pending or failed', () => {
  for (const status of ['queued','processing','error',null]) assert.throws(()=>normalise({...raw(),status}));
});
test('manual mapping overrides provider without changing raw identity', () => {
  const r=raw(); const id=JSON.stringify([null,'A']);
  const u=normalise(r,{[id]:'Tristan'},{[id]:'Host'}).utterances[0];
  assert.equal(u.display,'Tristan'); assert.equal(u.display_source,'manual'); assert.equal(u.speaker,'A'); assert.equal(r.utterances[0].display,undefined);
});
test('same speaker token in different channels is not conflated', () => {
  const r=raw(); r.utterances=[{...r.utterances[0],channel:0},{...r.utterances[0],channel:1}];
  const d=normalise(r,{ '[0,"A"]':'First' }); assert.notEqual(d.utterances[0].identity,d.utterances[1].identity); assert.equal(d.utterances[1].display_source,'generic');
});
test('malformed arrays and map entries rejected', () => {
  assert.throws(()=>normalise({...raw(),words:{}})); assert.throws(()=>normalise(raw(),{'A':5}));
});
test('empty successful transcript stays empty', () => {
  const d=normalise({status:'completed',text:''}); assert.equal(d.text,''); assert.deepEqual(d.words,[]);
});
test('Markdown escapes injected markup', () => {
  const d=normalise({status:'completed',text:'<script>bad</script> [go](https://x.test)'});
  const out=markdown(d); assert.ok(!out.includes('<script>')); assert.ok(!out.includes('[go]('));
});
test('bundle preserves unknown annotations and hashes files', async t => {
  const root=await fs.mkdtemp(path.join(os.tmpdir(),'aai-export-')); t.after(()=>fs.rm(root,{recursive:true,force:true}));
  const r={...raw(),speech_understanding:{future_field:'preserved'}}; const dest=path.join(root,'out');
  const m=await writeBundle(r,dest); assert.equal(m.complete,true);
  assert.deepEqual(JSON.parse(await fs.readFile(path.join(dest,'raw.json'),'utf8')),r);
  for (const entry of m.files) assert.equal(createHash('sha256').update(await fs.readFile(path.join(dest,entry.path))).digest('hex'),entry.sha256);
  await assert.rejects(writeBundle(r,dest));
});
