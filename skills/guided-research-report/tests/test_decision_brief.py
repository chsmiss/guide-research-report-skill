"""Synthetic behavioral checks of the optional join and its status boundaries."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import test_research_pack as legacy
fixture, m = legacy.fixture, legacy.m

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
spec = importlib.util.spec_from_file_location('brief', ROOT / 'scripts/build_decision_brief.py')
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)


def testrow():
    return dict(test_id='T1', judgment_id='J1', test_type='cash_stress',
                question_or_event='Delayed payment?', held_fixed='Other cash costs',
                changed_factor='Receipt date', observable_source='Future receivables note',
                review_window='Next filing', update_direction='down', affected_scope='Liquidity only',
                status='planned', result_or_remaining_gap='No executed calculation', evidence_ids='')


class BriefTests(unittest.TestCase):
    def test_pure_join_preserves_relations_and_no_grades(self):
        c,e,j,h = fixture(); before = copy.deepcopy((c,e,j,h))
        r = b.build_brief(c,e,j,h,[testrow()])
        self.assertEqual((c,e,j,h), before)
        self.assertTrue(r['structural_check_only'])
        self.assertEqual(r['rows'][0]['other_evidence'][0]['support_relation'], 'contextualizes')
        self.assertNotIn('evidence_domain', r['rows'][0]['basis_evidence'][0])
        self.assertNotIn('L1', json.dumps(r))
        self.assertEqual(r['rows'][0]['decision_tests'][0]['status'], 'planned')

    def test_profiles_are_retained_not_reclassified(self):
        c,e,j,h = fixture(); e[0].update(evidence_domain='financial', validation_design='issuer filing')
        r = b.build_brief(c,e,j,h)
        self.assertEqual(r['rows'][0]['basis_evidence'][0]['validation_design'], 'issuer filing')

    def test_markdown_escapes_table_characters(self):
        c,e,j,h = fixture(); j[0]['judgment_text'] = 'a|b\nc'
        text = b.markdown(b.build_brief(c,e,j,h))
        self.assertIn('a&#124;b<br>c', text)

    def validate(self, **edits):
        c,e,j,h = fixture(); t = testrow(); t.update(edits)
        return b.check_tests([t], j, e)

    def test_planned_test_needs_no_fabricated_observation(self):
        self.assertEqual(self.validate(), [])

    def test_observed_needs_checked_related_evidence(self):
        self.assertTrue(self.validate(status='observed'))
        self.assertEqual(self.validate(status='observed', evidence_ids='E1'), [])
        c,e,j,h = fixture(); e[0]['verification_status']='unchecked'
        t=testrow();t.update(status='observed', evidence_ids='E1')
        self.assertTrue(b.check_tests([t],j,e))

    def test_calculation_cannot_identify_causal_effect(self):
        self.assertTrue(self.validate(status='calculated_scenario', test_type='causal_identification'))
        self.assertEqual(self.validate(status='calculated_scenario', test_type='sensitivity'), [])

    def test_unrelated_or_unknown_links_rejected(self):
        self.assertTrue(self.validate(evidence_ids='E404'))
        self.assertTrue(self.validate(judgment_id='J404'))
        c,e,j,h=fixture();e[0]['claim_id']='C2';t=testrow();t['evidence_ids']='E1'
        self.assertTrue(b.check_tests([t],j,e))

    def test_missing_factors_scope_or_bad_enums_rejected(self):
        for edit in ({'held_fixed':''}, {'changed_factor':''}, {'affected_scope':''},
                     {'update_direction':'maybe'}, {'status':'done'}, {'test_type':'magic'}):
            with self.subTest(edit=edit): self.assertTrue(self.validate(**edit))

    def test_update_event_needs_source_and_window(self):
        self.assertTrue(self.validate(test_type='falsification_event', observable_source=''))
        self.assertTrue(self.validate(test_type='falsification_event', review_window=''))
        self.assertEqual(self.validate(test_type='falsification_event'), [])

    def test_duplicate_test_ids_rejected(self):
        c,e,j,h=fixture();self.assertTrue(b.check_tests([testrow(),testrow()],j,e))

    def invoke(self, directory, invalid=False):
        c,e,j,h=fixture()
        if invalid: j[0]['basis_evidence_ids']='E404'
        args=[]
        writer=legacy.CLITests()
        for name,rows,columns in [('claims',c,m.CLAIM_COLUMNS),('evidence',e,m.EVIDENCE_COLUMNS),('judgments',j,m.JUDGMENT_COLUMNS),('challenges',h,m.CHALLENGE_COLUMNS)]:
            path=writer.write(directory,name+'.csv',rows,columns);args+=['--'+name,str(path)]
        return subprocess.run([sys.executable,str(ROOT/'scripts/build_decision_brief.py'),*args,'--strict','--format','json','--output',str(directory/'brief.json')],text=True,capture_output=True)

    def test_cli_export_refuses_overwrite_and_invalid_no_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp);r=self.invoke(p,True);self.assertNotEqual(r.returncode,0);self.assertFalse((p/'brief.json').exists())
            r=self.invoke(p);self.assertEqual(r.returncode,0,r.stdout)
            before=(p/'brief.json').read_text();r=self.invoke(p)
            self.assertNotEqual(r.returncode,0);self.assertEqual((p/'brief.json').read_text(),before)


if __name__ == '__main__': unittest.main()
