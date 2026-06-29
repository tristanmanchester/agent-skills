# Agent instructions and skills

## AGENTS.md

A root `AGENTS.md` should tell coding agents how to work safely and effectively. Include project purpose, setup, tests, lint/build commands, architecture map, generated-file policy, secrets policy, style conventions, safe destructive boundaries, deployment rules, and escalation paths.

## llms.txt

For docs-heavy sites, `llms.txt` should be a concise markdown index of canonical current docs, not a giant dump. Include overview, quickstart, automation/agent guide, API/CLI/SDK references, auth/scopes, errors/retries, changelog, and examples.

## Agent Skills

A good Agent Skill has:

- Precise `description` trigger language.
- Compact `SKILL.md` with routing and workflow.
- Progressive disclosure through `references/`, `assets/`, and `scripts/`.
- Scripts with `--help`, non-interactive behavior, clear errors, and bounded output.
- Templates/schemas/evals that help agents act, not only prose.
- Versioning and backwards-compatible command names where practical.

## Skill audit checklist

- Does `SKILL.md` start with valid frontmatter?
- Does `name` match the directory and use lowercase hyphenated form?
- Is `description` specific enough for automatic invocation?
- Are referenced files present?
- Do scripts run with `--help`?
- Are evals present for trigger and output quality?
- Does the skill avoid hiding essential behavior in huge top-level prose?
