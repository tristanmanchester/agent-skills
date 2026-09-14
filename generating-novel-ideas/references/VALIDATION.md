# Validation

## Local helper tests

From this skill directory run:

```bash
python -m unittest discover -s tests -v
```

These cover parsing, input bounds, token handling, and lexical candidate reporting.
They do not evaluate the novelty, feasibility, or usefulness of generated ideas.

## Agent evaluations to run separately

Compare complete traces with and without the skill for substantial product,
scientific, campaign, naming-only, and process-redesign requests. Include a weak
existing concept, conflicting constraints, and a request for exactly one idea.

Check whether the output addresses the actual brief; explores distinct mechanisms
when exploration is needed; grounds current facts; separates proposals from evidence;
handles the strongest objection; and proposes an ethical test tied to an assumption.
Do not grade adherence to a fixed number of headings, personas, or contrast sentences.

Negative routing cases include proofreading, translation, summarising supplied
text, factual lookup, and implementing an exact specification. A naming-only task
should not trigger unsolicited product redesign. Same-context passes must not be
reported as independent blind agent runs. A lexical-overlap score must not be
reported as scientific or commercial novelty evidence.

Save the prompts, versions, outputs, reviewer judgements, and unresolved disagreements.
The existence of these scenarios is not a claim that an agent evaluation has run.
