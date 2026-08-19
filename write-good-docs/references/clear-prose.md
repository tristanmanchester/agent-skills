# Clear prose

Read this reference when drafting or rewriting for clarity and concision, especially when the source is dense, repetitive, vague, overformal, or AI-sounding.

## Aim

Clear prose makes the reader do less interpretive work. Concise prose is complete without avoidable friction; it is not prose with facts removed.

## Sentences

- Give each sentence one main job.
- Put the subject and verb early.
- Prefer a direct subject-verb-object structure.
- Use active voice unless the actor is unknown, irrelevant, or intentionally concealed.
- Name the actor when ownership or responsibility matters.
- Put a condition before the instruction or outcome it governs.
- Prefer positive constructions over double negatives and exceptions to exceptions.
- Split clause chains. A sentence with several commas, parentheses, dashes, or semicolons often needs rewriting.
- Replace noun-heavy phrases with verbs: **perform an evaluation of** → **evaluate**.
- Expose relationships in stacked nouns: **customer profile update event handling logic** → **logic that handles customer-profile update events**.
- Keep modifiers next to what they modify.
- Use parallel grammar for comparable items.

Do not enforce an arbitrary sentence-length limit. Use the shortest sentence that carries the full meaning naturally.

## Paragraphs

- Center each paragraph on one idea.
- Put the key point first.
- Keep supporting detail close to the claim it supports.
- Start a new paragraph when the subject, purpose, time, actor, or level of detail changes.
- Avoid one-sentence paragraphs in a long sequence unless the separation creates useful emphasis or scanning.
- Do not split one coherent idea into many tiny paragraphs merely to make the page look light.

## Natural technical tone

Sound like a knowledgeable colleague: direct, calm, respectful, and specific.

Prefer:

- familiar words over ceremony;
- literal wording over idioms and metaphors;
- confidence that matches the evidence;
- contractions when they fit the project's tone;
- a small amount of personality only when it does not delay the information.

Avoid:

- academic or bureaucratic phrasing when plain language works;
- marketing language, hype, and slogans;
- forced enthusiasm, jokes, memes, and pop-culture references;
- scolding or talking down to the reader;
- repeated **please** in ordinary instructions;
- exclamation marks except for rare genuine emphasis;
- describing a task as easy, simple, obvious, trivial, painless, or quick.

## Write for humans, not for the shape of a document

Agents often produce prose that looks organized while making the reader work harder. Remove these patterns:

- a title followed by an opening that restates the title;
- “This document will cover...,” “In this section...,” or “The following guide provides...”;
- a generic **Overview** before the actual answer;
- a **Benefits** section that repeats intended behavior as marketing claims;
- **Key takeaways** and **Conclusion** sections that repeat the body;
- an FAQ invented without evidence that readers ask those questions;
- three near-synonymous adjectives such as “robust, scalable, and reliable”;
- repetitive transition words such as **Additionally**, **Furthermore**, and **Moreover**;
- symmetrical sectioning that forces every topic into the same number of bullets;
- fake quotations, invented reader thoughts, or rhetorical questions used as decoration;
- meta-commentary about research, analysis, completeness, or how the answer was produced.

Do not add prose to make the output feel substantial. Let a short topic remain short.

## Concision pass

For each sentence or section, ask:

1. Does it add a fact, decision, condition, action, rationale, example, warning, or navigation aid?
2. Does the reader need it here?
3. Is the idea already stated?
4. Can the same meaning be expressed more directly?
5. Would removing it create ambiguity, risk, or a gap in execution?

Cut it when the first two answers are no and the fifth is no.

Common compressions, when meaning is preserved:

| Wordy | Direct |
|---|---|
| in order to | to |
| due to the fact that | because |
| at this point in time | now, or an exact date/version |
| has the ability to | can |
| is able to | can |
| make use of / utilize | use |
| perform a review of | review |
| provide an explanation of | explain |
| a number of | several, or the exact number |
| in the event that | if |
| prior to | before |
| subsequent to | after |
| with regard to | about |
| it is important to note that | state the point directly |
| please note | state the point directly |
| as mentioned above | name or link the section |
| the following | often omit |
| there are three options | three options are available, or list them directly |

Do not perform blind replacement. **In order to** can be necessary to avoid ambiguity, and **current** can be correct when the reference point is explicit.

## Terminology and jargon

- Use the same term for the same concept.
- Do not vary terminology for style.
- Prefer an established precise technical term over a simpler but inaccurate substitute.
- Define unfamiliar terms and abbreviations at the first useful mention.
- Do not define terms the audience clearly knows merely to sound thorough.
- Spell out an abbreviation only when the expansion helps the reader.
- Avoid internal codenames and organization-specific shorthand unless the audience uses them; explain them when unavoidable.
- Do not use **API** to mean a single endpoint, method, request, or class. Name the actual item.

## Person, voice, and tense

- Address the reader as **you** in task-oriented documentation.
- Use an imperative for direct steps: “Run the command.”
- Use **we** only for the organization or authoring team when that actor matters; do not use it to mean the reader and writer together.
- Avoid **let's** in instructions.
- Use present tense for product behavior unless a different time is material.
- Use future tense only for a genuinely future event, not a predictable result: “The command returns...” rather than “The command will return....”
- Avoid anthropomorphism that assigns knowledge, desire, belief, or intention to software. State the observable behavior or design intent.

## Obligation, recommendation, and uncertainty

Choose words that tell the reader exactly what category a statement belongs to:

- **must** or an imperative: required action or condition;
- **can**: capability or optional action;
- **might**: possible outcome;
- **we recommend** plus a reason: recommended but optional action;
- present tense: actual behavior or state;
- **is designed to** or **helps**: intended contribution without a guarantee.

Avoid ambiguous **should**. When it remains, make sure it clearly means a recognized recommendation rather than a requirement, expected state, or guess.

Do not change modality while editing. A possibility must not become a guarantee, and a recommendation must not become a requirement.

## Claims

- Make only objective, supportable claims.
- Scope performance, cost, reliability, compatibility, and security claims to a version, configuration, scenario, and measurement when those details matter.
- Prefer observable behavior over adjectives.
- Avoid guarantees and superlatives unless evidence and scope make them literally true.
- Do not infer roadmaps from code, prototypes, issue trackers, or discussion.
- Replace time-relative labels with exact versions, dates, or lifecycle states when possible.

Treat these as warning signs:

**always**, **never**, **guaranteed**, **ensures**, **best**, **fastest**, **easiest**, **simplest**, **cheapest**, **most secure**, **flawless**, **complete**, **perfect**, **dramatically**, **significantly**, **seamless**, **robust**.

## Lists versus prose

Use a list when items are genuinely parallel, sequence matters, or lookup is easier. Use prose when ideas form an argument or each item needs substantial qualification.

Avoid:

- a bullet list with one item;
- bullets that each contain several unrelated sentences;
- a list where every bullet begins with a bold pseudo-heading and a paragraph;
- nested lists deeper than the reader can hold in working memory;
- converting a natural two-sentence explanation into bullets solely for visual variety.

## Final human read

Read the prose at a natural speaking pace.

Fix:

- wording you would not say to a colleague;
- abrupt sentence fragments that make the prose choppy;
- long sentences that require rereading;
- repeated sentence openings;
- paragraphs whose point appears only at the end;
- transitions that announce structure instead of expressing meaning.
