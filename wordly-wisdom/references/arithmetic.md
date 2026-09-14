# Arithmetic contracts

## Fixed-anchor additive utility

Supply criteria with nonnegative weights and explicit `worst`/`best` anchors,
chosen independently of the alternatives being compared. Lower-is-better simply
has best < worst. Each score must lie between its anchors; the helper rejects
out-of-range values rather than silently clipping or rescaling.

```json
{
  "criteria": {
    "quality": {"weight": 0.6, "worst": 0, "best": 10},
    "cost": {"weight": 0.4, "worst": 10, "best": 0}
  },
  "options": [
    {"name": "A", "scores": {"quality": 10, "cost": 10}},
    {"name": "B", "scores": {"quality": 5, "cost": 5}}
  ]
}
```

Utility is `(score - worst) / (best - worst)`. Weights are normalised by their
positive total. Each weight therefore values a **full swing between its anchors**,
not merely the label 'importance'. A linear utility function is an explicit model
assumption; threshold/saturation effects need a different model or prior conversion
to justified utilities. This additive model also assumes tradeoffs can be combined
in this way. Do not double-count the same benefit under correlated criteria.

The old option-dependent normalisation changed tradeoffs when an alternative was
added. For quality/cost with weights .6/.4, A=(10,10), B=(5,5), adding C=(0,6)
(dominated by B) flipped A/B under the old scaling. Fixed anchors preserve their
existing scores. That removes this mathematical instability, not all possible
errors in the user's decision model.

Apply hard constraints before the matrix. Inspect sensitivity to weights, anchors,
and scores; never use the top gap as a confidence interval. Ties or rounded-near-
ties need interpretation, not a fabricated precise winner. The sample data are
illustrative ratings, not measurements or advice about the user's employment.

## Discrete scenario expected value

Supply a nonempty uniquely named scenario list with finite numeric probabilities
between zero and one, finite net values, and a common unit. Probabilities must sum
to one within an absolute tolerance of 1e-9. The helper returns the actual sum and
does not automatically renormalise an incomplete probability model.

```json
{
  "unit": "GBP", "horizon": "one year",
  "scenarios": [
    {"name": "Win", "probability": 0.25, "value": 100},
    {"name": "Loss", "probability": 0.75, "value": -20}
  ]
}
```

These inputs yield EV=10 GBP and loss probability=.75. They must describe mutually
exclusive, exhaustive scenarios on the same cost/net-value basis and horizon.
The script does not establish those assumptions. It excludes zero-probability
rows from the named positive-probability extrema, but keeps their original rows.
Unmodelled outcomes, fat tails, dependence, liquidity, and utility can dominate EV.

Both helpers validate when called through `compute`, not just via CLI. Decimal
intermediates reduce avoidable overflow/cancellation from ordinary float scaling;
JSON outputs are finite floats, not arbitrary-precision or accounting guarantees.
Input counts and sizes are bounded. Output goes to stdout; when saving it, choose
a private new filename and do not overwrite another model or source file.

## Regression versus real validation

`python -m unittest discover -s "$SKILL_DIR/tests" -v` exercises invalid inputs,
fixed-anchor invariance, direction, finite ranges, arithmetic, and CLI failure.
It does not validate the chosen scenario probabilities, utilities, sources, or
future outcomes. For a real decision, retain the supplied assumptions and compare
recommendations under plausible alternatives.
