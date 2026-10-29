"""Behavioral invariants for ledger validation; fixtures are synthetic, not research evidence."""
import copy
import csv
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('research_pack',ROOT/'scripts/check_research_pack.py')
m=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(m)

def fixture():
 c={k:'' for k in m.CLAIM_COLUMNS};c.update(claim_id='C1',tier='Tier1',claim_type='interpretation',claim_text='The observed business remains project-linked; recurring demand is unresolved.',entity='Synthetic vendor',observation_period='2025H1',as_of_date='2026-01-01',unit='USD',denominator='reported total',decision_implication='Compare project economics before long platform commitment.',verification_status='single_source',confidence='moderate',limitations='No customer-level independent revenue dataset.')
 e={k:'' for k in m.EVIDENCE_COLUMNS};e.update(evidence_id='E1',claim_id='C1',source_title='Synthetic issuer filing',source_url='https://issuer.example/filing',origin_actor='Synthetic issuer',source_type='original_record',publication_date='2025-08-01',observation_period='2025H1',evidence_chain_id='issuer_H1',independently_generated='no',support_relation='supports',verification_status='checked',exact_location='note 4',limitations='Interested issuer disclosure.')
 e2=copy.deepcopy(e);e2.update(evidence_id='E2',source_title='Synthetic renewal note',source_url='https://issuer.example/renewals',support_relation='contextualizes',exact_location='renewal note')
 j={k:'' for k in m.JUDGMENT_COLUMNS};j.update(judgment_id='J1',claim_ids='C1',judgment_type='interpretation',judgment_text='Use project-linked economics as the current comparison basis.',basis_evidence_ids='E1',strongest_alternative='Contract timing may obscure recurring adoption.',decision_implication='Verify renewals before applying a recurring software multiple.',update_trigger='Customer-side renewal and cost records establish repeated positive delivery economics.',confidence='moderate',limitations='No causal claim or market forecast.')
 h={k:'' for k in m.CHALLENGE_COLUMNS};h.update(challenge_id='H1',claim_id='C1',challenge_type='adverse_observation',challenge_text='Some observed renewals do not persist beyond pilots.',evidence_ids='E2',disposition='retained_with_limits',effect_on_judgment='Do not equate initial revenue with durable adoption.',independence_check='Same issuer chain; no independent measurement.',remaining_gap='Customer-side longitudinal renewals unavailable.')
 return [c],[e,e2],[j],[h]

