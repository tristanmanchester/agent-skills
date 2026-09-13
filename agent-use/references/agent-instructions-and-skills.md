# Agent instructions and skills

Keep project instructions grounded in actual setup, architecture, checks, generated
files, data handling, and release boundaries. A generated AGENTS.md is a draft to
review, not permission to replace a project's established instructions.

For a skill, make the trigger precise, the default workflow short, and references
conditional on the task. Preserve useful tested helpers and examples; remove
unsupported flags and obsolete compatibility layers rather than teaching every
historical interface. Optional scripts/references/assets need not exist when the
skill does not require them.

Validate YAML with a real parser, including folded/literal descriptions, duplicate
keys, field limits, and string-valued metadata. Then inspect links and script syntax
without running project code. `--help` is executable code, not a trusted metadata
read. The structural validator does not prove provider compatibility or task success.

Evaluate positive and negative triggers and inspect complete agent traces on real
tasks. A JSON file containing evaluation prompts is a fixture, not a passing eval.
Measure the improvement relative to using no skill; tighten instructions around
observed failure modes rather than adding generic admonitions indefinitely.

Sources reviewed 2026-09-13:
[format](https://agentskills.io/specification) and
[authoring practice](https://agentskills.io/skill-creation/best-practices).
