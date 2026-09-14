import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
sys.path.insert(0, str(Path(__file__).parents[1] / 'scripts'))
import decision_matrix as matrix
import ev_scenarios as ev
import _decision_math as common

def model():
    return {'criteria': {'quality': {'weight': .6, 'worst': 0, 'best': 10}, 'cost': {'weight': .4, 'worst': 10, 'best': 0}},
            'options': [{'name': 'A', 'scores': {'quality': 10, 'cost': 10}}, {'name': 'B', 'scores': {'quality': 5, 'cost': 5}}]}
def scenarios():
    return {'unit': 'GBP', 'scenarios': [{'name': 'win', 'probability': .25, 'value': 100}, {'name': 'lose', 'probability': .75, 'value': -20}]}

class DecisionTests(unittest.TestCase):
    def test_fixed_anchors_and_direction(self):
        rows = matrix.compute(model())['ranking']
        self.assertEqual([r['name'] for r in rows], ['A', 'B'])
        self.assertAlmostEqual(rows[0]['total'], .6); self.assertAlmostEqual(rows[1]['total'], .5)
    def test_dominated_addition_cannot_change_old_scores(self):
        data = model(); before = matrix.compute(data)['ranking']
        data['options'].append({'name': 'C', 'scores': {'quality': 0, 'cost': 6}})
        after = matrix.compute(data)['ranking']
        self.assertEqual(before, [r for r in after if r['name'] != 'C'])
    def test_negative_zero_and_invalid_weights(self):
        for bad in [-1, float('nan'), float('inf'), True, '0.6']:
            data = model(); data['criteria']['quality']['weight'] = bad
            with self.assertRaises(ValueError): matrix.compute(data)
        data = model()
        for v in data['criteria'].values(): v['weight'] = 0
        with self.assertRaises(ValueError): matrix.compute(data)
    def test_bounds_missing_fields_and_duplicate_names(self):
        data = model(); data['options'][0]['scores']['quality'] = 11
        with self.assertRaises(ValueError): matrix.compute(data)
        data = model(); del data['options'][0]['scores']['cost']
        with self.assertRaises(ValueError): matrix.compute(data)
        data = model(); data['options'][1]['name'] = 'A'
        with self.assertRaises(ValueError): matrix.compute(data)
    def test_zero_width_anchor_and_extra_fields(self):
        data = model(); data['criteria']['quality']['best'] = 0
        with self.assertRaises(ValueError): matrix.compute(data)
        data = model(); data['direction'] = {}
        with self.assertRaises(ValueError): matrix.compute(data)
    def test_large_finite_ranges_do_not_overflow(self):
        data = model(); data['criteria']['quality'].update(worst=-1e308,best=1e308,weight=1e308)
        data['criteria']['cost']['weight'] = 1e308
        self.assertTrue(all(0 <= r['total'] <= 1 for r in matrix.compute(data)['ranking']))
    def test_ev_arithmetic(self):
        result = ev.compute(scenarios())
        self.assertEqual(result['expected_value'], 10)
        self.assertEqual(result['loss_probability'], .75)
    def test_ev_invalid_probabilities_and_values(self):
        for key in ['probability','value']:
            for bad in [float('nan'), float('inf'), True, '0.25']:
                data = scenarios(); data['scenarios'][0][key] = bad
                with self.assertRaises(ValueError): ev.compute(data)
        data = scenarios(); data['scenarios'][0]['probability'] = .3
        with self.assertRaises(ValueError): ev.compute(data)
    def test_zero_probability_not_used_as_possible_extreme(self):
        data = scenarios(); data['scenarios'].append({'name':'impossible','probability':0,'value':-1000})
        self.assertEqual(ev.compute(data)['worst_positive_probability_value'], -20)
    def test_json_duplicates_constants_and_size(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'input.json'
            for text in ['{"a":1,"a":2}', '{"a":NaN}', ' '*(common.MAX_BYTES+1)]:
                path.write_text(text)
                with self.assertRaises(ValueError): common.load_input(path)
    def test_cli_failure_status_and_no_success_output(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'input.json'; path.write_text('{"unit":"GBP","scenarios":[]}')
            run = subprocess.run([sys.executable,str(Path(ev.__file__)), '--input', str(path)],capture_output=True,text=True)
            self.assertEqual(run.returncode,1); self.assertEqual(run.stdout,''); self.assertIn('error',json.loads(run.stderr))
    def test_input_model_not_mutated(self):
        data = model(); before = copy.deepcopy(data); matrix.compute(data); self.assertEqual(data,before)

if __name__ == '__main__': unittest.main()
