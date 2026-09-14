# Evaluate these scenarios

`scenarios.json` is a manual agent-trace evaluation set, not executable tests.
For each `cases` entry, run the `prompt` in an isolated representative integration
fixture and assess the trace/output against `expect`. Record the model, skill
revision, fixture, observed behaviour, and pass/fail rationale; include a no-skill
comparison when measuring improvement. Do not make live sends or trigger customer
Automations as part of a fixture.

There is no repository-wide runner that discovers this file, and no model-output
results are bundled. A JSON parse checks the fixture structure, not the expected
behaviour. Individual skills may have their own unrelated evaluation formats.
