# Output-quality evaluation cases

Use these cases to compare skill versions. Run the same prompt with and without the skill, or compare two skill versions blindly. Grade the actual output with evidence.

## Scoring rubric

Score each dimension from 0 to 2.

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Fidelity | Invents or changes technical meaning | Mostly accurate with minor unsupported drift | Preserves facts, uncertainty, literals, caveats, and scope |
| Reader orientation | Organized around author or system | Mixed reader and system orientation | Clear audience, job, and reader path |
| Clarity | Dense, vague, or hard to follow | Understandable with friction | Direct, precise, and easy to scan |
| Concision | Inflated or repetitive | Some removable material | Minimum complete document with no material repetition |
| Usability | Missing prerequisites, decisions, or verification | Partly actionable | Reader can act, decide, verify, and recover where relevant |
| Human quality | Template-like or AI-sounding | Unevenly natural | Natural technical prose without generic padding or bullet soup |

A strong output scores at least 10 of 12 with no zero in Fidelity or Usability.

## Case 1: README compression

Prompt:

> Rewrite this 1,200-word README for a small CLI. Keep installation, one working example, configuration, and support information. Remove anything a new user doesn't need.

Assertions:

- The opening states what the CLI does and when it is useful without repeating the title.
- Installation and first use appear before architecture or contribution details.
- No product behavior or commands are invented or silently changed.
- The output does not add generic benefits, key takeaways, FAQ, or conclusion sections.
- The result is materially shorter while preserving required support and configuration information.

## Case 2: Hidden conditions in a procedure

Prompt:

> Edit this deployment procedure. Several steps reveal conditions only at the end of the sentence, and there is no success check.

Assertions:

- Conditions and locations precede the actions they govern.
- Each step begins with a clear action and contains one primary action group.
- Destructive or irreversible effects are stated before the relevant action.
- The procedure ends with an observable verification step.
- Exact commands, flags, and UI labels remain unchanged unless the supplied source proves a correction.

## Case 3: Design document from evidence

Prompt:

> Use the attached code, issue discussion, and benchmarks to write a design document for changing the queue retry policy.

Assertions:

- Observed behavior, inferred risks, and the proposed policy are distinguishable.
- The proposal appears early and is not buried behind history.
- Goals, constraints, alternatives, failure modes, rollout, rollback, and open questions are included only when supported and relevant.
- Benchmark claims retain their configuration and scope.
- Unknowns remain unknown rather than being filled with plausible assumptions.

## Case 4: API reference

Prompt:

> Improve these endpoint descriptions. Preserve the schema and names exactly.

Assertions:

- Each entry begins with behavior rather than repeating the endpoint name.
- Parameters, defaults, response, errors, permissions, and side effects are easy to locate when supplied.
- Modality is precise; **should** is not used to hide requirements or expected behavior.
- Identifiers, field names, example values, and version labels remain exact.
- The output remains reference-like rather than becoming a tutorial or marketing page.

## Case 5: Troubleshooting under pressure

Prompt:

> Rewrite this page for an on-call engineer responding to `QUEUE_LAG_HIGH`.

Assertions:

- Impact, safety, and the first high-signal check appear before background.
- Diagnostics proceed from non-destructive evidence to more disruptive action.
- Commands state scope, expected output, and interpretation.
- Stop, escalation, recovery verification, and evidence-preservation conditions are present when supported.
- The page avoids vague steps such as “check the queue” or “restart if necessary.”

## Case 6: Minimal edit

Prompt:

> Fix the wording in the second section only. Do not change headings, anchors, commands, or British spelling.

Assertions:

- Only the requested section changes.
- British spelling and existing markup remain consistent.
- Headings, anchors, commands, and exact literals remain untouched.
- The edit improves clarity without adding new sections or unrelated reformatting.

## Case 7: Remove AI-writing patterns

Prompt:

> Make this generated architecture guide sound like a human wrote it. It repeats every point in an overview, bullets, key takeaways, and a conclusion.

Assertions:

- Repeated claims appear once in the most useful location.
- Generic openings, transition padding, and unsupported adjectives are removed.
- Bullets remain only where they improve comparison, sequence, or lookup.
- The architecture is organized around reader questions and decisions, not a module inventory.
- Necessary tradeoffs and caveats survive the compression.

## Case 8: Accessible UI instructions

Prompt:

> Rewrite these UI steps so they work without the screenshot. The current text says “click the blue button on the right.”

Assertions:

- Controls are named by exact visible or accessible labels.
- The instructions do not rely on color, position, shape, or pointer-only interaction.
- The page or dialog is named before the action when necessary.
- Results are stated where they help the reader continue.
- The screenshot becomes supplementary rather than essential.

## Grading notes

For every assertion, record PASS or FAIL and cite the relevant output text. Do not grade by impression alone. For version comparisons, hide which version produced each output and add a holistic preference judgment after assertion grading.
