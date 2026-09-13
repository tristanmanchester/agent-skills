---
name: wordly-wisdom
description: >-
  Analyse consequential choices with outside views, incentives, inversion,
  scenario arithmetic, opportunity costs, and explicit update conditions. Use
  for decision memos, premortems, strategy choices, or a requested red-team;
  not routine factual questions or a reason to overanalyse a small decision.
license: MIT
compatibility: Core reasoning needs no special tools. Optional arithmetic helpers require Python 3.10+ and use only the standard library. Time-sensitive or specialised claims require current relevant sources.
metadata:
  version: "4.0.0"
  reviewed: "2026-09-13"
  source-book: "Poor Charlie's Almanack"
---

# Disciplined decision analysis

Help the user make a defensible choice, not admire an oracle. Preserve the useful
Munger-inspired methods: multiple models, an outside view, incentives, inversion,
margin of safety, and separation of process quality from outcome luck. These are
reasoning lenses, not a substitute for evidence or a universal scoring formula.

## Frame the choice

Read the available context first. Identify the decision, objective, horizon,
options, constraints, affected people, and what would count as success. Include
do-nothing/defer/learn-first when they are real alternatives. Infer ordinary
defaults explicitly and proceed; ask only about a consequential unresolved fact
that cannot be established from the supplied evidence.

Match depth to stakes and the requested deliverable. A quick take can be a
recommendation, its decisive reason, main risk, and next step. A decision memo
can use the existing [memo template](assets/oracle-decision-memo-template.md).
Do not impose a fixed count of models, questions, headings, or psychological
explanations on every answer.

## Test the case before ranking it

Establish the outside view when a meaningful comparison class exists. State the
class, denominator, selection/survivorship limits, and sources; do not invent a
base rate to complete a template. Check current prices, rules, products, and
technical limits before using them as facts. A lack of retrieval is a known gap,
not evidence the world has not changed.

Build the inside view from mechanisms, dependencies, costs, time, and opportunity
cost. Use only the models that materially change the decision. Explain the link
between a model and its conclusion. Do not use a bias label to diagnose the user
or assume an absent stakeholder's motives. Incentives suggest hypotheses about
behaviour; they do not prove intent.

First enforce hard constraints and unacceptable downside. A weighted average
cannot compensate for a violated safety, legal, resource, or ethical requirement.
Then compare the feasible options. Look for dominated options, correlated criteria,
fragile assumptions, and plans whose upside depends on several uncertain events
all succeeding. Test the strongest case for and against the leading option.

## Use arithmetic without manufacturing certainty

Read [arithmetic contracts](references/arithmetic.md) before using the helpers.
They calculate a supplied model; they do not estimate probabilities or make the
recommendation. Utility weights, scales, scores, and scenario probabilities need
stated provenance or an explicit assumption label.

Resolve SKILL_DIR to this installed directory, not the target project's scripts:

```bash
python "$SKILL_DIR/scripts/decision_matrix.py" --input /private/model.json
python "$SKILL_DIR/scripts/ev_scenarios.py" --input /private/scenarios.json
```

Both emit JSON on stdout and errors/nonzero status on failure. Inputs are bounded
at 1 MiB; booleans, numeric strings, NaN/Infinity, duplicate keys, and malformed
models are rejected. The matrix now requires fixed best/worst utility anchors,
not min-max scaling from whichever options happen to be listed. The old matrix
schema and Markdown/output flags are removed, with no compatibility conversion.

Vary the decisive assumptions and show when the recommendation reverses. A tiny
score gap is not statistical confidence; a positive expected value does not make
a loss affordable. Keep units, net/gross basis, time horizon, liquidity, downside,
and dependencies explicit. Missing values stay unknown, not zero or a convenient
middle score. Do not adjust weights merely to recover a preferred winner.

## Invert and decide

Ask how the leading plan could fail, what evidence contradicts it, who bears the
loss, and what can be learned before an irreversible commitment. Distinguish
reversible experiments from obligations that continue after the experiment ends.
Choose a cheap test only when it can resolve a consequential uncertainty.

Make a recommendation or identify the genuine unresolved tradeoff. State the
critical assumption, strongest reason, main failure mode, and specific evidence
that would change the view. Probability statements need an event and resolution
date; subjective confidence in advice is not that probability. Record forecasts
before outcomes are known using the [ledger](assets/forecast-ledger-template.md).

Do not imply future monitoring or reminders exist because an update condition is
written in a memo. Establish a scheduler or owner only when authorised and actually
available. Advice to investigate, transact, hire, invest, or contact someone is not
permission to execute it.

## Targeted references

- [Model latticework](references/model-latticework.md): selecting relevant lenses.
- [Misjudgment](references/misjudgment-playbook.md): incentives and bias hypotheses.
- [Checklists](references/decision-checklists.md): domain-specific questions.
- [Examples](references/use-cases-and-examples.md): adapted reasoning patterns.
- [Arithmetic](references/arithmetic.md): matrix/scenario assumptions and limits.
- [Portability](references/portability-and-adaptation.md): available tools/evidence.

The longer operating-system and memo assets remain a menu for substantial work,
not a requirement to reproduce their whole structure. Keep conclusions connected
to the user's actual decision and sources. No controlled decision-quality or
agent-output improvement is claimed from this revision.
