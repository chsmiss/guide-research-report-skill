#!/usr/bin/env python3
"""Replay file hashes and assessment arithmetic offline. Does not verify truth."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

CASE = Path(__file__).resolve().parents[1]
ROOT = CASE.parents[2]
SKILL = ROOT / 'skills/research-report-evaluator'

def load(path):
    return json.loads(path.read_text(encoding='utf-8'))

def main():
    manifest = load(CASE / 'manifest.json')
    for report in manifest['reports']:
        assert hashlib.sha256((CASE / report['path']).read_bytes()).hexdigest() == report['sha256'], report['id']
    for entry in load(CASE / 'evaluation/skill_snapshot.json')['files']:
        assert hashlib.sha256((ROOT / entry['path']).read_bytes()).hexdigest() == entry['sha256'], entry['path']
    spec = importlib.util.spec_from_file_location('scorer', SKILL / 'scripts/score_report.py')
    scorer = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(scorer)
    cfg = scorer.load_config()
    totals = {}
    for report in manifest['reports']:
        key = report['id']
        record = load(CASE / 'evaluation/records' / (key+'.json'))
        totals[key] = {}
        for profile in ('balanced', 'orientation', 'investment'):
            adapted = copy.deepcopy(record)
            adapted['profile'] = profile
            calculated = scorer.score(adapted, cfg)
            saved = load(CASE / 'evaluation/scores' / f'{key}.{profile}.json')
            if profile != 'balanced':
                calculated['sensitivity_only'] = True
            assert calculated == saved, (key, profile, 'saved score differs')
            totals[key][profile] = calculated['headline_total']
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
    print(json.dumps({'report_hashes':'PASS','skill_hashes':'PASS','score_records':12,'scores':totals,'arithmetic':checks},ensure_ascii=False,indent=2))

if __name__ == '__main__':
    main()
