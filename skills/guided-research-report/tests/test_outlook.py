"""Behavioral arithmetic and refusal checks; these do not evaluate research quality."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('outlook', ROOT/'scripts/analyse_outlook.py')
OUTLOOK = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(OUTLOOK)


class OutlookTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT/'templates/outlook.synthetic.json').read_text())

    def test_bottom_up_market_and_vendor_capture(self):
        totals = OUTLOOK.analyse(self.data)['market']['totals']
        self.assertEqual(totals, {'tam': 200, 'sam': 130, 'served_market': 30, 'vendor_som': 3})

    def test_industry_adoption_is_not_automatically_company_som(self):
        for item in self.data['market']['segments']:
            del item['vendor_share']
        self.assertNotIn('vendor_som', OUTLOOK.analyse(self.data)['market']['totals'])

    def test_duplicate_budget_cannot_be_summed(self):
        segments = self.data['market']['segments']
        segments[1]['buyer_budget_key'] = segments[0]['buyer_budget_key']
        with self.assertRaisesRegex(ValueError, 'duplicate buyer_budget_key'):
            OUTLOOK.analyse(self.data)

    def test_market_rejects_mixed_units_and_partial_vendor_share(self):
        self.data['market']['segments'][0]['unit'] = 'RMB'
        with self.assertRaisesRegex(ValueError, 'unit mismatch'):
            OUTLOOK.analyse(self.data)
        del self.data['market']['segments'][0]['unit']
        del self.data['market']['segments'][0]['vendor_share']
        with self.assertRaisesRegex(ValueError, 'every segment'):
            OUTLOOK.analyse(self.data)

    def test_subjective_weighted_mean_and_transfer(self):
        scenario = OUTLOOK.analyse(self.data)['scenarios']
        self.assertEqual(scenario['probability_type'], 'analyst_subjective')
        self.assertAlmostEqual(scenario['weighted_mean'], 36.25)
        self.assertAlmostEqual(scenario['weight_sensitivity'][0]['weighted_mean'], 34.75)
        self.assertAlmostEqual(sum(scenario['weight_sensitivity'][0]['weights'].values()), 1)

    def test_subjective_weights_do_not_need_fabricated_calibration(self):
        self.assertNotIn('calibration_evidence', self.data['scenarios'])
        OUTLOOK.analyse(self.data)
        self.data['scenarios']['probability_type'] = 'empirical'
        with self.assertRaisesRegex(ValueError, 'calibration_evidence'):
            OUTLOOK.analyse(self.data)

    def test_weights_cannot_be_confidence_labels_or_unnormalized(self):
        self.data['scenarios']['scenarios'][0]['probability'] = 'high'
        with self.assertRaisesRegex(ValueError, 'expected number'):
            OUTLOOK.analyse(self.data)
        self.data['scenarios']['scenarios'][0]['probability'] = .3
        with self.assertRaisesRegex(ValueError, 'sum to 1'):
            OUTLOOK.analyse(self.data)

    def test_scenario_semantic_mismatch_is_refused(self):
        for key, value in [('unit', 'RMB'), ('horizon', '2030-12-31'), ('outcome_definition', 'share price')]:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data['scenarios']['scenarios'][0][key] = value
                with self.assertRaisesRegex(ValueError, 'mismatch'):
                    OUTLOOK.analyse(data)

    def test_empty_probability_rationale_and_partition_are_refused(self):
        for key in ['probability_basis', 'partition_definition']:
            with self.subTest(key=key):
                data = copy.deepcopy(self.data)
                data['scenarios'][key] = '  '
                with self.assertRaisesRegex(ValueError, 'required nonempty'):
                    OUTLOOK.analyse(data)

    def test_duplicate_scenarios_and_invalid_transfers_refused(self):
        self.data['scenarios']['scenarios'][1]['id'] = 'down'
        with self.assertRaisesRegex(ValueError, 'duplicate id'):
            OUTLOOK.analyse(self.data)
        self.setUp()
        self.data['scenarios']['weight_transfers'][0]['amount'] = .9
        with self.assertRaisesRegex(ValueError, 'exceeds source'):
            OUTLOOK.analyse(self.data)

    def test_cash_base_and_delay_have_different_funding_needs(self):
        cases = OUTLOOK.analyse(self.data)['cash']['cases']
        self.assertEqual(cases[0]['terminal_cash'], 5)
        self.assertIsNone(cases[0]['first_below_floor'])
        self.assertEqual(cases[0]['minimum_incremental_funding'], 0)
        self.assertEqual(cases[1]['first_below_floor'], 'Q2')
        self.assertEqual(cases[1]['terminal_cash'], -25)
        self.assertEqual(cases[1]['minimum_incremental_funding'], 30)

    def test_delayed_cash_moves_without_disappearing(self):
        cases = OUTLOOK.analyse(self.data)['cash']['cases']
        base, delayed = cases[:2]
        self.assertEqual(sum(p['milestone_receipts'] for p in base['periods']), 20)
        self.assertEqual([p['milestone_receipts'] for p in delayed['periods']], [0, 0, 20, 0])
        self.assertEqual(delayed['deferred_milestones_beyond_horizon'], 0)

    def test_beyond_horizon_cash_is_identified_and_costs_stressed(self):
        case = OUTLOOK.analyse(self.data)['cash']['cases'][2]
        self.assertEqual(case['deferred_milestones_beyond_horizon'], 20)
        self.assertEqual(case['terminal_cash'], -65)
        self.assertEqual(case['minimum_incremental_funding'], 70)

    def test_positive_terminal_cash_does_not_hide_earlier_gap(self):
        cash = self.data['cash']
        cash['opening_usable_cash'] = 10
        cash['periods'] = [
            dict(period='early', operating_receipts=0, milestone_receipts=0, financing_receipts=0, operating_payments=30, capex=0, debt_service=0),
            dict(period='later', operating_receipts=0, milestone_receipts=100, financing_receipts=0, operating_payments=0, capex=0, debt_service=0)]
        del cash['stresses']
        case = OUTLOOK.analyse(self.data)['cash']['cases'][0]
        self.assertEqual(case['terminal_cash'], 80)
        self.assertEqual(case['first_below_floor'], 'early')
        self.assertEqual(case['minimum_incremental_funding'], 25)

    def test_cash_model_does_not_mutate_input_or_reverse_accrual_revenue(self):
        before = copy.deepcopy(self.data)
        result = OUTLOOK.analyse(self.data)
        self.assertEqual(self.data, before)
        self.assertNotIn('revenue', result['cash'])

    def test_misspelled_stress_cannot_silently_become_base_case(self):
        stress = self.data['cash']['stresses'][0]
        stress['milestone_delay_period'] = stress.pop('milestone_delay_periods')
        with self.assertRaisesRegex(ValueError, 'unknown cash stress fields'):
            OUTLOOK.analyse(self.data)

    def test_invalid_cash_timing_inputs_and_reserved_id_refused(self):
        for value in [-1, .5, True]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data['cash']['stresses'][0]['milestone_delay_periods'] = value
                with self.assertRaisesRegex(ValueError, 'nonnegative integer'):
                    OUTLOOK.analyse(data)
        self.data['cash']['stresses'][0]['id'] = 'base'
        with self.assertRaisesRegex(ValueError, 'reserved'):
            OUTLOOK.analyse(self.data)

    def test_conditional_funnel_preserves_fractional_expectations(self):
        funnel = OUTLOOK.analyse(self.data)['funnel']
        self.assertAlmostEqual(funnel['cumulative_probability'], .096)
        self.assertAlmostEqual(funnel['expected_final_projects'], 9.6)
        self.assertEqual([round(s['expected_projects'], 1) for s in funnel['stages']], [60, 24, 12, 9.6])
        self.assertIn('not observed counts', funnel['limit'])

    def test_cumulative_loa_and_ongoing_ai_cohort_cannot_use_reference_product(self):
        self.data['funnel']['rate_kind'] = 'cumulative_loa'
        with self.assertRaisesRegex(ValueError, 'only conditional'):
            OUTLOOK.analyse(self.data)
        self.data['funnel']['rate_kind'] = 'conditional_transition'
        self.data['funnel']['basis'] = 'ongoing_ai_cohort'
        with self.assertRaisesRegex(ValueError, 'ongoing AI cohort'):
            OUTLOOK.analyse(self.data)

    def test_disconnected_or_looping_clinical_stages_refused(self):
        self.data['funnel']['transitions'][1]['from'] = 'unrelated cohort'
        with self.assertRaisesRegex(ValueError, 'contiguous'):
            OUTLOOK.analyse(self.data)
        self.setUp()
        self.data['funnel']['transitions'][1]['to'] = 'Phase I'
        with self.assertRaisesRegex(ValueError, 'loop'):
            OUTLOOK.analyse(self.data)

    def test_nonfinite_boolean_negative_and_invalid_probability_refused(self):
        for value in [float('nan'), float('inf'), True, -.1, 1.1]:
            with self.subTest(value=value):
                data = copy.deepcopy(self.data)
                data['scenarios']['scenarios'][0]['probability'] = value
                with self.assertRaises(ValueError):
                    OUTLOOK.analyse(data)

    def test_derived_overflow_does_not_publish_nonfinite_results(self):
        self.data['market']['segments'][0]['buyers'] = 1e308
        self.data['market']['segments'][0]['annual_spend'] = 1e308
        with self.assertRaisesRegex(ValueError, 'derived output is nonfinite'):
            OUTLOOK.analyse(self.data)

    def test_modules_are_optional_but_empty_work_is_not_success(self):
        data = {'schema_version': 1, 'scope': self.data['scope'], 'funnel': self.data['funnel']}
        self.assertIn('funnel', OUTLOOK.analyse(data))
        del data['funnel']
        with self.assertRaisesRegex(ValueError, 'at least one'):
            OUTLOOK.analyse(data)

    def test_cli_outputs_and_refuses_overwrite_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory)/'inputs.json'
            output = Path(directory)/'result.json'
            source.write_text(json.dumps(self.data))
            command = [sys.executable, str(ROOT/'scripts/analyse_outlook.py'), '--input', str(source), '--output', str(output)]
            result = subprocess.run(command, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            frozen = output.read_bytes()
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertEqual(output.read_bytes(), frozen)
            output.unlink()
            self.data['scenarios']['scenarios'][0]['probability'] = .8
            source.write_text(json.dumps(self.data))
            self.assertEqual(subprocess.run(command, capture_output=True).returncode, 2)
            self.assertFalse(output.exists())


if __name__ == '__main__':
    unittest.main()
