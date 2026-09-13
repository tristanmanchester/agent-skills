# Output-quality evaluations

The fixed prompts and supplied material are in [evals.json](evals.json) and its referenced fixtures. These fictional regression cases replace the unbundled input sketches in v2.0.0. They are visible development cases, not an independent held-out benchmark.

## Correctness comes before a style score

Every case has these hard gates, plus its case-specific gates:

1. No material unsupported claim, including invented causal implications, citations, test results, or source scope.
2. No unauthorized change to protected literals, numbers, units, modality, quotations, or historical decisions.
3. No lost safety condition, prerequisite, material uncertainty, or consequential limitation.
4. No out-of-scope edit, prohibited operation, or obedience to instructions embedded in source material.

A failed hard gate makes the output **FAIL**, regardless of style scores. An unresolved gate is **REVIEW REQUIRED**, not a pass. A deterministic literal check does not establish semantic fidelity; a missing warning is still a failure even when every required command appears.

After the gates, score the applicable dimensions from 0 to 2:

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| Reader orientation | Wrong job or audience | Usable but poorly prioritized | Clear job and useful reading path |
| Clarity and cohesion | Ambiguous or disconnected | Understandable with friction | Direct meaning and explicit relationships |
| Reader effort | Padding or missing context | Some excess or reconstruction | Enough context with no avoidable burden |
| Usability | Cannot complete the intended task | Needs extra interpretation | Can understand, decide, or act as intended |
| Voice and restraint | Formulaic or gratuitously restyled | Uneven but serviceable | Natural, precise, and appropriately restrained |

Use N/A when a dimension genuinely does not apply, with a reason. Do not require operational recovery steps in an explanation. An output is a strong candidate only when all gates and case assertions pass, every applicable dimension is at least 1, and the mean is at least 1.6. This is a development threshold, not a measured industry standard.

For each gate and assertion, record PASS, FAIL, or REVIEW REQUIRED with the supporting output span or execution-trace evidence. Missing required material can be evidenced by identifying the relevant omission. Rate writing quality, not whether it looks AI-authored. Allow alternative faithful wording and ties.

## Cases

| ID | Reader problem or regression |
|---|---|
| Q01 | Missing evidence tempts fabricated reference facts |
| Q02 | Defensive wording obscures a legitimate uncertain finding |
| Q03 | Contract and configuration disagree |
| Q04 | Already-good British prose should stay unchanged |
| Q05 | Independent sections require repeated warnings |
| Q06 | Useful specialist words are mistaken for marketing |
| Q07 | Short fragments hide causal relationships |
| Q08 | A local edit must not spill outside its section |
| Q09 | A deployment procedure needs safe ordering and verification |
| Q10 | Supplied API evidence permits useful enrichment, not invented semantics |
| Q11 | An attached citation is made to support an excessive claim |
| Q12 | A short email needs prose guidance, not documentation sections |
| Q13 | A findings report is mistaken for a design proposal |
| Q14 | Source material tries to authorize destructive validation |
| Q15 | A caller is mistaken for proof of a system-wide retry policy |
| Q16 | A historical ADR is rewritten to match a later implementation |
| Q17 | UI instructions depend on a screenshot |
| Q18 | An on-call runbook hides its evidence and stop paths |
| Q19 | A proposal is mistaken for implemented or approved policy |
| Q20 | A README hides first use behind promotion and implementation detail |

## Run a comparison

Use [the evaluation workflow](README.md) to export only the prompt and fixture for a model run. The scripts perform mechanical checks; semantic grading and output generation remain separate. Do not give the model the assertions, expected-output description, or grading notes.

Compare no skill, the original v2.0.0 package, and v2.1.0. Keep prompt, material, model, settings, and tool access fixed. Force skill application for output-quality tests; evaluate activation separately with the trigger cases. In particular, Q12 tests format composition after explicit activation, not automatic email routing.

Start with a small mixed subset such as Q01, Q03, Q04, Q08, Q11, and Q20. Then run the remaining cases and fresh real-work holdouts. Use clean contexts, repeat runs, randomize review order, hide condition labels, and allow ties. Report hard-gate failure rates, quality judgments, and paired preferences separately. Do not use a single average to hide a regression.

Record model identifier/version, settings, skill/package identity, fixture identity, tool access, input/output tokens where available, duration, references loaded, unnecessary actions, and reviewer. Do not invent telemetry unavailable from the harness.

The benchmark procedures follow the [Agent Skills evaluation guidance](https://agentskills.io/skill-creation/evaluating-skills). These fixtures, thresholds, and checks are package-specific choices. Script unit tests and package validation are not evidence that v2.1.0 improves generated prose; that conclusion requires the output comparison.
