# Clear prose

Use this reference for a substantive prose rewrite or a specific problem with clarity, tone, uncertainty, or the connections between ideas. These are editorial judgments, not tests of AI authorship.

## Begin with something the reader needs

Start with a finding, instruction, decision, useful question, or necessary context. "This document explains" often delays the information; an explicit scope statement is useful when it tells the reader what the guidance applies to.

Do not create an overview, benefits section, FAQ, key takeaways, and conclusion by default. A summary can legitimately repeat findings for a different reading path. A closing paragraph can synthesize consequences or state a decision; it need not repeat the opening to sound finished.

## Put uncertainty in the claim

State the strongest claim the evidence supports, with its material conditions and limitations. Do not remove uncertainty to satisfy a request for confident prose.

Given evidence that two candidates share the measured features and the measurement cannot distinguish them:

> The measured features are consistent with either candidate; this measurement does not distinguish them.

This carries the information more directly than "I would be cautious about claiming a unique identification." The limitation belongs to the measurement, not to the author's willingness to make a claim.

Negative findings are substantive: "The test did not reproduce the failure" does not mean "The failure cannot occur." Preserve that distinction. A lack of evidence at one location is not a system-wide negative result.

Use attribution when it matters: "The operator reported three failures" is different from three independently observed failures. Avoid repeated "it seems," "perhaps," or "I would not claim" when one precise qualifier supplies the same uncertainty. Retain a qualifier that changes probability, scope, or the reader's decision.

## Check each step from evidence to implication

A sentence can begin with a verified fact and end with an unsupported consequence. Inspect clauses introduced by "therefore," "which improves," "ensuring," "demonstrating," or "highlighting." Ask whether the source establishes that consequence and whether the reader needs it.

For example, a source that establishes only encrypted object storage does not establish an overall secure or reliable service. Delete the broad assurance or replace it with a specifically supported property; do not substitute "helps" as camouflage for the same claim.

Distinguish requirements, actual behavior, design intent, inference, and proposal. "Is designed to" needs a source for intent. "Helps" still claims a contribution. "Might" is not permission to add an ungrounded mechanism.

Reasoned judgments and recommendations are useful when requested. State the criterion, evidence, and assumptions instead of disguising a judgment as a measured fact.

## Connect sentences and paragraphs

Let each sentence carry a manageable idea without forcing one clause per sentence. Make cause, contrast, sequence, and referents explicit. Use an established concept as the starting point when that helps readers follow the next development.

Given an established lease mechanism:

> When a lease expires, another worker can claim the job. If the original worker is still running, both workers can execute it.

The reader does not have to reconstruct the relationship from four fragments about leases, expiry, workers, and duplicates.

Use transitions for meaning, not ceremony. "However" is useful for a genuine contrast; repeated "Furthermore" does not connect unrelated observations. A paragraph can begin with a short bridge when the main point otherwise lacks context.

Keep support and qualification close to their claim. Break a paragraph when the purpose or subject changes, not merely to produce uniform paragraph lengths. Avoid both long clause chains and strings of abrupt one-sentence blocks. Do not randomly vary rhythm to simulate a human writer.

## Choose focus, voice, and syntax

Prefer direct verbs over needless nominalizations: "evaluate" rather than "perform an evaluation of." Keep modifiers beside what they modify, and unpack noun stacks when their relationships are unclear.

Use active voice when it clarifies responsibility. Passive voice is appropriate when the object is the topic, the actor is irrelevant, or responsibility is already clear. "The token is refreshed after it expires" can remain unchanged; do not invent the client as actor or imply self-action just to avoid the passive.

Put conditions and warnings before instructions they govern. In explanation, use the order that preserves focus and makes the dependency clear. Prefer positive constructions to tangled double negatives, but keep meaningful negative findings, prohibitions, and exceptions.

No sentence-length quota applies. Split a sentence when it asks too much of the reader; join fragments when their relationship otherwise becomes obscure.

## Make technical language earn its place

Use one established term for one concept. Define unfamiliar terminology at its first useful mention, but do not explain concepts the intended audience already knows.

Ask what an abstract phrase commits the system to doing. Can the reader identify the actor, operation, affected state, or relationship? A phrase such as "a coherent operational layer" may need explanation rather than another adjective.

Do not replace useful specialist terms with longer, less accurate euphemisms. "Robust estimator" and a precisely supported statistical use of "significant" are not marketing claims. Words such as "robust," "seamless," "complete," and "always" warrant a meaning-and-evidence check, not automatic deletion. Em dashes, three-item lists, and particular vocabulary do not establish authorship.

## Avoid manufactured rhetoric

Use a contrast when it distinguishes real behaviors or consequences. "At-least-once delivery is not exactly-once execution" can teach a crucial distinction. "This is not merely a tool; it is a new way of working" adds little without explaining what changes.

Question phrases such as "the real challenge," "what matters most," or "this highlights the importance" when they claim significance without a criterion or evidence. Do not force symmetrical sections, three-part slogans, decorative rhetorical questions, fake quotations, or an invented opposing view.

A natural technical voice is calm and specific. Avoid hype, unnecessary ceremony, reader blame, and performative enthusiasm. Do not describe a task as trivial when it may be unfamiliar. Retain an author's useful personality; do not add anecdotes, slang, jokes, or errors to make the text seem human.

## Preserve modality and time

Use **must** for requirements, **can** for capability or optional action, **might** for possibility, and explicit recommendation language for an optional choice. Use present tense for established behavior and the appropriate tense for historical findings or decisions.

Resolve ambiguous **should** from evidence, not taste. Preserve formal normative keywords and quoted language. Do not turn "should retry" into "must retry" without establishing which meaning was intended.

Use dates, versions, and lifecycle states when relative wording would drift. A bounded phrase such as "the current transaction" can already be exact. Do not replace every temporal word mechanically.

## Reduce effort without flattening the prose

For each passage, ask what it contributes and what the reader would need to reconstruct without it. Remove redundant announcements, filler, and duplicated claims with no distinct purpose. Retain a helpful mental model, example, summary, or standalone warning even if it increases length.

Common edits include "in order to" to "to," "due to the fact that" to "because," and "it is important to note that" to the point itself. Make the change only when meaning and emphasis survive. Do not invent an exact number to replace "several."

Use lists for parallel items, sequence, comparison, or lookup. Use prose for a connected argument. Headings should help someone find an answer; repeated bold pseudo-headings on every sentence rarely help.

For an existing passage, prefer no change over a change with no reader-facing benefit. Read the revision at a natural pace and check that it retains the author's effective voice, logical connections, and supported meaning. Stop when further changes are merely preferences.
