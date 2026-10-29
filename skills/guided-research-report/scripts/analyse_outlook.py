#!/usr/bin/env python3
"""Replay declared outlook models. Arithmetic/structure checks are not research validation."""
import argparse
from datetime import date
import json
import math
from pathlib import Path


def require(condition, message):
    if not condition:
        raise ValueError(message)


def number(value, label, lower=None, upper=None):
    require(isinstance(value, (int, float)) and not isinstance(value, bool), f'{label}: expected number')
    require(math.isfinite(value), f'{label}: nonfinite number')
    if lower is not None:
        require(value >= lower, f'{label}: below {lower}')
    if upper is not None:
        require(value <= upper, f'{label}: above {upper}')
    return value


def words(obj, key):
    value = obj.get(key)
    require(isinstance(value, str) and bool(value.strip()), f'{key}: required nonempty text')
    return value


def rows(obj, key, minimum=1):
    value = obj.get(key)
    require(isinstance(value, list) and len(value) >= minimum, f'{key}: expected at least {minimum} rows')
    require(all(isinstance(row, dict) for row in value), f'{key}: rows must be objects')
    return value


def unique(items, key):
    ids = [words(item, key) for item in items]
    require(len(ids) == len(set(ids)), f'duplicate {key}')


def market(model):
    unit = words(model, 'unit')
    definition = words(model, 'definition')
    year = model.get('year')
    require(isinstance(year, int) and not isinstance(year, bool), 'market year must be integer')
    segments = rows(model, 'segments')
    unique(segments, 'id')
    unique(segments, 'buyer_budget_key')
    vendor_present = ['vendor_share' in segment for segment in segments]
    require(all(vendor_present) or not any(vendor_present), 'vendor_share required for every segment or none')
    result = []
    for segment in segments:
        words(segment, 'input_basis')
        words(segment, 'nonoverlap_basis')
        require(segment.get('unit', unit) == unit, 'market segment unit mismatch')
        buyers = number(segment.get('buyers'), 'buyers', 0)
        spend = number(segment.get('annual_spend'), 'annual_spend in stated unit per buyer', 0)
        eligible = number(segment.get('addressable_fraction'), 'addressable_fraction', 0, 1)
        adoption = number(segment.get('adoption'), 'adoption', 0, 1)
        tam = buyers * spend
        sam = tam * eligible
        item = {'id': segment['id'], 'tam': tam, 'sam': sam, 'served_market': sam * adoption}
        if all(vendor_present):
            item['vendor_som'] = item['served_market'] * number(segment['vendor_share'], 'vendor_share', 0, 1)
        result.append(item)
    keys = ['tam', 'sam', 'served_market'] + (['vendor_som'] if all(vendor_present) else [])
    return {'unit': unit, 'year': year, 'definition': definition, 'segments': result,
            'totals': {key: sum(item[key] for item in result) for key in keys},
            'limit': 'Conditional on declared demand/price/adoption and nonoverlap; no source-truth validation.'}


