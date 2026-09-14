import test from 'node:test';
import assert from 'node:assert/strict';
import { prepareRequest } from '../scripts/request.mjs';
const input = () => ({audio:'./test.wav'});
test('defaults to current ordered model route and automatic language', () => {
  const r=prepareRequest(input()); assert.deepEqual(r.speech_models,['universal-3-5-pro','universal-2']); assert.equal(r.language_detection,true);
});
test('manual language is preserved without auto detection', () => {
  assert.equal(prepareRequest({...input(),language_code:'de'}).language_detection,undefined);
});
test('conflicting language and singular legacy model rejected', () => {
  assert.throws(()=>prepareRequest({...input(),language_code:'de',language_detection:true}));
  assert.throws(()=>prepareRequest({...input(),speech_model:'universal-3-pro'}));
});
test('prompt requires a compatible reviewed model', () => {
  assert.throws(()=>prepareRequest({...input(),speech_models:['universal-2'],prompt:'Corrosion research'}));
  assert.equal(prepareRequest({...input(),speech_models:['universal-3-5-pro'],prompt:'Corrosion research'}).prompt,'Corrosion research');
});
test('keyterm phrase and total budgets enforced', () => {
  assert.throws(()=>prepareRequest({...input(),keyterms_prompt:['one two three four five six seven']}));
  assert.throws(()=>prepareRequest({...input(),keyterms_prompt:Array(501).fill('two words')}));
  assert.equal(prepareRequest({...input(),keyterms_prompt:['X-ray tomography']}).keyterms_prompt[0],'X-ray tomography');
});
test('malformed input rejected before upload', () => {
  for (const r of [null,{}, {...input(),speech_models:[]},{...input(),language_detection:'false'},{...input(),keyterms_prompt:[null]}]) assert.throws(()=>prepareRequest(r));
});
