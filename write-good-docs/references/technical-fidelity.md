# Technical fidelity

Read this reference when documentation contains code, commands, output, APIs, configuration, UI instructions, architecture claims, examples, or other exact technical material.

## Establish the source of truth

Use the most authoritative available evidence for each claim:

1. User-approved requirements or contractual specifications.
2. Project-specific documentation and established terminology.
3. Executable behavior in code, tests, schemas, configuration, generated reference, or observed output.
4. Maintainer decisions in accepted issues, pull requests, ADRs, or release records.
5. Current official external documentation for third-party behavior.

Do not treat comments, stale examples, issue proposals, branch names, or unmerged code as established product behavior without context.

When sources disagree, surface the conflict or choose the higher-authority source. Do not silently synthesize a plausible answer.

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
- Test runnable samples when tools and environment permit. Otherwise state the validation limit internally and avoid claiming they were tested.

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

For the applicable surface, document:

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

For each setting, document the facts readers need to choose and operate it:

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

- **Observed:** verified in code, configuration, tests, runtime evidence, or accepted documentation.
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

- Link to authoritative sources.
- Use descriptive link text that states the destination.
- Verify that the label matches the destination.
- Disclose unexpected downloads, sign-in requirements, or application launches when useful.
- Prefer an original summary and link over copied prose, code, screenshots, or diagrams.
- Preserve required licenses and attribution.
- Do not assume public or open-source material can be copied without conditions.

## Docstrings and comments

- Describe public behavior, contracts, side effects, failure conditions, and non-obvious rationale.
- Do not repeat names and types without adding meaning.
- Do not explain obvious syntax.
- Keep comments synchronized with the code.
- Prefer a test or clearer code over a comment that attempts to compensate for ambiguous behavior.
- Explain unusual workarounds, including the condition that permits their removal.
