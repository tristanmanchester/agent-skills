---
name: agent-use
description: >-
  Audit or design agent-facing product capabilities: action/context parity,
  discoverable contracts, safe mutations, verifiable outcomes, and recovery.
  Use for explicit agent-readiness reviews of apps, repos, CLIs, APIs, MCP/A2A
  integrations, or Agent Skills; not every general code or documentation task.
license: MIT
compatibility: Local helper scripts require Python 3.10+; structural validation also requires PyYAML 6.0.3 or later in major 6. Network and execution checks need separately authorised tools and environments.
metadata:
  version: "3.0.0"
  reviewed: "2026-09-13"
---

# Agent-useful products

Start with real tasks, not a checklist of fashionable protocols. Retain the core
method: action parity, context parity, stable object identity, bounded outputs,
verification, and recovery. A documented capability is not an implemented one;
a directory of manifests is not evidence that an agent can finish the task.

## Audit an existing surface

1. Select 5–10 representative tasks with expected outcomes, including a read,
   an authorised mutation, a denied operation, and interrupted-work recovery.
2. Map each task's necessary context, object IDs, available action, permission,
   success evidence, and retry/resume path. Use the noun test: discover, identify,
   read, change where appropriate, verify, recover.
3. Inspect source/contracts, then execute only the authorised checks. Record
   whether each observation is a source signal, documented claim, or runtime proof.
4. Compare the human and agent paths. Preserve intentionally human-only consent,
   MFA, CAPTCHA, and biometric boundaries; do not score bypassing them as parity.
5. Prioritise demonstrated blockers and test the proposed repair on the same tasks.
   Report unresolved evidence rather than turning missing tool access into a failure.

Use [the report template](references/report-template.md),
[architecture methods](references/agent-native-architecture.md), and
[evaluation guidance](references/evaluation.md) as needed. The retained local/web
scanners and scoring rubric are heuristic inventory aids, not protocol validators
or measured agent-success scores. A missing optional discovery convention is not
an interoperability defect without a consumer that actually requires it.

## Design the smallest useful contract

Prefer the surface already native to the product. A small CLI may need help,
structured output, and explicit exit codes, not an A2A server. An HTTP integration
may need its current OpenAPI contract and SDK, not a parallel handwritten client.
Use a workflow-level operation when it owns atomicity or a real server-side job;
otherwise expose composable operations with identifiable results.

For writes, define what happens after timeout, partial success, concurrent edits,
and repeated delivery. Request IDs are not automatically idempotency keys. Keep
confirmed outcomes separate from unknown outcomes, and define the retention/scope
of any deduplication guarantee. A preview or hash cannot authorise additional work.
Long-running tasks need durable IDs, explicit terminal states, and bounded waits;
local cancellation is not proof remote work stopped.

Read [web/discovery contracts](references/web-and-docs-readiness.md) or
[API/MCP/A2A contracts](references/api-sdk-mcp-readiness.md) for the chosen surface.
The A2A example now targets protocol 1.0; `/.well-known/mcp.json` and the bundled
skills index are local design examples, not universal standards. A2A skills are
protocol capability descriptions, not filesystem Agent Skills packages.

## Inspect a skill without executing it

Resolve `SKILL_DIR` to the installed directory containing this file. Paths below
are skill-relative, not scripts expected in the target repository.

```bash
python "$SKILL_DIR/scripts/validate_agent_assets.py" --skill-dir /absolute/path/to/skill
```

Install the declared PyYAML dependency in an authorised environment first, or run
the implementation file with a PEP 723-aware runner. Validation parses real YAML,
checks required fields, JSON/Python syntax, and conventional relative Markdown
links. It does not execute scripts, write bytecode, contact services, validate
complete protocol schemas, or evaluate whether the skill improves agent behaviour.
The old `--run-help` and `--py-compile` modes are removed. Running even `--help`
can execute arbitrary project code; do that separately only after trust review.

See [skill/instruction checks](references/agent-instructions-and-skills.md).
Optional directories are optional, not automatic quality failures. Prefer current
commands and useful examples rather than retaining aliases solely for compatibility.

## Generate drafts, not deployed discovery endpoints

```bash
python "$SKILL_DIR/scripts/generate_agent_assets.py" \
  --output /private/existing-parent/new-drafts --project-name "Example" \
  --base-url https://example.com --surface a2a
```

This previews without creating directories. Select each surface explicitly;
add `--write` only to create a new private draft directory. Existing paths are
never overwritten. The final manifest marks completion; an interrupted write can
leave a partial directory. No `--force`, default `all`, live `.well-known` publication,
or automatic replacement of a project's AGENTS.md remains.

Review generated placeholders and validate the protocol with the actual chosen
SDK/schema before publication. Declare only implemented capabilities and enforced
authentication. The A2A fixture uses HTTP+JSON, a real service endpoint separate
from the card URL, and a bearer-auth declaration that the server must implement.

## Maintenance evidence

Run `python -m unittest discover -s "$SKILL_DIR/tests" -v` for local regression
checks. The new fixture tests cover scaffold/validator behaviour and selected A2A
shape regressions, not full A2A or MCP conformance. Preserve the substantive domain
references, evaluation seeds, capability maps, and existing MIT licence.

Reviewed 2026-09-13 against [Agent Skills](https://agentskills.io/specification),
[authoring guidance](https://agentskills.io/skill-creation/best-practices),
[A2A 1.0](https://a2a-protocol.org/latest/specification/), and
[RFC 9727](https://www.rfc-editor.org/rfc/rfc9727.html).
