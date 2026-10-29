"""Real publication failure modes; all source fixtures are synthetic."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('publication_checks', ROOT/'scripts/publication_checks.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def sources():
    return [{'id': sid, 'title': f'Synthetic record {sid}', 'url': f'https://issuer.example/{sid}'}
            for sid in ['S01', 'S19', 'S23']]


def metric(**changes):
    row = {'id': 'residual_growth', 'kind': 'growth_pct', 'inputs': ['151.987', '264.220'],
           'shown_inputs': ['151.987', '264.220'], 'decimals': 2, 'display': '73.84%',
           'context': '残余收入增长73.84%'}
    row.update(changes)
    return row


class ReferenceTests(unittest.TestCase):
    def test_gapped_internal_ids_become_continuous_first_use_numbers(self):
        data = sources()
        before = copy.deepcopy(data)
        mapping, rendered = m.prepare_references(data, '判断[S19]，比较[S01]，再看[S19]。')
        self.assertEqual(rendered, '判断[1]，比较[2]，再看[1]。')
        self.assertEqual([r['source_id'] for r in mapping['references']], ['S19', 'S01'])
        self.assertEqual(mapping['unused_source_ids'], ['S23'])
        self.assertEqual(data, before)
        self.assertEqual(m.check_publication(rendered, mapping)['errors'], [])

    def test_source_urls_and_locators_survive_publication_mapping(self):
        data = sources()
        data[1]['locator'] = 'note 4 page 12'
        mapping, _ = m.prepare_references(data, '结果[S19]')
        row = mapping['references'][0]
        self.assertEqual(row['url'], data[1]['url'])
        self.assertEqual(row['locator'], data[1]['locator'])

    def test_unknown_source_is_rejected_instead_of_filled(self):
        with self.assertRaises(ValueError): m.prepare_references(sources(), '结果[S18]')

    def test_duplicate_source_id_is_rejected(self):
        with self.assertRaises(ValueError): m.prepare_references(sources()+[sources()[0]], '结果[S01]')

    def test_renumber_from_stable_body_after_source_removal(self):
        mapping, first = m.prepare_references(sources(), '第一[S19]，第二[S23]')
        with self.assertRaises(ValueError): m.prepare_references(sources(), first)
        revised, text = m.prepare_references(sources(), '第二[S23]')
        self.assertEqual(text, '第二[1]')
        self.assertEqual(revised['references'][0]['source_id'], 'S23')

    def test_missing_publication_number_and_stale_map_fail(self):
        mapping, _ = m.prepare_references(sources(), '第一[S01]，第二[S19]')
        self.assertTrue(m.check_publication('第一[1]，第二[3]', mapping)['errors'])
        self.assertTrue(m.check_publication('第一[1]', mapping)['errors'])
        mapping['references'][1]['number'] = 3
        self.assertTrue(m.check_publication('第一[1]，第二[3]', mapping)['errors'])

    def test_reordered_first_appearance_requires_new_mapping(self):
        mapping, _ = m.prepare_references(sources(), '第一[S01]，第二[S19]')
        self.assertTrue(m.check_publication('第二[2]，第一[1]', mapping)['errors'])

    def test_stable_tokens_left_in_final_text_fail(self):
        mapping, _ = m.prepare_references(sources(), '第一[S01]')
        self.assertTrue(m.check_publication('第一[1]，补充[S19]', mapping)['errors'])


class DisplayTests(unittest.TestCase):
    def test_full_precision_inputs_and_display_replay(self):
        errors, warnings, rows = m.check_numbers([metric()], '残余收入增长73.84%')
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(rows[0]['shown_input_result'], '73.84%')

    def test_rounded_input_growth_difference_is_found(self):
        errors, _, rows = m.check_numbers([metric(shown_inputs=['1.520', '2.642'])], '残余收入增长73.84%')
        self.assertTrue(errors)
        self.assertEqual(rows[0]['shown_input_result'], '73.82%')

    def test_rounded_input_share_difference_is_found(self):
        row = metric(kind='share_pct', inputs=['111.654', '112.233'], shown_inputs=['1.117', '1.122'],
                     display='99.48%', context='增量占比99.48%')
        errors, _, result = m.check_numbers([row], '增量占比99.48%')
        self.assertTrue(errors)
        self.assertEqual(result[0]['shown_input_result'], '99.55%')

    def test_disclosed_rounding_basis_is_preserved_as_warning(self):
        note = '百分比按未舍入金额计算。'
        row = metric(shown_inputs=['1.520', '2.642'], rounding_note=note)
        errors, warnings, _ = m.check_numbers([row], '残余收入增长73.84%。'+note)
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        errors, _, _ = m.check_numbers([row], '残余收入增长73.84%')
        self.assertTrue(errors)

    def test_rounding_note_cannot_excuse_wrong_raw_result(self):
        note = '百分比按未舍入金额计算。'
        row = metric(display='73.82%', context='残余收入增长73.82%', rounding_note=note)
        self.assertTrue(m.check_numbers([row], row['context']+note)[0])

    def test_number_must_occur_in_declared_context(self):
        self.assertTrue(m.check_numbers([metric()], '另一项收入为73.84%')[0])
        self.assertEqual(m.check_numbers([metric()], '残余收入 增长 73.84%')[0], [])

    def test_decimal_half_up_is_explicit_and_negative_zero_normalized(self):
        self.assertEqual(m.format_value('70.175', 2, True), '70.18%')
        self.assertEqual(m.format_value('-1.005', 2), '-1.01')
        self.assertEqual(m.format_value('-0.0001', 2), '0.00')

    def test_plain_number_and_negative_growth(self):
        plain = metric(id='cash', kind='number', inputs=['106.303'], display='106.303', decimals=3, context='收入106.303')
        decline = metric(id='decline', inputs=['81.003', '68.104'], shown_inputs=['81.003', '68.104'],
                         display='-15.92%', context='软件收入变化-15.92%')
        self.assertEqual(m.check_numbers([plain, decline], '收入106.303\n软件收入变化-15.92%')[0], [])

    def test_zero_denominators_nonfinite_and_duplicate_metric_ids_fail(self):
        for row in [metric(inputs=['0', '1']), metric(inputs=['NaN', '1']), metric(decimals=-1)]:
            self.assertTrue(m.check_numbers([row], '残余收入增长73.84%')[0])
        self.assertTrue(m.check_numbers([metric(), metric()], '残余收入增长73.84%')[0])

    def test_missing_reader_inputs_is_explicit(self):
        row = metric()
        del row['shown_inputs']
        self.assertTrue(m.check_numbers([row], '残余收入增长73.84%')[0])


class ScopeAndCLITests(unittest.TestCase):
    def test_production_markers_adjacent_to_chinese_text_are_visible(self):
        hints = m.editorial_hints('研究包内calculation_inputs.json区分来源，运行python3 research/recompute.py即可重算；结果记录在qa目录。')
        self.assertTrue(hints)
        self.assertIn('calculation_inputs.json', hints[0]['markers'])
        self.assertIn('qa', hints[0]['markers'])

    def test_empty_display_list_does_not_imply_numeric_coverage(self):
        result = m.check_publication('纯定性研究', {'references':[]}, [])
        self.assertTrue(result['warnings'])
        self.assertEqual(result['numeric_record_count'], 0)

    def test_technical_content_is_advisory_not_automatically_rejected(self):
        mapping, body = m.prepare_references(sources(), '研究实现需要model.py。[S01]')
        result = m.check_publication(body, mapping)
        self.assertEqual(result['mechanical_status'], 'passed')
        self.assertEqual(result['editorial_status'], 'manual_review_required')
        self.assertTrue(result['editorial_hints'])
        self.assertTrue(result['warnings'])

    def test_long_exact_repetition_is_only_a_review_lead(self):
        paragraph = '已有结果支持这项任务中的比较，需要结合成本与资源解释具体作用。' * 3
        hints = m.editorial_hints(paragraph+'\n\n'+paragraph)
        self.assertTrue(any(h['type']=='exact_repetition' for h in hints))

    def test_cli_round_trip_protects_inputs_and_existing_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root/'sources.json'
            source.write_text(json.dumps(sources()), encoding='utf-8')
            body = root/'body.txt'
            body.write_text('残余收入增长73.84%[S19]。', encoding='utf-8')
            before = (source.read_bytes(), body.read_bytes())
            base = [sys.executable, str(ROOT/'scripts/publication_checks.py')]
            args = ['prepare-references', '--sources', str(source), '--body', str(body), '--output-dir', str(root/'publication')]
            self.assertEqual(subprocess.run(base+args, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(base+args, capture_output=True).returncode, 2)
            numbers = root/'numbers.json'
            numbers.write_text(json.dumps({'values':[metric()]}), encoding='utf-8')
            check = ['check', '--body', str(root/'publication/numbered_body.txt'), '--references', str(root/'publication/citation_map.json'),
                     '--numbers', str(numbers), '--output', str(root/'result.json')]
            self.assertEqual(subprocess.run(base+check, capture_output=True).returncode, 0)
            self.assertEqual(subprocess.run(base+check, capture_output=True).returncode, 2)
            self.assertEqual(before, (source.read_bytes(), body.read_bytes()))
            result = json.loads((root/'result.json').read_text())
            self.assertEqual(result['editorial_status'], 'manual_review_required')

    def test_cli_reports_bad_values_with_failure_exit_status(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mapping, body = m.prepare_references(sources(), '残余收入增长73.84%[S01]')
            (root/'body.txt').write_text(body, encoding='utf-8')
            (root/'map.json').write_text(json.dumps(mapping), encoding='utf-8')
            (root/'numbers.json').write_text(json.dumps({'values':[metric(shown_inputs=['1.520','2.642'])]}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/publication_checks.py'), 'check',
                '--body', str(root/'body.txt'), '--references', str(root/'map.json'), '--numbers', str(root/'numbers.json'),
                '--output', str(root/'result.json')], capture_output=True)
            self.assertEqual(result.returncode, 1)
            self.assertTrue(json.loads((root/'result.json').read_text())['errors'])


if __name__ == '__main__':
    unittest.main()
