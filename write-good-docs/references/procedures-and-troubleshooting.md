# Procedures and troubleshooting

Read this reference for tutorials, how-to guides, numbered steps, runbooks, troubleshooting, incident response, optional branches, destructive actions, and verification.

## Before the steps

State only what the reader needs before acting:

- the goal;
- applicability conditions;
- prerequisites, permissions, tools, versions, and cost implications;
- data-loss, outage, security, or irreversible effects;
- where the action takes place when that is not obvious.

Do not repeat the heading in an introductory sentence. A procedure can begin immediately when the heading and context already establish the task.

## Step design

- Use numbered steps only when order matters.
- Write a one-action task as a sentence or bullet, not a one-item numbered procedure.
- Begin each step with an imperative action.
- Keep one primary action or tightly coupled action group per step.
- Put the location and condition before the action: “In the **Settings** page, select **Delete project**.”
- Put a step's goal before the action when it helps: “To preserve the existing key, export it before rotation.”
- Put the result after the action when it helps the reader navigate: “Select **Run**. The results appear in the output pane.”
- Explain placeholders immediately after the code or command in appearance order.
- Keep justifications brief and next to the action they justify.
- Use substeps only for genuinely subordinate actions. Split long or branching work into separate procedures when that is easier to follow.
- Mark optional steps at the beginning: “Optional: ...”
- State whether a set of alternatives means choose one, complete all, or complete every applicable option.

Do not write vague steps such as “Configure the service correctly,” “Ensure the database is healthy,” or “Handle the error.” Name the setting, evidence, command, expected state, or decision rule.

## Conditions and branches

Conditions belong before the action they govern:

- “If the deployment uses a private network, create the endpoint before you continue.”
- Not: “Create the endpoint before you continue if the deployment uses a private network.”

For branches:

1. Start with an observable condition.
2. Give the action for that condition.
3. State the expected result or next branch.
4. Rejoin the main path when possible.

Prefer short named subsections over deeply nested numbered lists.

## Commands and output inside steps

Use this order when applicable:

1. State the action.
2. Show the command.
3. Define placeholders.
4. Explain non-obvious behavior or flags.
5. Show representative output.
6. Explain how to interpret the output.

A click-to-copy command must be runnable. Do not include a shell prompt, optional-syntax brackets, explanatory ellipses, or comments that make the command invalid.

## Verification

A procedure is not complete merely because the commands end.

Tell the reader how to verify the intended result through an observable signal such as:

- a status value;
- a query result;
- a file or resource state;
- a health endpoint;
- a log event;
- a UI confirmation;
- a test or dry run.

Use specific success criteria. “Verify that it works” is not enough.

For consequential changes, include rollback or cleanup. State when rollback is unavailable or only partially restores the earlier state.

## Warnings and destructive actions

Place a warning immediately before the action it protects. Include:

- what can happen;
- what scope is affected;
- whether the action is reversible;
- the prerequisite backup, approval, or confirmation;
- a safer alternative when one exists.

Do not dilute serious warnings with routine notes. Do not put a warning after the destructive command.

## Tutorials

A tutorial should create a controlled learning experience:

- use known inputs and a reproducible environment;
- follow one path;
- avoid optional complexity;
- give checkpoints that confirm the learner is on track;
- explain concepts at the moment they become useful;
- end with a working result and safe cleanup.

The tutorial author is responsible for preventing avoidable failure. Do not require production credentials, irreversible changes, or uncontrolled cost.

## How-to guides

A how-to guide assumes a competent reader who has a real goal:

- start near the task, not at first principles;
- focus on action and decision points;
- cover realistic conditions and branches;
- prefer practical usability over exhaustive product reference;
- link to concepts and reference instead of embedding long digressions.

## Troubleshooting

Write from symptoms to evidence to action.

### Structure

For each issue, include the relevant parts:

1. **Symptom.** Exact error text, alert, failed state, or observable behavior.
2. **Applicability.** Versions, configurations, or conditions where the issue occurs.
3. **Diagnostic check.** The safest, quickest evidence that separates likely causes.
4. **Interpretation.** What each result means.
5. **Resolution.** A scoped corrective action.
6. **Verification.** Evidence that the issue is resolved.
7. **Escalation.** What to collect, when to stop, and who or what to contact.

### Diagnostic order

- Begin with non-destructive and high-signal checks.
- Prefer evidence over speculative cause lists.
- Do not ask the reader to restart, delete, rotate, or migrate before collecting evidence that might be lost.
- State expected output or a comparison point.
- Distinguish “not found,” “permission denied,” “timeout,” and “unhealthy” instead of grouping them as a generic failure.
- When multiple causes share a symptom, use a decision tree or table only if it is easier to follow than prose.

## Runbooks and incident response

Under pressure, the operator needs direct decisions, not background.

- Put impact, safety, and immediate containment first.
- State required role, account, region, environment, and change-approval conditions.
- Make every command's scope visible.
- Identify commands that are read-only, mutating, destructive, or expensive.
- Include stop conditions and escalation thresholds.
- Preserve evidence before actions that alter logs, queues, processes, or data.
- State how to verify service recovery and how long stabilization can reasonably take when known.
- Separate temporary mitigation from permanent remediation.
- Capture follow-up work outside the urgent response path.

## Reuse and standalone safety

Avoid copying the same procedure into several pages. Link to one maintained source of truth.

However, repeat the minimum context required when:

- readers commonly enter at that step from search;
- the warning must travel with the action;
- a standalone runbook section would otherwise be unsafe;
- a cross-reference could be unavailable during an incident.
