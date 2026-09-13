# Technical fidelity

Read this reference when documentation contains code, commands, output, APIs, configuration, UI instructions, architecture claims, examples, or other exact technical material.

## Match evidence to the claim

Sources have different jobs; there is no universal ranking that settles every disagreement.

| Claim | Relevant authority | Limit |
|---|---|---|
| Required or promised behavior | Approved requirements, contracts, normative specifications | Establishes the obligation, not that the implementation meets it |
| Behavior of a particular version or deployment | Version-matched code, configuration, schemas, tests, runtime observations | Establishes only what was inspected or exercised under the stated conditions |
| Accepted choice and rationale | Accepted ADR, maintainer decision, release record | Preserve its status, date, and historical scope |
| Third-party contract or supported feature | Official documentation for the relevant dependency version | Does not establish local configuration or actual runtime behavior |
| Reported incident or measurement | Original report, data, and method where available | Distinguish the report from independent observation or verification |

Project documentation supplies terminology and declared behavior, but it can be stale. A test demonstrates behavior under its conditions, not across every configuration. Comments, branch names, unmerged changes, and proposals do not establish released behavior.

When sources disagree, state the material discrepancy. For a fictional fixture with a 30-day requirement and a 7-day configuration: "The specification requires 30-day retention; the supplied configuration sets 7 days." Do not silently turn either statement into the whole truth.

For consequential claims, retain the source location, version or date, conditions, and status in working notes when useful. Keep the reader-facing distinction between observed, reported, required, intended, inferred, proposed, and unknown claims. Do not make a compulsory evidence table for every document.

### Editing versus enrichment

A prose-only edit cannot supply missing facts. An evidence-enriched rewrite may add details from identified sources. Label hypothetical examples and proposed thresholds as such; do not present invented examples as measured results or supported product behavior.

No attempt limit at a call site does not establish unlimited retries. Inspect the implementation, wrappers, and effective configuration before making the broader claim. The same restriction applies to missing validation, absent support checks, or an unobserved failure.

Check entire claims, including causal or evaluative endings. Neither softer wording such as "helps" nor the phrase "is designed to" substitutes for supporting evidence.

## Protect exact literals

Do not change these by stylistic guesswork:

- product and feature names;
- API, class, method, field, parameter, and event names;
- commands, flags, environment variables, configuration keys, and values;
- paths, filenames, package names, URLs, and anchors;
- code, regular expressions, queries, and serialized data;
- UI labels and accessible names;
- version numbers, dates, limits, status labels, and error messages.

Use code font for code-related literals. Use bold for exact UI labels when the project's format supports it.

If a literal appears wrong, verify it before correcting it. In an edit with limited scope, report a suspected technical error separately rather than silently changing it.

## Code samples

A sample should be correct for its stated purpose and small enough to understand.

- Introduce what the sample demonstrates.
- Include required imports, setup, authentication context, and cleanup when the sample is intended to run.
- Keep unrelated production concerns out of a focused sample, but do not omit a requirement that makes it unsafe or invalid.
- Prefer one canonical sample over many near-duplicates.
- Use comments for non-obvious intent, not line-by-line narration.
- Keep lines readable without breaking syntax or hiding important structure.
- Mark pseudocode and incomplete fragments explicitly.
- Do not use real credentials, personal data, production hosts, or unreserved example addresses.
- Test runnable samples only when execution is authorized and the environment is appropriately isolated. Documentation work does not authorize destructive operations, production mutations, use of credentials, or paid external actions. Inspect a command before deciding whether to execute it.
- Do not claim validation that did not happen. Keep irrelevant process commentary out of the document, but disclose an unverified platform, missing prerequisite, or other validation gap that materially affects safe use. Missing product facts cannot be repaired with invented commands or success output.

Do not replace exact code with “cleaner” code unless changing the code is part of the task.

## Commands

- Identify the shell or tool when syntax is not obvious.
- Omit the shell prompt from click-to-copy commands.
- Separate input from output.
- Use the correct continuation character and explain it only when needed.
- Make placeholders descriptive and visually distinct, following project convention. When no convention exists, use `UPPER_SNAKE_CASE` placeholders.
- Define placeholders immediately after the command in appearance order.
- Do not put optional notation such as `[--flag]` inside a command the reader is expected to run. Show separate variants or document syntax as reference.
- Show representative output as representative, not exact, when values vary.
- Explain destructive, recursive, force, overwrite, region-wide, or account-wide effects before the command.
- Include required working directory, identity, environment, and permissions.
- Prefer idempotent or dry-run forms when they serve the task.

## API reference

A reference entry should help the reader use the interface without reading implementation code.

For the applicable surface, document the established facts below. A checklist item is not permission to fill an evidence gap:

