# Document shapes

Read this reference before creating or substantially restructuring a full document. Choose the smallest shape that serves the reader. Treat these as defaults, not mandatory templates.

## General rules

- Give each page one primary job.
- Organize around what the reader needs to learn, do, find, decide, or recover from.
- Make the page useful when entered from search or a direct link.
- Put the recommended route first.
- Link to supporting explanation or reference instead of interrupting the main path.
- Do not add a section merely because it appears in a common template.
- For a small topic, a short page is better than an inflated document.

## README or project overview

A README helps a new or returning reader decide whether the project is relevant and reach a first useful result.

Use only the sections the project needs:

1. **What it is and when to use it.** One short paragraph. Lead with the concrete purpose, not a slogan.
2. **Quick start.** The shortest supported path to a meaningful result.
3. **Prerequisites.** Required software, access, versions, and environment assumptions.
4. **Common tasks.** Link to fuller guides rather than reproducing them.
5. **Configuration.** Document required settings and the most common options; link to exhaustive reference.
6. **Troubleshooting.** Cover only frequent blockers, or link to a dedicated guide.
7. **Development or contribution.** Include only when the README serves contributors.
8. **Ownership and support.** State the responsible team or support route when useful.

Avoid badges, feature inventories, architecture tours, and contribution boilerplate that do not help the intended reader.

## Tutorial

A tutorial creates a successful learning experience. It is not merely a long how-to guide.

- State what the learner will build or experience.
- Use a controlled, reproducible setup.
- Follow one safe path. Do not present branches and alternatives unless they are part of the lesson.
- Introduce concepts only when the learner needs them.
- Use concrete inputs and show meaningful checkpoints.
- Explain enough for learning, but link to deeper explanation and reference.
- End with a working result and a concise account of what the learner learned.
- Make cleanup or reset possible when the tutorial changes external state or incurs cost.

Do not use a tutorial to catalog all features or solve an arbitrary production problem.

## How-to guide

A how-to guide helps a competent reader complete a real task.

- Use a goal-oriented title such as “Rotate an API key.”
- State the applicable conditions and prerequisites.
- Begin near the point where the reader needs help; do not reteach basic concepts.
- Give the safest, most common supported path first.
- Include branches only for materially different cases.
- Keep explanation subordinate to the task. Link to conceptual material when it would interrupt the flow.
- State how to verify success and what to do when the expected result does not occur.
- Include rollback or cleanup for consequential changes.

## Concept or explanation guide

An explanation helps the reader understand why a system behaves as it does, how parts relate, or what tradeoffs matter.

A useful shape is:

1. The question, problem, or central claim.
2. The minimum context needed to follow the explanation.
3. The mental model or relationship between components.
4. A concrete example or diagram when it clarifies the model.
5. Consequences, tradeoffs, limitations, and common misconceptions.
6. Links to related tasks and reference material.

Do not disguise a task procedure or option catalog as an explanation. Avoid chronology unless history explains the current design.

## Reference documentation

Reference content is for lookup. Predictability and completeness matter more than narrative flow.

- Mirror the structure of the thing being described.
- Use a stable entry pattern.
- State facts neutrally and precisely.
- Keep behavior, syntax, parameters, defaults, constraints, return values, errors, side effects, permissions, and versions easy to locate.
- Put examples after the normative description.
- Do not bury reference facts in tutorial prose or marketing claims.
- Link to procedures and explanations instead of mixing them into every entry.

For APIs, commands, configuration, and UI, also read [Technical fidelity](technical-fidelity.md).

## Design document or RFC

A design document helps reviewers understand a problem, evaluate a proposal, and see its consequences. It must distinguish evidence from recommendation.

Use the relevant sections:

1. **Summary or decision request.** State the proposed direction and what feedback or approval is needed.
2. **Context and problem.** Describe the observed problem, affected users or systems, and supporting evidence.
3. **Goals and non-goals.** Bound the proposal. Do not use non-goals to evade foreseeable consequences.
4. **Constraints and assumptions.** Include technical, product, operational, legal, cost, timeline, and compatibility constraints that shape the design.
5. **Proposed design.** Explain components, data or control flow, interfaces, states, and invariants at the level needed for review.
6. **Alternatives.** Include serious alternatives and why the proposal is preferable under the stated constraints. Do not invent straw alternatives.
7. **Failure modes and risks.** Cover partial failure, concurrency, retries, security boundaries, data loss, abuse, observability, and operator error when applicable.
8. **Rollout and migration.** State compatibility, sequencing, backfill, feature flags, rollback, and success criteria.
9. **Open questions.** List genuine unresolved decisions with owners or decision conditions when known.