class LedgerTests(unittest.TestCase):
 def run_check(self,change=None,strict=True):
  c,e,j,h=fixture()
  if change:change(c,e,j,h)
  return m.check(c,e,j,h,strict)
 def assertRejected(self,change):
  errors,_=self.run_check(change);self.assertTrue(errors)
 def test_strict_qualitative_judgment_needs_no_numeric_forecast(self):
  errors,warnings=self.run_check();self.assertEqual(errors,[]);self.assertEqual(warnings,[])
 def test_legacy_two_table_api_remains_usable(self):
  c,e,_,_=fixture();errors,warnings=m.check(c,e);self.assertEqual(errors,[]);self.assertTrue(warnings)
 def test_checked_contradiction_alone_cannot_verify_fact(self):
  c,e,_,_=fixture();c[0]['verification_status']='verified_original'
  for row in e:row['support_relation']='contradicts'
  errors,_=m.check(c,e);self.assertTrue(errors)
 def test_missing_tier1_challenge_rejected(self):
  self.assertRejected(lambda c,e,j,h:h.clear())
 def test_missing_tier1_author_judgment_rejected(self):
  self.assertRejected(lambda c,e,j,h:j.clear())
 def test_factual_tier1_does_not_force_an_author_forecast(self):
  def edit(c,e,j,h):c[0]['claim_type']='calculation';j.clear()
  errors,_=self.run_check(edit);self.assertEqual(errors,[])
 def test_adverse_context_is_not_forced_to_be_contradiction(self):
  c,e,j,h=fixture();before=copy.deepcopy(e);errors,_=m.check(c,e,j,h,True)
  self.assertEqual(errors,[]);self.assertEqual(e,before);self.assertEqual(e[1]['support_relation'],'contextualizes')
 def test_bounded_unsuccessful_search_accepted_without_fake_evidence(self):
  def edit(c,e,j,h):h[0].update(challenge_type='search_no_result',evidence_ids='',search_scope='External trial database and counterparty reports searched for this specific claim.',search_date='2026-01-01')
  errors,_=self.run_check(edit);self.assertEqual(errors,[])
 def test_unbounded_search_no_result_rejected(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(challenge_type='search_no_result',evidence_ids='',search_date='2026-01-01'))
 def test_search_no_result_needs_date(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(challenge_type='search_no_result',evidence_ids='',search_scope='Named registry queried.'))
 def test_search_no_result_cannot_claim_found_evidence(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(challenge_type='search_no_result',search_scope='Named registry queried.',search_date='2026-01-01'))
 def test_alternative_mechanism_without_empirical_counterexample_accepted(self):
  errors,_=self.run_check(lambda c,e,j,h:h[0].update(challenge_type='alternative_mechanism',evidence_ids=''))
  self.assertEqual(errors,[])
 def test_missing_test_needs_explicit_remaining_gap(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(challenge_type='missing_test',evidence_ids='',remaining_gap=''))
 def test_adverse_observation_cannot_use_unchecked_evidence(self):
  self.assertRejected(lambda c,e,j,h:e[1].update(verification_status='unchecked'))
 def test_challenge_cannot_cite_unknown_evidence(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(evidence_ids='E404'))
 def test_challenge_cannot_borrow_evidence_linked_to_other_claim(self):
  def edit(c,e,j,h):
   c2=copy.deepcopy(c[0]);c2.update(claim_id='C2',tier='Tier2');c.append(c2);e[1]['claim_id']='C2'
  self.assertRejected(edit)
 def test_judgment_cannot_cite_unknown_claim(self):
  self.assertRejected(lambda c,e,j,h:j[0].update(claim_ids='C404'))
 def test_judgment_cannot_cite_unknown_evidence(self):
  self.assertRejected(lambda c,e,j,h:j[0].update(basis_evidence_ids='E404'))
 def test_judgment_cannot_borrow_unrelated_evidence(self):
  def edit(c,e,j,h):
   c2=copy.deepcopy(c[0]);c2.update(claim_id='C2',tier='Tier2');c.append(c2)
   e3=copy.deepcopy(e[0]);e3.update(evidence_id='E3',claim_id='C2');e.append(e3);j[0]['basis_evidence_ids']='E3'
  self.assertRejected(edit)
 def test_no_update_trigger_rejected(self):
  self.assertRejected(lambda c,e,j,h:j[0].update(update_trigger=''))
 def test_grouped_judgment_cannot_cover_an_untraced_claim(self):
  def edit(c,e,j,h):
   c2=copy.deepcopy(c[0]);c2.update(claim_id='C2',tier='Tier2');c.append(c2);j[0]['claim_ids']='C1;C2'
  self.assertRejected(edit)
 def test_forecast_without_horizon_rejected(self):
  self.assertRejected(lambda c,e,j,h:j[0].update(judgment_type='conditional_forecast'))
 def test_conditional_forecast_with_horizon_is_not_forced_to_have_probability(self):
  errors,_=self.run_check(lambda c,e,j,h:j[0].update(judgment_type='conditional_forecast',horizon='Next disclosed fiscal year'))
  self.assertEqual(errors,[])
 def test_declaration_of_independence_without_basis_rejected_in_strict_mode(self):
  self.assertRejected(lambda c,e,j,h:e[0].update(independently_generated='yes'))
 def test_independence_metadata_is_only_a_declaration(self):
  errors,_=self.run_check(lambda c,e,j,h:e[0].update(independently_generated='yes',observation_path='Named customer independently recorded purchases.',independence_basis='Customer accounting record distinct from issuer forecast.'))
  self.assertEqual(errors,[])
 def test_same_chain_multiple_urls_not_corroboration(self):
  def edit(c,e,j,h):
   c[0]['verification_status']='corroborated'
   e[1].update(support_relation='supports',independently_generated='yes',observation_path='Reproduced report.',independence_basis='Still shares original dataset.')
  self.assertRejected(edit)
 def test_duplicate_challenge_ids_rejected(self):
  self.assertRejected(lambda c,e,j,h:h.append(copy.deepcopy(h[0])))
 def test_duplicate_judgment_ids_rejected(self):
  self.assertRejected(lambda c,e,j,h:j.append(copy.deepcopy(j[0])))
 def test_challenge_effect_must_be_recorded(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(effect_on_judgment=''))
 def test_invalid_search_date_rejected(self):
  self.assertRejected(lambda c,e,j,h:h[0].update(search_date='2026-02-30'))
 def test_strict_empty_pack_rejected(self):
  errors,_=m.check([],[],[],[],True);self.assertTrue(errors)
 def test_review_summary_preserves_ids_relations_and_limits(self):
  c,e,j,h=fixture();r=m.review_summary(c,e,j,h)
  self.assertTrue(r['structural_check_only']);self.assertEqual(r['substantive_verification'],'not_established_by_this_script')
  row=r['rows'][0];self.assertEqual(row['judgments'][0]['judgment_id'],'J1');self.assertEqual(row['challenges'][0]['challenge_id'],'H1')
  self.assertEqual(row['challenges'][0]['evidence_relations'][0]['support_relation'],'contextualizes')

class CLITests(unittest.TestCase):
 def write(self,directory,name,rows,columns):
  p=directory/name
  with p.open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=sorted(columns));w.writeheader();w.writerows(rows)
  return p
 def invoke(self,directory,change=None):
  c,e,j,h=fixture()
  if change:change(c,e,j,h)
  cp=self.write(directory,'claims.csv',c,m.CLAIM_COLUMNS);ep=self.write(directory,'evidence.csv',e,m.EVIDENCE_COLUMNS)
  jp=self.write(directory,'judgments.csv',j,m.JUDGMENT_COLUMNS);hp=self.write(directory,'challenges.csv',h,m.CHALLENGE_COLUMNS)
  return subprocess.run([sys.executable,str(ROOT/'scripts/check_research_pack.py'),'--claims',str(cp),'--evidence',str(ep),'--judgments',str(jp),'--challenges',str(hp),'--strict','--review-output',str(directory/'review.json')],capture_output=True,text=True)
 def test_cli_exports_validated_summary(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);result=self.invoke(p);self.assertEqual(result.returncode,0,result.stdout)
   self.assertTrue(json.loads((p/'review.json').read_text())['structural_check_only'])
 def test_invalid_pack_publishes_no_review_summary(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);result=self.invoke(p,lambda c,e,j,h:h.clear());self.assertNotEqual(result.returncode,0);self.assertFalse((p/'review.json').exists())
 def test_existing_output_is_not_overwritten(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);(p/'review.json').write_text('existing review');result=self.invoke(p)
   self.assertNotEqual(result.returncode,0);self.assertEqual((p/'review.json').read_text(),'existing review')
 def test_missing_csv_headers_are_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'bad.csv';p.write_text('claim_id\nC1\n');_,errors=m.read_rows(p,m.CLAIM_COLUMNS);self.assertTrue(errors)

if __name__=='__main__':unittest.main()