def scenarios(model, horizon):
    unit = words(model, 'unit')
    definition = words(model, 'outcome_definition')
    require(words(model, 'horizon') == horizon, 'scenario horizon differs from scope')
    basis = words(model, 'probability_type')
    require(basis in {'empirical', 'model_based', 'analyst_subjective'}, 'unknown probability_type')
    words(model, 'probability_basis')
    words(model, 'partition_definition')
    if basis != 'analyst_subjective':
        words(model, 'calibration_evidence')
    branches = rows(model, 'scenarios', 2)
    unique(branches, 'id')
    probabilities, outcomes = {}, {}
    for branch in branches:
        for key in ['state_definition', 'assumptions', 'update_trigger', 'decision_implication']:
            words(branch, key)
        require(branch.get('unit', unit) == unit, 'scenario unit mismatch')
        require(branch.get('horizon', horizon) == horizon, 'scenario branch horizon mismatch')
        require(branch.get('outcome_definition', definition) == definition, 'scenario outcome definition mismatch')
        probabilities[branch['id']] = number(branch.get('probability'), 'probability', 0, 1)
        outcomes[branch['id']] = number(branch.get('outcome'), 'outcome')
    require(math.isclose(sum(probabilities.values()), 1, rel_tol=0, abs_tol=1e-9), 'probabilities must sum to 1')
    expected = sum(probabilities[key] * outcomes[key] for key in probabilities)
    sensitivity = []
    if 'weight_transfers' in model:
        for transfer in rows(model, 'weight_transfers'):
            label = words(transfer, 'label')
            source, target = words(transfer, 'from'), words(transfer, 'to')
            require(source in probabilities and target in probabilities and source != target, 'invalid weight transfer branches')
            amount = number(transfer.get('amount'), 'transfer amount', 0, 1)
            require(amount <= probabilities[source], 'weight transfer exceeds source probability')
            weights = dict(probabilities)
            weights[source] -= amount
            weights[target] += amount
            sensitivity.append({'label': label, 'weights': weights,
                                'weighted_mean': sum(weights[key] * outcomes[key] for key in weights)})
    return {'unit': unit, 'horizon': horizon, 'outcome_definition': definition,
            'probability_type': basis, 'weights': probabilities, 'weighted_mean': expected,
            'scenario_range': [min(outcomes.values()), max(outcomes.values())], 'weight_sensitivity': sensitivity,
            'limit': 'A conditional weighted estimate, not calibrated truth, most likely outcome, or solvency evidence.'}


CASH_FIELDS = ['operating_receipts', 'milestone_receipts', 'financing_receipts',
               'operating_payments', 'capex', 'debt_service']


def cash_path(opening, floor, periods):
    balance = opening
    minimum = opening
    first_breach = 'opening' if opening < floor else None
    first_pre_financing_breach = first_breach
    output = []
    for period in periods:
        pre_financing = balance + period['operating_receipts'] + period['milestone_receipts'] - period['operating_payments'] - period['capex'] - period['debt_service']
        closing = pre_financing + period['financing_receipts']
        if first_pre_financing_breach is None and pre_financing < floor:
            first_pre_financing_breach = period['period']
        if first_breach is None and closing < floor:
            first_breach = period['period']
        minimum = min(minimum, closing)
        output.append({**period, 'opening_cash': balance, 'pre_financing_cash': pre_financing, 'closing_cash': closing})
        balance = closing
    return {'periods': output, 'terminal_cash': balance, 'minimum_period_end_or_opening_cash': minimum,
            'first_below_floor': first_breach, 'first_pre_financing_below_floor': first_pre_financing_breach,
            'minimum_incremental_funding': max(0, floor - minimum)}


def cash(model):
    unit = words(model, 'unit')
    for key in ['cash_definition', 'period_timing', 'input_basis']:
        words(model, key)
    opening = number(model.get('opening_usable_cash'), 'opening_usable_cash', 0)
    floor = number(model.get('minimum_cash'), 'minimum_cash', 0)
    periods = rows(model, 'periods')
    unique(periods, 'period')
    # List order is authoritative; labels need not be a specific quarter naming system.
    for period in periods:
        for key in CASH_FIELDS:
            number(period.get(key), key, 0)
    result = [{'id': 'base', **cash_path(opening, floor, periods), 'deferred_milestones_beyond_horizon': 0}]
    if 'stresses' in model:
        stresses = rows(model, 'stresses')
        unique(stresses, 'id')
        require(all(item['id'] != 'base' for item in stresses), 'stress id base is reserved')
        for stress in stresses:
            allowed = {'id', 'assumption_basis', 'milestone_delay_periods', 'operating_payment_multiplier', 'financing_receipt_multiplier'}
            require(not (set(stress) - allowed), 'unknown cash stress fields; check for misspelled assumptions')
            words(stress, 'assumption_basis')
            delay = stress.get('milestone_delay_periods', 0)
            require(isinstance(delay, int) and not isinstance(delay, bool) and delay >= 0, 'milestone delay must be nonnegative integer')
            costs = number(stress.get('operating_payment_multiplier', 1), 'operating_payment_multiplier', 0)
            financing = number(stress.get('financing_receipt_multiplier', 1), 'financing_receipt_multiplier', 0)
            changed = [{**period, 'milestone_receipts': 0,
                        'operating_payments': period['operating_payments'] * costs,
                        'financing_receipts': period['financing_receipts'] * financing} for period in periods]
            deferred = 0
            for index, period in enumerate(periods):
                if index + delay < len(changed):
                    changed[index + delay]['milestone_receipts'] += period['milestone_receipts']
                else:
                    deferred += period['milestone_receipts']
            result.append({'id': stress['id'], **cash_path(opening, floor, changed),
                           'deferred_milestones_beyond_horizon': deferred})
    return {'unit': unit, 'cash_floor': floor, 'cases': result,
            'limit': 'Period-end arithmetic only; intra-period timing may add gaps. Negative cash requires funding; no automatic financing, revenue reversal or liquidity inference from expected values.'}


