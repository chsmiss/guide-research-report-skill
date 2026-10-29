#!/usr/bin/env python3
"""Join research records into an editorial review scaffold; never verify their substance."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from check_research_pack import (CLAIM_COLUMNS, EVIDENCE_COLUMNS, JUDGMENT_COLUMNS,
                                 CHALLENGE_COLUMNS, check, ids, read_rows)

TEST_COLUMNS = set('test_id,judgment_id,test_type,question_or_event,held_fixed,changed_factor,observable_source,review_window,update_direction,affected_scope,status,result_or_remaining_gap,evidence_ids'.split(','))
TEST_TYPES = {'causal_identification', 'sensitivity', 'cash_stress', 'falsification_event', 'scenario'}
STATUSES = {'planned', 'observed', 'calculated_scenario', 'unavailable'}
DIRECTIONS = {'up', 'down', 'both', 'confidence_only', 'no_change'}


def check_tests(tests, judgments, evidence):
    errors, seen = [], set()
    jm = {r['judgment_id']: r for r in judgments}
    em = {r['evidence_id']: r for r in evidence}
    for i, t in enumerate(tests, 2):
        loc = f'decision_tests.csv:{i}'
        key = t.get('test_id', '')
        if not key or key in seen:
            errors.append(f'{loc}: blank or repeated test_id')
        seen.add(key)
        j = jm.get(t.get('judgment_id'))
        if j is None:
            errors.append(f'{loc}: unknown judgment_id')
        kind, status = t.get('test_type'), t.get('status')
        if kind not in TEST_TYPES:
            errors.append(f'{loc}: invalid test_type')
        if status not in STATUSES:
            errors.append(f'{loc}: invalid status')
        if t.get('update_direction') not in DIRECTIONS:
            errors.append(f'{loc}: invalid update_direction')
        required = ['question_or_event', 'affected_scope', 'result_or_remaining_gap']
        if kind in TEST_TYPES - {'falsification_event'}:
            required += ['held_fixed', 'changed_factor']
        if kind == 'falsification_event':
            required += ['observable_source', 'review_window']
        for field in required:
            if not t.get(field):
                errors.append(f'{loc}: missing {field}')
        if status == 'calculated_scenario' and kind not in {'sensitivity', 'cash_stress', 'scenario'}:
            errors.append(f'{loc}: calculation cannot establish causal identification or an observed event')
        linked = ids(t.get('evidence_ids', ''))
        if status == 'observed' and not linked:
            errors.append(f'{loc}: observed row needs checked evidence')
        for eid in linked:
            e = em.get(eid)
            if e is None:
                errors.append(f'{loc}: unknown evidence_id {eid}')
            elif j is not None and e['claim_id'] not in ids(j['claim_ids']):
                errors.append(f'{loc}: evidence {eid} unrelated to affected claims')
            elif status == 'observed' and e.get('verification_status') != 'checked':
                errors.append(f'{loc}: observed row cites unchecked evidence {eid}')
    return errors


def build_brief(claims, evidence, judgments, challenges, tests=()):
    """Pure join preserving all supplied metadata and statuses, without adding grades."""
    cm = {r['claim_id']: r for r in claims}
    em = {r['evidence_id']: r for r in evidence}
    rows = []
    for j in judgments:
        cids = ids(j['claim_ids'])
        rows.append({
            'judgment': dict(j),
            'claims': [dict(cm[cid]) for cid in cids],
            'basis_evidence': [dict(em[eid]) for eid in ids(j['basis_evidence_ids'])],
            'other_evidence': [dict(e) for e in evidence if e['claim_id'] in cids
                               and e['evidence_id'] not in ids(j['basis_evidence_ids'])],
            'challenges_and_gaps': [dict(h) for h in challenges if h['claim_id'] in cids],
            'decision_tests': [dict(t) for t in tests if t['judgment_id'] == j['judgment_id']],
        })
    return {'structural_check_only': True,
            'substantive_verification': 'not_established_by_this_script', 'rows': rows}


def cell(value):
    return str(value).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('|', '&#124;').replace('\r', '').replace('\n', '<br>')


def markdown(brief):
    lines = ['# Judgment — evidence — gap', '',
             'Editorial input only: synthesize a reader-facing argument before publication.', '',
             'Structural join only. Source truth, independence and inference are not established by this script.', '',
             '| Judgment | Evidence and scope | Decisive recorded gap |', '|---|---|---|']
    for row in brief['rows']:
        j = row['judgment']
        ev = []
        for e in row['basis_evidence']:
            profile = '; '.join(f'{k}: {e[k]}' for k in ('evidence_domain', 'validation_design', 'evidence_scope') if e.get(k))
            ev.append(f"{e['evidence_id']}: {e['source_title']} ({e['support_relation']}; {e['verification_status']}); {e.get('exact_location', '')}; {profile}; limit: {e.get('limitations', '')}")
        gaps = [h.get('remaining_gap', '') or h.get('challenge_text', '') for h in row['challenges_and_gaps']]
        lines.append('| ' + ' | '.join(cell(v) for v in (j['judgment_text'], '\n'.join(ev), '\n'.join(gaps))) + ' |')
    for row in brief['rows']:
        j = row['judgment']
        lines += ['', f"## {cell(j['judgment_id'])}", '',
                  f"Alternative: {cell(j['strongest_alternative'])}", '',
                  f"Decision: {cell(j['decision_implication'])}", '',
                  f"Update trigger: {cell(j['update_trigger'])}", '',
                  f"Confidence: {cell(j['confidence'])}; limits: {cell(j.get('limitations', ''))}"]
        for h in row['challenges_and_gaps']:
            lines += ['', f"Challenge {cell(h['challenge_id'])} [{cell(h['challenge_type'])}]: {cell(h['challenge_text'])}; effect: {cell(h['effect_on_judgment'])}"]
        for e in row['other_evidence']:
            lines += ['', f"Other evidence {cell(e['evidence_id'])} [{cell(e['support_relation'])}; {cell(e['verification_status'])}]: {cell(e['source_title'])}; {cell(e.get('exact_location', ''))}; limits: {cell(e.get('limitations', ''))}"]
        for t in row['decision_tests']:
            lines += ['', f"Test {cell(t['test_id'])} [{cell(t['test_type'])}; status={cell(t['status'])}]: {cell(t['question_or_event'])}; direction={cell(t['update_direction'])}; scope={cell(t['affected_scope'])}; result/gap: {cell(t['result_or_remaining_gap'])}",
                      f"Fixed: {cell(t.get('held_fixed', ''))}; changed: {cell(t.get('changed_factor', ''))}; source: {cell(t.get('observable_source', ''))}; window: {cell(t.get('review_window', ''))}; evidence: {cell(t.get('evidence_ids', ''))}"]
    return '\n'.join(lines) + '\n'


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for name in ('claims', 'evidence', 'judgments', 'challenges'):
        p.add_argument('--' + name, required=True, type=Path)
    p.add_argument('--decision-tests', type=Path)
    p.add_argument('--strict', action='store_true')
    p.add_argument('--format', choices=('markdown', 'json'), default='markdown')
    p.add_argument('--output', required=True, type=Path)
    a = p.parse_args()
    packs, errors = [], []
    for name, columns in (('claims', CLAIM_COLUMNS), ('evidence', EVIDENCE_COLUMNS),
                          ('judgments', JUDGMENT_COLUMNS), ('challenges', CHALLENGE_COLUMNS)):
        rows, err = read_rows(getattr(a, name), columns)
        packs.append(rows); errors.extend(err)
    tests = []
    if a.decision_tests:
        tests, err = read_rows(a.decision_tests, TEST_COLUMNS); errors.extend(err)
    if not errors:
        err, warnings = check(*packs, strict=a.strict)
        errors.extend(err)
        errors.extend(check_tests(tests, packs[2], packs[1]))
    else:
        warnings = []
    if errors:
        print(json.dumps({'errors': errors, 'warnings': warnings}, ensure_ascii=False, indent=2))
        return 1
    brief = build_brief(*packs, tests)
    result = json.dumps(brief, ensure_ascii=False, indent=2) + '\n' if a.format == 'json' else markdown(brief)
    try:
        with a.output.open('x', encoding='utf-8') as stream:
            stream.write(result)
    except OSError as exc:
        print(f'Cannot create output: {exc}')
        return 1
    print(json.dumps({'output': str(a.output), 'warnings': warnings, 'structural_check_only': True}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
