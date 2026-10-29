#!/usr/bin/env python3
"""Replay file hashes and assessment arithmetic offline. Does not verify truth."""
import hashlib
import json
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[2]

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    manifest = load(CASE / 'manifest.json')
    for report in manifest['reports']:
        assert hashlib.sha256((CASE / report['path']).read_bytes()).hexdigest() == report['sha256'], report['id']
    # Historical protocol only: recompute saved weighted contributions without
    # importing the retired evaluator. This does not reproduce its full gates.
    totals = {}
    for report in manifest['reports']:
        key = report['id']
        totals[key] = {}
        for profile in ('balanced', 'orientation', 'investment'):
            saved = load(CASE / 'evaluation/scores' / f'{key}.{profile}.json')
            contributions = []
            for dim in saved['dimensions']:
                assert dim['weight'] == saved['weights'][dim['id']]
                contribution = dim['weight'] * dim['rating'] / 5
                assert abs(contribution - dim['contribution']) < 1e-8
                contributions.append(contribution)
            assert sum(saved['weights'].values()) == 100
            assert abs(round(sum(contributions), 2) - saved['diagnostic_total']) < 1e-8
            totals[key][profile] = saved['headline_total']
    evidence = CASE / 'evaluation/evidence'
    registry = {n: load(evidence / (n+'.json')) for n in ('NCT05938920','NCT07687459','NCT07276724','NCT07359846')}
    combined = sum(registry[n]['protocolSection']['designModule']['enrollmentInfo']['count'] for n in ('NCT07276724','NCT07359846'))
    assert combined == 1572
    assert registry['NCT07687459']['protocolSection']['designModule']['enrollmentInfo']['count'] == 320
    checks = {
        'gb0895_combined_planned_enrollment': combined,
        'isomorphic_lilly_upfront_pct': round(45 / (45+1700) * 100, 6),
        'sdgr_2026q2_net_income_thousand_usd': -41547+45868+3026-1372,
        'xtalpi_ai4s_2026h1_growth_pct': round((193518 / 81864 - 1) * 100, 6),
        'codex_hypothetical_customer_contract_value_cny': 50*2000000,
        'codex_hypothetical_cash_runway_quarters': 120000000 / 20000000,
        'warning': 'Only arithmetic and stored-file integrity. No automated assessment of source truth, causality, readability or valuation.'
    }
    assert checks == load(evidence / 'calculation_checks.json'), 'calculation replay differs'
    print(json.dumps({'report_hashes':'PASS','retired_evaluator':'not required; historical snapshot retained','score_records':12,'scores':totals,'arithmetic':checks},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