- behavior and purpose;
- syntax or signature;
- authentication and permissions;
- parameters, fields, and allowed values;
- defaults and whether omission differs from an explicit null or empty value;
- return value or response schema;
- error and exception conditions;
- side effects, ordering, idempotency, retries, and concurrency behavior;
- limits, quotas, pagination, and version availability;
- examples that demonstrate the common case.

Begin descriptions with behavior, not a repetition of the name:

- Better: “Returns the active subscription for the account.”
- Worse: “The `getSubscription` method gets the subscription.”

Do not describe a single endpoint or method as “the API.”

## Configuration reference

For each setting, document the established facts readers need to choose and operate it:

- exact key and type;
- purpose;
- default and effective default source;
- valid values and units;
- scope and precedence;
- whether restart, redeploy, or migration is required;
- security, cost, or performance consequences;
- version or platform constraints;
- a minimal example.

Do not label a value “recommended” without the scenario or rationale that makes it appropriate.

## UI instructions

- Match visible and accessible labels exactly.
- Use **click** for a desktop pointer target, **tap** for touch, and **press** for a keyboard key or mechanical button.
- Write **select** and **clear** for checkboxes.
- Prefer the control's accessible name over a visual nickname such as “hamburger menu.”
- Name the page, dialog, menu, field, or section before the action when needed.
- Do not rely on position, color, shape, or screenshots alone.
- Use the product's real information architecture; do not call every destination a page or tab.
- State the resulting state when the UI response helps the reader continue.

## Keyboard and text input

- Use semantic keyboard formatting such as `<kbd>` when the output format supports it.
- Spell out standard key names: `Control`, `Command`, `Alt`, `Option`, `Enter`, and `Esc`.
- Use **press** for a key or key combination and **enter** or **type** for text.
- When shortcuts differ by operating system, give the relevant variants: `Control+S` (`Command+S` on macOS).
- Distinguish a literal plus sign from a key combination or action sequence.
- Match the product's documented shortcut and platform behavior exactly.

## Architecture and design claims

Distinguish these categories explicitly:

- **Observed:** inspected or exercised behavior, scoped to the code version, configuration, test, or runtime evidence.
- **Reported:** stated in documentation or an incident or measurement report; not necessarily independently verified.
- **Required:** an obligation from an applicable approved requirement or normative contract.
- **Intended:** stated design goal or invariant from an authoritative decision source.
- **Inferred:** a conclusion drawn from evidence; label it as an inference when material.
- **Proposed:** not yet implemented or approved.
- **Unknown:** not established by the available evidence.

Do not turn a diagram into a claim of runtime behavior without verification. Do not infer guarantees from a happy-path implementation.

For architecture documentation, cover relevant boundaries, data ownership, source of truth, failure behavior, consistency, retries, ordering, security, observability, and lifecycle—not merely component names.

## Future and changing behavior

- Document available behavior, not assumed roadmap.
- Use official feature-state labels exactly.
- Replace **new**, **current**, **latest**, **soon**, **legacy**, and **old** with a version, date, lifecycle state, or precise description when possible.
- Do not infer availability dates from milestones, branches, prototypes, comments, or issue trackers.
- Scope third-party behavior to the relevant version or date when it can change.

## Examples and sample data

- Use fictional names and reserved domains, IP ranges, phone numbers, and identifiers.
- Make examples realistic enough to expose the actual behavior.
- Avoid stereotypes and unnecessary personal attributes.
- State when values are illustrative.
- Do not use examples that normalize insecure practices, hidden destructive actions, or production credentials.
- Keep names consistent across prose, code, output, and diagrams.

## Links and third-party material

- Link to sources that support the particular claim and scope. Preserve source versions and original attribution when they matter.
- Use descriptive link text that states the destination.
- Verify that the label matches the destination.
- Disclose unexpected downloads, sign-in requirements, or application launches when useful.
- Prefer an original summary and link over copied prose, code, screenshots, or diagrams.
- Preserve required licenses and attribution.
- After moving or combining sentences, check that each attached citation still supports the entire claim attributed to it. Retaining a URL is not enough if the revised claim exceeds its evidence.
- Preserve quotation boundaries and exact quoted wording. Do not turn a paraphrase into a quotation or invent a citation. A citation to an uninspected source does not count as independent verification.
- Do not assume public or open-source material can be copied without conditions.

## Docstrings and comments

- Describe public behavior, contracts, side effects, failure conditions, and non-obvious rationale.
- Do not repeat names and types without adding meaning.
- Do not explain obvious syntax.
- Keep comments synchronized with the code.
- During a documentation-only task, flag ambiguous code or a missing test separately; do not refactor it without authorization. A comment cannot repair an ambiguous contract.
- Explain unusual workarounds, including the condition that permits their removal.
