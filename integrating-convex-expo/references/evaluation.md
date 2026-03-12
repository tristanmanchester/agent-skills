# Evaluating this skill

This skill bundles two evaluation aids:

- `evals/trigger-queries.json`
- `evals/evals.json`

Use them to test both **when the skill triggers** and **whether it produces good outputs once loaded**.

## 1. Trigger evaluation

`evals/trigger-queries.json` contains realistic prompts labelled with `should_trigger: true` or `false`.

### How to use it

- Run each query several times rather than only once.
- Record whether the skill loads.
- Calculate a trigger rate for each query.
- Tighten the description if true cases fail to trigger.
- Add scope or negative guidance if false cases trigger too often.

### What good trigger tests look like

A useful set includes:

- obvious should-trigger requests,
- paraphrases and typo-heavy variants,
- and near-miss should-not-trigger requests such as generic Expo UI work or non-Expo Convex tasks.

## 2. Functional evaluation

`evals/evals.json` contains higher-level tasks with an expected outcome description.

Each case is designed to answer:

- does the skill pick the right workflow,
- does it produce the right edits or guidance,
- does it avoid common Convex mistakes,
- and does it improve results compared with no skill?

## Recommended evaluation loop

### With the skill

Run each eval with this skill available.

### Without the skill

Run the same eval in a clean session without the skill, or against the previous skill version.

### Compare

Look at:

- correctness,
- completeness,
- tool choice,
- number of avoidable follow-up questions,
- and whether the output follows Convex best practices.

## What to grade in this skill specifically

- correct Expo entrypoint detection,
- correct use of `EXPO_PUBLIC_CONVEX_URL`,
- correct root provider wiring,
- generated API usage,
- validators on public Convex functions,
- auth enforced on the backend,
- correct action vs mutation boundaries,
- pagination for growing lists,
- and migration safety when schema changes are involved.

## Suggested lightweight rubric

For each functional eval, score:

- **Pass**: the output is correct and production-safe.
- **Borderline**: the main idea is right but it misses one important hardening step.
- **Fail**: it uses the wrong workflow or introduces unsafe patterns.

## Iteration advice

If the skill under-triggers:

- add clearer user-intent phrases to the frontmatter description,
- include more Expo-specific language,
- and add near-obvious trigger phrases such as `expo-router`, `EXPO_PUBLIC_CONVEX_URL`, `useQuery undefined`, `Clerk`, or `file://` uploads.

If it over-triggers:

- narrow the description,
- add “do not use” scope language,
- and add more near-miss negatives to the trigger file.

If it loads correctly but outputs weak advice:

- strengthen the body instructions,
- move specifics into references,
- and expand the functional eval set around the weak scenario.
