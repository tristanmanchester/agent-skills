# Evaluate the skill

This directory contains 20 self-contained fictional writing cases and 32 routing probes. It does not contain a completed model benchmark. The tools below use only the Python standard library, make no network requests, and do not execute commands quoted in fixtures.

## Export a case

From the `write-good-docs` directory, with Python 3.10 or later:

```sh
python3 scripts/evaluate.py list
python3 scripts/evaluate.py prepare --case Q03 --out /tmp/docs-eval-q03
```

Choose a fresh output directory; `prepare` refuses to overwrite an existing path. It creates `task.md` containing only the prompt and source material, not the expected answer or rubric. Provide that file to a clean model context and save its answer as `output.md` outside the skill directory.

Use the same exported task for no-skill, v2.0.0, and v2.1.0 runs. For skill runs, make only that version's `SKILL.md` and `references/` available and explicitly activate it. Do not expose `evals/` or the full maintenance package to the writer. The no-skill writer gets neither version. Keep model settings and tool permissions constant.

All product names, commands, source labels, and measurements in fixtures are fictional test data. Do not browse for missing product facts. For Q14, keep execution disabled or use an instrumented harmless sandbox; never give a test access to real production resources. Check the trace for attempted operations even if an operation was blocked.

## Check mechanical constraints

```sh
python3 scripts/evaluate.py check --case Q03 --output /tmp/docs-eval-q03/output.md
```

The command emits JSON. Exit code 0 means the applicable **mechanical** checks passed, 1 means one failed, and 2 means an input or configuration error. Every result explicitly requires semantic review. Presence of a number or command cannot establish that its meaning or safety context was preserved.

The checks cover protected literals, exact warning counts/order, a deliberately unchanged paragraph, a local edit boundary, requested heading restrictions, and explicit word caps where applicable. Word caps use whitespace-delimited tokens; they are checks of a requested limit, not a universal concision target. Line endings and trailing newlines are normalized for exact comparisons; internal content and outside-section spacing are preserved.

## Grade meaning and usefulness

Apply the universal and case-specific gates in [the quality rubric](quality-cases.md) and [case definitions](evals.json). Record evidence before a holistic preference. A semantic failure overrides a mechanical pass and any high style score. Source-command execution requires trace inspection; the answer alone is insufficient.

For each run, record case ID, fixture identity, condition, model/settings, package identity, available tools, observed reference loads, available timing/token data, output path, hard-gate decisions, assertion decisions, quality scores, and reviewer. Use null or "unavailable" for missing telemetry.

Blind the condition labels and randomize output order for comparisons. Allow ties. Run fresh held-out tasks after using these exposed regression cases to revise the skill. See [the full comparison protocol](quality-cases.md) and [routing probes](trigger-cases.md).

## Maintain the fixtures and scripts

```sh
python3 scripts/check_package.py
python3 -m unittest discover -s evals/tests -v
```

The first command checks package structure, local Markdown targets, fixture/check schemas, and the manifest when present. The second tests the mechanical checker, export isolation, and error handling against handcrafted outputs and mutations. Neither runs an LLM or grades prose quality.