Do not spend half the document restating the problem, or hide the actual proposal behind background. Use diagrams only when they clarify relationships that prose cannot express efficiently.

## Architecture decision record

An ADR records a decision in its historical context.

A compact shape is:

- **Status and date**
- **Context**
- **Decision**
- **Rationale**
- **Consequences**
- **Alternatives considered**
- **Supersedes or superseded by**, when applicable

Write the decision in concrete terms. Keep speculative implementation detail out unless it formed part of the decision. Do not rewrite an accepted ADR to match a later design; add a new ADR that supersedes it.

## Runbook

A runbook helps an operator act safely under time pressure.

Put urgent information first:

1. Trigger conditions or alert name.
2. Impact and immediate safety concerns.
3. Required access, permissions, and tools.
4. Fast checks that confirm the condition.
5. Decision points based on observable evidence.
6. Remediation steps, ordered from least to most disruptive.
7. Verification of recovery.
8. Rollback, escalation, and stop conditions.
9. Evidence to preserve and follow-up actions.

Commands must be exact, scoped, and clearly marked when destructive. Do not rely on institutional memory or vague instructions such as “check the service.” Name the signal, command, dashboard, or expected result.

## Troubleshooting guide

Start from what the reader can observe, not from an internal cause they may not know.

For each problem:

- symptom or error text;
- likely applicability conditions;
- safest diagnostic check;
- interpretation of each relevant result;
- corrective action;
- verification;
- escalation or further evidence to collect.

Prefer a small decision tree over a long undifferentiated list of causes. Do not ask readers to make destructive changes merely to test a theory.

## Onboarding guide

An onboarding guide should get a defined audience to a first independent success.

- State who the guide is for and what completion means.
- Put access and account dependencies first.
- Separate one-time setup from recurring work.
- Give a minimal first task that verifies the environment.
- Link to common workflows, terminology, ownership, and support routes.
- Mark organization-specific assumptions that outsiders would not know.
- Avoid a tour of every tool, team, and system.

## Migration guide

A migration guide must make impact and required action unmistakable.

Include:

- affected users, versions, configurations, or data;
- the reason for migration only to the extent that it helps planning;
- deadlines and lifecycle states from authoritative sources;
- prerequisites and compatibility limits;
- ordered migration steps;
- verification and observability;
- rollback or recovery;
- known behavior changes and unsupported cases.

Distinguish required actions from optional improvements. Do not use relative terms such as “soon” or “the new API” when an exact date or version is available.

## Release note

A release note helps affected readers understand what changed and whether they must act.

Lead with the reader impact, not the implementation work.

- Name the product, version, date, and feature state precisely.
- State who is affected.
- Separate added, changed, fixed, deprecated, and removed behavior when useful.
- Include required actions, compatibility, and links to migration guidance.
- Avoid promotional adjectives and claims that every change is important.
- Do not call a change “minor” when impact depends on the reader's configuration.

## Docstrings and code comments

Document contracts, behavior, rationale, and non-obvious constraints—not syntax already visible in the code.

Useful content includes:

- public behavior and side effects;
- parameter meaning beyond its type and name;
- return and error conditions;
- ownership or lifetime constraints;
- concurrency and ordering assumptions;
- invariants and why an unusual implementation exists;
- security or compatibility constraints.

Do not narrate each line, repeat the function name, or preserve a stale explanation when the code changes.

## Multi-page documentation sets

- Keep one source of truth for each fact or procedure.
- Link instead of copying substantial content.
- Use consistent names and content-type boundaries.
- Make navigation reflect reader tasks and concepts, not the repository tree by default.
- Preserve useful standalone context at likely search entry points.
- When moving or renaming pages, protect incoming links and heading anchors.