def funnel(model):
    for key in ['source', 'population', 'observation_window', 'denominator_definition']:
        words(model, key)
    require(model.get('basis') == 'historical_reference', 'funnel supports a historical reference, not an unadjusted ongoing AI cohort')
    require(model.get('rate_kind') == 'conditional_transition', 'only conditional stage rates can be multiplied; cumulative LOA cannot')
    initial = number(model.get('initial_projects'), 'initial_projects', 0)
    transitions = rows(model, 'transitions')
    product, count = 1, initial
    result = []
    previous, visited = None, set()
    for transition in transitions:
        start, end = words(transition, 'from'), words(transition, 'to')
        require(start != end and end not in visited, 'funnel stage loop')
        if previous is not None:
            require(start == previous, 'funnel transitions must be contiguous')
        visited.add(start)
        visited.add(end)
        rate = number(transition.get('rate'), 'conditional transition rate', 0, 1)
        product *= rate
        count *= rate
        result.append({'from': start, 'to': end, 'rate': rate, 'cumulative_probability': product, 'expected_projects': count})
        previous = end
    return {'source': model['source'], 'basis': model['basis'], 'initial_projects': initial,
            'stages': result, 'cumulative_probability': product, 'expected_final_projects': count,
            'limit': 'Conditional historical-reference expectation, not observed counts, asset-specific probability or causal AI uplift. Cohort compatibility is declared, not verified.'}


def analyse(data):
    require(isinstance(data, dict) and type(data.get('schema_version')) is int and data['schema_version'] == 1, 'expected schema_version 1 object')
    scope = data.get('scope')
    require(isinstance(scope, dict), 'scope object required')
    subject = words(scope, 'subject')
    cutoff, horizon = words(scope, 'as_of'), words(scope, 'horizon')
    require(date.fromisoformat(cutoff) < date.fromisoformat(horizon), 'horizon must follow as_of')
    modules = set(data) & {'market', 'scenarios', 'cash', 'funnel'}
    require(bool(modules), 'at least one quantitative module required')
    result = {'schema_version': 1, 'subject': subject, 'as_of': cutoff, 'horizon': horizon,
              'verification_scope': 'Input declarations and arithmetic only; not factual or probabilistic validation.'}
    for key in sorted(modules):
        require(isinstance(data[key], dict), f'{key}: expected object')
        result[key] = scenarios(data[key], horizon) if key == 'scenarios' else globals()[key](data[key])
    def finite_output(value):
        if isinstance(value, (int, float)):
            require(math.isfinite(value), 'derived output is nonfinite')
        elif isinstance(value, dict):
            for child in value.values():
                finite_output(child)
        elif isinstance(value, list):
            for child in value:
                finite_output(child)
    finite_output(result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--output', type=Path, help='New file only; refuses overwrite')
    args = parser.parse_args()
    try:
        data = json.loads(args.input.read_text(encoding='utf-8'))
        result = analyse(data)
        text = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + '\n'
        if args.output:
            # Exclusive creation protects frozen inputs/results, including a same-path invocation.
            with args.output.open('x', encoding='utf-8') as output:
                output.write(text)
        else:
            print(text, end='')
    except (ValueError, TypeError, KeyError, OSError, OverflowError) as error:
        parser.exit(2, f'error: {error}\n')


if __name__ == '__main__':
    main()
