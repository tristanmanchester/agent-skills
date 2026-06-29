# Agent-use audit report template

# Agent-use audit: <target>

Overall: <score>/100 (<grade>)
Date: <date>
Reviewer: <name/agent>
Surfaces reviewed: <repo/docs/CLI/API/SDK/MCP/UI/files/skill>
Surfaces not reviewed: <limits>

## Executive summary

<3-7 sentences. State the main strengths, biggest blockers, and highest-leverage fixes.>

## Applicability

| Surface/dimension | Applies? | Why |
| --- | --- | --- |
| Web/docs | yes/no | <reason> |
| CLI/TUI | yes/no | <reason> |
| API/SDK | yes/no | <reason> |
| App UI | yes/no | <reason> |
| Tools/MCP/A2A | yes/no | <reason> |
| Files/workspace | yes/no | <reason> |

## Scores

| Dimension | Applicable | Score | Evidence | Main gap |
| --- | --- | ---: | --- | --- |
| Discoverability | yes/no | 0-10 | <file/url/command> | <gap> |
| Content readability | yes/no | 0-10 | <file/url/command> | <gap> |
| Capability contracts | yes/no | 0-10 | <file/url/command> | <gap> |
| Action parity | yes/no | 0-10 | <file/url/command> | <gap> |
| Context parity | yes/no | 0-10 | <file/url/command> | <gap> |
| Parseable outputs | yes/no | 0-10 | <file/url/command> | <gap> |
| Safety/recovery | yes/no | 0-10 | <file/url/command> | <gap> |
| Evals/maintenance | yes/no | 0-10 | <file/url/command> | <gap> |

## Action/context parity map

| Human capability | Human context | Agent-readable context | Agent action path | Safety level | Recovery path | Gap |
| --- | --- | --- | --- | --- | --- | --- |
| <workflow> | <UI state> | <endpoint/file/tool> | <command/API/tool> | <level> | <undo/status> | <gap> |

## Findings

### Critical

1. **<Issue>** — `<evidence>` — Impact: <impact>. Fix: <patchable recommendation>. Acceptance test: <test>.

### High / Medium / Low

<Repeat as needed.>

## Top remediation plan

### 0-2 days

1. <Fix, owner, acceptance test>

### 2-7 days

1. <Fix, owner, acceptance test>

### 7-30 days

1. <Fix, owner, acceptance test>

## Evals to add

| Task | Current failure mode | Passing condition |
| --- | --- | --- |
| <task> | <failure> | <assertion> |
