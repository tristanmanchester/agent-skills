// Current pre-recorded SDK request preparation. No upload or network access.
export function prepareRequest(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input)) throw new TypeError('Expected an SDK request object');
  if (typeof input.audio !== 'string' || !input.audio.trim()) throw new TypeError('A nonempty audio path or URL is required');
  if ('speech_model' in input) throw new Error('Pre-recorded requests use speech_models, not speech_model');
  const request = { ...input, speech_models: input.speech_models ?? ['universal-3-5-pro', 'universal-2'] };
  if (!Array.isArray(request.speech_models) || !request.speech_models.length || request.speech_models.some(x => !['universal-3-5-pro', 'universal-2'].includes(x))) {
    throw new Error('Choose current reviewed models explicitly; recheck this helper before adding a new model');
  }
  if (input.language_code !== undefined && (typeof input.language_code !== 'string' || !input.language_code.trim())) throw new TypeError('Invalid language_code');
  if (input.language_detection !== undefined && typeof input.language_detection !== 'boolean') throw new TypeError('language_detection must be boolean');
  if (input.language_code && input.language_detection) throw new Error('Choose manual language or automatic detection, not both');
  if (!input.language_code && input.language_detection === undefined) request.language_detection = true;
  if (input.prompt !== undefined) {
    if (typeof input.prompt !== 'string' || !input.prompt.trim()) throw new TypeError('Context prompt must be nonempty text');
    if (!request.speech_models.includes('universal-3-5-pro')) throw new Error('Contextual prompting needs Universal-3.5 Pro');
  }
  if (input.keyterms_prompt !== undefined) {
    if (!Array.isArray(input.keyterms_prompt)) throw new TypeError('keyterms_prompt must be an array');
    let words = 0;
    for (const term of input.keyterms_prompt) {
      if (typeof term !== 'string' || !term.trim()) throw new TypeError('Keyterms must be nonempty strings');
      const count = term.trim().split(/\s+/).length;
      if (count > 6) throw new Error('A keyterm phrase may contain at most six words');
      words += count;
    }
    if (words > 1000) throw new Error('Keyterms exceed the conservative 1000-word budget; provider tokenisation can impose a lower limit');
  }
  return request;
}
