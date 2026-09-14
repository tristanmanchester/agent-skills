#!/usr/bin/env python3
"""Weighted utility with explicit fixed best/worst anchors; no option-set scaling."""
from decimal import Decimal
from _decision_math import cli, number, name, object_keys, unique_rows, finite_float

def compute(data):
    object_keys(data, {'criteria', 'options'})
    criteria = data['criteria']
    if not isinstance(criteria, dict) or not 1 <= len(criteria) <= 100:
        raise ValueError('Expected 1 to 100 criteria')
    parsed = {}
    for key, criterion in criteria.items():
        name(key, 'Criterion name')
        object_keys(criterion, {'weight', 'worst', 'best'})
        weight = number(criterion['weight'], 'Weight')
        worst, best = number(criterion['worst'], 'Worst anchor'), number(criterion['best'], 'Best anchor')
        if weight < 0 or worst == best:
            raise ValueError('Weights must be nonnegative and anchors distinct')
        parsed[key] = (weight, worst, best)
    total = sum((v[0] for v in parsed.values()), Decimal(0))
    if total <= 0:
        raise ValueError('At least one weight must be positive')
    ranking = []
    for option in unique_rows(data['options'], 2):
        object_keys(option, {'name', 'scores'})
        scores = option['scores']
        if not isinstance(scores, dict) or set(scores) != set(parsed):
            raise ValueError('Each option must supply exactly the declared criteria')
        contributions = {}
        utility = Decimal(0)
        for key, (weight, worst, best) in parsed.items():
            raw = number(scores[key], 'Score')
            if not min(worst, best) <= raw <= max(worst, best):
                raise ValueError('Score lies outside its fixed anchors; review the model, do not clip silently')
            scaled = (raw - worst) / (best - worst)
            contribution = (weight / total) * scaled
            utility += contribution
            contributions[key] = {'raw': finite_float(raw), 'utility': finite_float(scaled),
                                  'weighted_contribution': finite_float(contribution)}
        ranking.append({'name': option['name'], 'total': finite_float(utility), 'contributions': contributions})
    ranking.sort(key=lambda row: row['total'], reverse=True)
    return {'model': 'fixed-anchor-additive-utility',
            'weights_normalized': {k: finite_float(v[0] / total) for k, v in parsed.items()},
            'criteria': criteria, 'ranking': ranking,
            'note': 'Utilities and weights are assumptions, not probabilities. Check sensitivity, hard constraints, and correlated criteria.'}

if __name__ == '__main__':
    raise SystemExit(cli(compute, __doc__))
