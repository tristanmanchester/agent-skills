#!/usr/bin/env python3
"""Expected value of an explicitly supplied scenario model, not estimated probabilities."""
from decimal import Decimal
from _decision_math import cli, number, name, object_keys, unique_rows, finite_float

def compute(data):
    object_keys(data, {'unit', 'scenarios'}, {'horizon'})
    name(data['unit'], 'Unit')
    if 'horizon' in data:
        name(data['horizon'], 'Horizon')
    contributions = []
    probability_sum, expected, loss_probability = Decimal(0), Decimal(0), Decimal(0)
    possible = []
    for scenario in unique_rows(data['scenarios'], 1):
        object_keys(scenario, {'name', 'probability', 'value'})
        probability = number(scenario['probability'], 'Probability')
        value = number(scenario['value'], 'Value')
        if not 0 <= probability <= 1:
            raise ValueError('Probabilities must be between zero and one')
        probability_sum += probability
        term = probability * value
        expected += term
        if value < 0:
            loss_probability += probability
        if probability > 0:
            possible.append(value)
        contributions.append({**scenario, 'contribution': finite_float(term)})
    if abs(probability_sum - 1) > Decimal('1e-9'):
        raise ValueError('Scenario probabilities must sum to one (absolute tolerance 1e-9); no automatic renormalisation')
    return {'model': 'supplied-discrete-scenarios', 'unit': data['unit'], 'horizon': data.get('horizon'),
            'probability_sum': finite_float(probability_sum), 'expected_value': finite_float(expected),
            'loss_probability': finite_float(loss_probability),
            'worst_positive_probability_value': finite_float(min(possible)),
            'best_positive_probability_value': finite_float(max(possible)), 'scenarios': contributions,
            'note': 'Requires mutually exclusive, exhaustive scenarios on a common net-value basis. Expected value does not establish affordability, utility, or acceptable ruin risk.'}

if __name__ == '__main__':
    raise SystemExit(cli(compute, __doc__))
